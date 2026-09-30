from pydantic import BaseModel, ConfigDict


class QuestionOut(BaseModel):
    """
    Representação pública de uma questão. Note que `correct_answer` NÃO entra
    aqui de propósito — o gabarito só é revelado pela resposta do endpoint
    POST /api/answers, depois que o usuário já respondeu.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    year: int
    area: str
    number: int
    context: str
    statement: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    option_e: str
    images: list[str] = []

    @classmethod
    def from_model(cls, question, image_urls: list[str]) -> "QuestionOut":
        return cls(
            id=question.id,
            year=question.year,
            area=question.area,
            number=question.number,
            context=question.context,
            statement=question.statement,
            option_a=question.option_a,
            option_b=question.option_b,
            option_c=question.option_c,
            option_d=question.option_d,
            option_e=question.option_e,
            images=image_urls,
        )


class QuestionPage(BaseModel):
    items: list[QuestionOut]
    total: int
    page: int
    page_size: int


class FilterOptions(BaseModel):
    areas: list[str]
    years: list[int]
