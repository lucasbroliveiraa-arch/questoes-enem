from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.question import Question
from app.schemas.question import FilterOptions, QuestionOut, QuestionPage

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("", response_model=QuestionPage)
def list_questions(
    area: list[str] | None = Query(None, description="Filtra por área (repetível: ?area=X&area=Y)"),
    year: list[int] | None = Query(None, description="Filtra por ano (repetível: ?year=2022&year=2023)"),
    q: str | None = Query(None, description="Busca por palavra-chave no enunciado/contexto"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Lista questões com filtro e paginação. `area` e `year` aceitam múltiplos
    valores (checkbox-style, como os chips do frontend). O frontend usa
    page_size=1 para navegar questão a questão (anterior/próxima), mas o
    endpoint é genérico — outros clientes podem pedir páginas maiores.
    """
    query = db.query(Question)

    if area:
        query = query.filter(Question.area.in_(area))
    if year:
        query = query.filter(Question.year.in_(year))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Question.statement.ilike(like), Question.context.ilike(like)))

    total = query.count()
    query = query.order_by(Question.year, Question.area, Question.number)
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    out_items = [
        QuestionOut.from_model(question, image_urls=[f"/static/images/{img.path}" for img in question.images])
        for question in items
    ]

    return QuestionPage(items=out_items, total=total, page=page, page_size=page_size)


@router.get("/filters", response_model=FilterOptions)
def get_filter_options(db: Session = Depends(get_db)):
    """Áreas e anos existentes no banco, para popular os filtros do frontend."""
    areas = [row[0] for row in db.query(Question.area).distinct().order_by(Question.area).all()]
    years = [row[0] for row in db.query(Question.year).distinct().order_by(Question.year).all()]
    return FilterOptions(areas=areas, years=years)


@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Questão não encontrada")
    image_urls = [f"/static/images/{img.path}" for img in question.images]
    return QuestionOut.from_model(question, image_urls=image_urls)
