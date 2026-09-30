"""
Popula o banco a partir do repositório de dados brutos: consolida os CSVs
(consolidate.py), comprime as imagens de cada questão (WebP, redimensionadas)
salvando-as em app/static/images/, e insere tudo em Postgres via SQLAlchemy.

Substitui o antigo par consolidate.py + generate_data.py do MVP em HTML: a
diferença é que a imagem agora vira um arquivo estático servido pela API, em
vez de um base64 embutido num JSON gigante — não há mais motivo pra
comprimir agressivamente só para caber num limite de tamanho de arquivo.

Uso:
    python -m pipeline.seed_db --source /caminho/para/extract-enem-data/enem-data
"""
import argparse
import io
import os
import sys
from pathlib import Path

from PIL import Image
from sqlalchemy.orm import Session

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import settings  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.question import Question  # noqa: E402
from app.models.question_image import QuestionImage  # noqa: E402
from pipeline.consolidate import consolidate  # noqa: E402

# Imagens ainda são redimensionadas (pouco sentido em servir uma foto de
# 3000px para caber numa tela de estudo), mas com folga bem maior que no MVP
# em HTML, já que não competem mais por espaço num único arquivo.
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
    with open(dest_path, "wb") as f:
        f.write(buf.getvalue())
    return True


def seed(source_dir: str, reset: bool = False) -> None:
    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    df = consolidate(source_dir)
    print(f"{len(df)} questões consolidadas a partir de {source_dir}")

    db: Session = SessionLocal()
    missing_images = 0
    try:
        db.query(QuestionImage).delete()
        db.query(Question).delete()
        db.commit()

        for _, row in df.iterrows():
            question = Question(
                year=row["year"],
                area=row["area"],
                number=row["number"],
                context=row["context"],
                statement=row["statement"],
                option_a=row["option_a"],
                option_b=row["option_b"],
                option_c=row["option_c"],
                option_d=row["option_d"],
                option_e=row["option_e"],
                correct_answer=row["correct_answer"],
            )
            db.add(question)
            db.flush()  # garante question.id antes de criar as imagens

            for position, rel_path in enumerate(row["image_paths"]):
                # rel_path vem do CSV original como "enem-data/enem-2009/...",
                # ou seja, relativo à raiz do repositório de dados (um nível
                # acima da pasta enem-data/ que passamos em --source). Como
                # `source_dir` já É a pasta enem-data/, removemos esse
                # prefixo duplicado antes de juntar os caminhos.
                rel_inside_source = rel_path.removeprefix("enem-data/")
                src_path = os.path.join(source_dir, rel_inside_source)
                image_name = f"q{question.id}_{position}.webp"
                dest_path = os.path.join(settings.static_dir, "images", image_name)
                if compress_image(src_path, dest_path):
                    db.add(QuestionImage(question_id=question.id, path=image_name, position=position))
                else:
                    missing_images += 1

        db.commit()
    finally:
        db.close()

    print(f"seed concluído. imagens ausentes/corrompidas na fonte: {missing_images}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Caminho para a pasta enem-data/ do repositório de dados")
    parser.add_argument("--reset", action="store_true", help="Apaga e recria as tabelas antes de popular")
    args = parser.parse_args()
    seed(args.source, reset=args.reset)
