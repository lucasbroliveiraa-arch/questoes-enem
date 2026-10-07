from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.schemas.question import FilterOptions, QuestionOut, QuestionPage

router = APIRouter(prefix="/api/questions", tags=["questions"])


def load_query(db: Session):
    return db.query(Question).options(
        selectinload(Question.options).selectinload(QuestionOption.images),
        selectinload(Question.images),
    )


@router.get("", response_model=QuestionPage)
def list_questions(
    area: list[str] | None = Query(None),
    year: list[int] | None = Query(None),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = load_query(db)
    if area:
        query = query.filter(Question.area.in_(area))
    if year:
        query = query.filter(Question.year.in_(year))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Question.statement.ilike(like), Question.context.ilike(like)))

    total = query.count()
    items = (
        query.order_by(Question.year, Question.area, Question.number, Question.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return QuestionPage(
        items=[QuestionOut.from_model(question) for question in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/filters", response_model=FilterOptions)
def get_filter_options(db: Session = Depends(get_db)):
    areas = [row[0] for row in db.query(Question.area).distinct().order_by(Question.area).all()]
    years = [row[0] for row in db.query(Question.year).distinct().order_by(Question.year).all()]
    return FilterOptions(areas=areas, years=years)


@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = (
        load_query(db)
        .filter(Question.id == question_id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Questão não encontrada")
    return QuestionOut.from_model(question)
