from pydantic import BaseModel, ConfigDict


class QuestionOptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    letter: str
    position: int
    text: str
    explanation: str
    images: list[str] = []


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    year: int
    area: str
    number: int
    context: str
    statement: str
    explanation: str
    options: list[QuestionOptionOut] = []
    images: list[str] = []

    @classmethod
    def from_model(cls, question) -> "QuestionOut":
        return cls(
            id=question.id,
            external_id=question.external_id,
            year=question.year,
            area=question.area,
            number=question.number,
            context=question.context,
            statement=question.statement,
            explanation=question.explanation,
            options=[
                QuestionOptionOut(
                    id=option.id,
                    letter=option.letter,
                    position=option.position,
                    text=option.text,
                    explanation=option.explanation,
                    images=[f"/static/images/{img.path}" for img in option.images],
                )
                for option in question.options
            ],
            images=[f"/static/images/{img.path}" for img in question.images],
        )


class QuestionPage(BaseModel):
    items: list[QuestionOut]
    total: int
    page: int
    page_size: int


class FilterOptions(BaseModel):
    areas: list[str]
    years: list[int]
