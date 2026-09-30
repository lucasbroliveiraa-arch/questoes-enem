from pydantic import BaseModel, Field


class AnswerIn(BaseModel):
    question_id: int
    selected_option: str = Field(min_length=1, max_length=1, pattern="^[A-E]$")


class AnswerOut(BaseModel):
    is_correct: bool
    correct_answer: str


class AreaStats(BaseModel):
    area: str
    answered: int
    correct: int
    accuracy: float


class StatsOut(BaseModel):
    total_answered: int
    total_correct: int
    accuracy: float
    by_area: list[AreaStats]
