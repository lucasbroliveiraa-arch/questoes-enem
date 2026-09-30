from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Question(Base):
    """
    Uma questão do ENEM. Uma linha por questão; alternativas ficam em colunas
    fixas (A-E) porque o ENEM sempre tem exatamente 5 alternativas — não vale
    a pena normalizar isso em outra tabela.
    """

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    area: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)

    context: Mapped[str] = mapped_column(Text, default="")
    statement: Mapped[str] = mapped_column(Text, nullable=False)

    option_a: Mapped[str] = mapped_column(Text, default="")
    option_b: Mapped[str] = mapped_column(Text, default="")
    option_c: Mapped[str] = mapped_column(Text, default="")
    option_d: Mapped[str] = mapped_column(Text, default="")
    option_e: Mapped[str] = mapped_column(Text, default="")

    correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)

    images: Mapped[list["QuestionImage"]] = relationship(
        back_populates="question", cascade="all, delete-orphan", order_by="QuestionImage.position"
    )
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )

    def options(self) -> list[str]:
        return [self.option_a, self.option_b, self.option_c, self.option_d, self.option_e]
