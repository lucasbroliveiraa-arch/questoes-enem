from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Question(Base):
    """Questão do ENEM; alternativas são entidades filhas."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    area: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)

    context: Mapped[str] = mapped_column(Text, default="", nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, default="", nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)

    options: Mapped[list["QuestionOption"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOption.position",
    )
    images: Mapped[list["QuestionImage"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionImage.position",
    )
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )
