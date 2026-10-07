"""Adiciona identidade estável e normaliza alternativas como entidade.

Revision ID: 0002
Revises: 0001
"""

import hashlib
import json
import re
import unicodedata

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def normalize(value):
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def external_id(row):
    payload = {
        "area": normalize(row["area"]),
        "context": normalize(row["context"]),
        "number": int(row["number"]),
        "options": [normalize(row[f"option_{letter}"]) for letter in "abcde"],
        "statement": normalize(row["statement"]),
        "year": int(row["year"]),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def upgrade():
    op.add_column("questions", sa.Column("external_id", sa.String(length=64), nullable=True))
    op.add_column("questions", sa.Column("explanation", sa.Text(), nullable=False, server_default=""))

    bind = op.get_bind()
    rows = bind.execute(sa.text("""
        SELECT id, year, area, number, context, statement,
               option_a, option_b, option_c, option_d, option_e
        FROM questions
        ORDER BY id
    """)).mappings().all()

    seen = set()
    for row in rows:
        eid = external_id(row)
        if eid in seen:
            raise RuntimeError(
                f"external_id duplicado durante migration para question.id={row['id']}"
            )
        seen.add(eid)
        bind.execute(
            sa.text("UPDATE questions SET external_id = :external_id WHERE id = :id"),
            {"external_id": eid, "id": row["id"]},
        )

    op.create_index("ix_questions_external_id", "questions", ["external_id"], unique=True)

    op.create_table(
        "question_options",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "question_id",
            sa.Integer(),
            sa.ForeignKey("questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("letter", sa.String(length=1), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False, server_default=""),
        sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
        sa.UniqueConstraint("question_id", "letter", name="uq_question_options_question_letter"),
        sa.UniqueConstraint("question_id", "position", name="uq_question_options_question_position"),
    )
    op.create_index("ix_question_options_question_id", "question_options", ["question_id"])

    rows = bind.execute(sa.text("""
        SELECT id, option_a, option_b, option_c, option_d, option_e
        FROM questions
        ORDER BY id
    """)).mappings().all()
    for row in rows:
        for position, letter in enumerate("ABCDE"):
            bind.execute(
                sa.text("""
                    INSERT INTO question_options
                        (question_id, letter, position, text, explanation)
                    VALUES
                        (:question_id, :letter, :position, :text, '')
                """),
                {
                    "question_id": row["id"],
                    "letter": letter,
                    "position": position,
                    "text": row[f"option_{letter.lower()}"] or "",
                },
            )

    with op.batch_alter_table("questions") as batch:
        batch.alter_column("external_id", nullable=False)
        batch.drop_column("option_a")
        batch.drop_column("option_b")
        batch.drop_column("option_c")
        batch.drop_column("option_d")
        batch.drop_column("option_e")


def downgrade():
    with op.batch_alter_table("questions") as batch:
        for name in "abcde":
            batch.add_column(sa.Column(f"option_{name}", sa.Text(), nullable=False, server_default=""))

    bind = op.get_bind()
    rows = bind.execute(sa.text("""
        SELECT question_id, letter, text
        FROM question_options
        ORDER BY question_id, position
    """)).mappings().all()
    for row in rows:
        bind.execute(
            sa.text(
                f"UPDATE questions SET option_{row['letter'].lower()} = :text WHERE id = :id"
            ),
            {"text": row["text"], "id": row["question_id"]},
        )

    op.drop_index("ix_question_options_question_id", table_name="question_options")
    op.drop_table("question_options")
    op.drop_index("ix_questions_external_id", table_name="questions")
    op.drop_column("questions", "explanation")
    op.drop_column("questions", "external_id")
