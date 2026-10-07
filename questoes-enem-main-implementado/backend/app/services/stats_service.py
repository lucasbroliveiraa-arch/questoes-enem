from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.question import Question
from app.schemas.answer import AreaStats, StatsOut


def _accuracy(correct: int, total: int) -> float:
    return round(correct / total, 4) if total else 0.0


def compute_stats(db: Session) -> StatsOut:
    total_answered = db.query(func.count(Answer.id)).scalar() or 0
    total_correct = db.query(func.count(Answer.id)).filter(Answer.is_correct.is_(True)).scalar() or 0

    by_area_rows = (
        db.query(
            Question.area,
            func.count(Answer.id).label("answered"),
            func.sum(case((Answer.is_correct.is_(True), 1), else_=0)).label("correct"),
        )
        .join(Answer, Answer.question_id == Question.id)
        .group_by(Question.area)
        .order_by(Question.area)
        .all()
    )

    by_area = [
        AreaStats(
            area=row.area,
            answered=row.answered,
            correct=row.correct or 0,
            accuracy=_accuracy(row.correct or 0, row.answered),
        )
        for row in by_area_rows
    ]

    return StatsOut(
        total_answered=total_answered,
        total_correct=total_correct,
        accuracy=_accuracy(total_correct, total_answered),
        by_area=by_area,
    )
