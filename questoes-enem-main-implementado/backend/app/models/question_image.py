from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QuestionImage(Base):
    """
    Uma imagem associada a uma questão (algumas questões têm mais de uma,
    ex. gráfico + tabela). O arquivo em si fica em app/static/images/, aqui
    guardamos só o caminho relativo servido pela API.
    """

    __tablename__ = "question_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0)

    question: Mapped["Question"] = relationship(back_populates="images")
