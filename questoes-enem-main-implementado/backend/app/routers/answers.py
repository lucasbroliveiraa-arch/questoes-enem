from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.answer import Answer
from app.models.question import Question
from app.schemas.answer import AnswerIn, AnswerOut

router = APIRouter(prefix="/api/answers", tags=["answers"])


@router.post("", response_model=AnswerOut)
def submit_answer(payload: AnswerIn, db: Session = Depends(get_db)):
    """
    Recebe a alternativa escolhida, corrige no servidor (o gabarito nunca é
    enviado ao frontend antes disso) e persiste a resposta para as
    estatísticas.
    """
    question = db.get(Question, payload.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    is_correct = payload.selected_option == question.correct_answer

    answer = Answer(
        question_id=question.id,
        selected_option=payload.selected_option,
        is_correct=is_correct,
    )
    db.add(answer)
    db.commit()

    return AnswerOut(is_correct=is_correct, correct_answer=question.correct_answer)
