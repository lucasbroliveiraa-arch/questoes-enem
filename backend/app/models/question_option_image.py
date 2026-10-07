from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QuestionOptionImage(Base):
    """Imagem associada a uma alternativa; preparada para múltiplas imagens."""

    __tablename__ = "question_option_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    option_id: Mapped[int] = mapped_column(
        ForeignKey("question_options.id", ondelete="CASCADE"), nullable=False, index=True
    )
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    option: Mapped["QuestionOption"] = relationship(back_populates="images")
