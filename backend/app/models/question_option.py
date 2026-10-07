from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QuestionOption(Base):
    """Alternativa da questão; no ENEM v1 existem A-E."""

    __tablename__ = "question_options"
    __table_args__ = (
        UniqueConstraint("question_id", "letter", name="uq_question_options_question_letter"),
        UniqueConstraint("question_id", "position", name="uq_question_options_question_position"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    letter: Mapped[str] = mapped_column(String(1), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    explanation: Mapped[str] = mapped_column(Text, default="", nullable=False)

    question: Mapped["Question"] = relationship(back_populates="options")
    images: Mapped[list["QuestionOptionImage"]] = relationship(
        back_populates="option",
        cascade="all, delete-orphan",
        order_by="QuestionOptionImage.position",
    )
