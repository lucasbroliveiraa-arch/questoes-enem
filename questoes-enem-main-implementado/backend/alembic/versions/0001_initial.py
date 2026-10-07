"""cria tabelas questions, question_images e answers

Revision ID: 0001
Revises:
Create Date: 2026-09-27

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("area", sa.String(length=50), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("context", sa.Text(), nullable=False, server_default=""),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("option_a", sa.Text(), nullable=False, server_default=""),
        sa.Column("option_b", sa.Text(), nullable=False, server_default=""),
        sa.Column("option_c", sa.Text(), nullable=False, server_default=""),
        sa.Column("option_d", sa.Text(), nullable=False, server_default=""),
        sa.Column("option_e", sa.Text(), nullable=False, server_default=""),
        sa.Column("correct_answer", sa.String(length=1), nullable=False),
    )
    op.create_index("ix_questions_year", "questions", ["year"])
    op.create_index("ix_questions_area", "questions", ["area"])

    op.create_table(
        "question_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("selected_option", sa.String(length=1), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("answers")
    op.drop_table("question_images")
    op.drop_index("ix_questions_area", table_name="questions")
    op.drop_index("ix_questions_year", table_name="questions")
    op.drop_table("questions")
