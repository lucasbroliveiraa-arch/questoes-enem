import argparse
import io
import os
import sys
from pathlib import Path

from PIL import Image
from sqlalchemy.orm import Session

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import settings  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models.answer import Answer
from app.models.question import Question  # noqa: E402
from app.models.question_image import QuestionImage  # noqa: E402
from app.models.question_option import QuestionOption  # noqa: E402
from app.services.question_identity import generate_external_id  # noqa: E402
from pipeline.consolidate import consolidate  # noqa: E402

MAX_DIM = 900
QUALITY = 80


def compress_image(src_path: str, dest_path: str) -> bool:
    try:
        im = Image.open(src_path).convert("RGB")
    except Exception:
        return False
    w, h = im.size
    if max(w, h) > MAX_DIM:
        scale = MAX_DIM / max(w, h)
        im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))))
    buf = io.BytesIO()
    im.save(buf, format="WEBP", quality=QUALITY, method=6)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    Path(dest_path).write_bytes(buf.getvalue())
    return True


def seed(source_dir: str, reset: bool = False) -> None:
    df = consolidate(source_dir)
    print(f"{len(df)} questões consolidadas a partir de {source_dir}")

    db: Session = SessionLocal()
    missing_images = 0
    created = updated = 0
    try:
        if reset:
            # Reset explícito é destrutivo e deve ser usado apenas em reconstruções.
            db.query(QuestionImage).delete()
            db.query(QuestionOption).delete()
            db.query(Question).delete()
            db.commit()

        for _, row in df.iterrows():
            options = row["options"]
            external_id = generate_external_id(
                year=row["year"],
                area=row["area"],
                number=row["number"],
                context=row["context"],
                statement=row["statement"],
                options=options,
            )
            question = db.query(Question).filter_by(external_id=external_id).first()

            if question is None:
                question = Question(
                    external_id=external_id,
                    year=row["year"],
                    area=row["area"],
                    number=row["number"],
                    context=row["context"],
                    statement=row["statement"],
                    correct_answer=row["correct_answer"],
                )
                db.add(question)
                db.flush()
                for position, letter in enumerate("ABCDE"):
                    db.add(QuestionOption(
                        question_id=question.id,
                        letter=letter,
                        position=position,
                        text=options[position],
                    ))
                created += 1
            else:
                # Fonte atualiza apenas campos de origem; explicações internas não são tocadas.
                question.year = row["year"]
                question.area = row["area"]
                question.number = row["number"]
                question.context = row["context"]
                question.statement = row["statement"]
                question.correct_answer = row["correct_answer"]

                by_letter = {opt.letter: opt for opt in question.options}
                for position, letter in enumerate("ABCDE"):
                    opt = by_letter.get(letter)
                    if opt is None:
                        db.add(QuestionOption(
                            question_id=question.id,
                            letter=letter,
                            position=position,
                            text=options[position],
                        ))
                    else:
                        opt.position = position
                        opt.text = options[position]
                updated += 1

            # Imagens da fonte são recriadas para a questão; explicações continuam intactas.
            for image in list(question.images):
                db.delete(image)
            db.flush()
            for position, rel_path in enumerate(row["image_paths"]):
                rel_inside_source = rel_path.removeprefix("enem-data/")
                src_path = os.path.join(source_dir, rel_inside_source)
                image_name = f"q{question.id}_{position}.webp"
                dest_path = os.path.join(settings.static_dir, "images", image_name)
                if compress_image(src_path, dest_path):
                    db.add(QuestionImage(
                        question_id=question.id,
                        path=image_name,
                        position=position,
                    ))
                else:
                    missing_images += 1

        db.commit()
    finally:
        db.close()

    print(f"seed concluído. criadas={created}, atualizadas={updated}, imagens ausentes/corrompidas={missing_images}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    seed(args.source, reset=args.reset)
