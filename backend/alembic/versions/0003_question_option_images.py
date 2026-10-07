"""Adiciona imagens específicas das alternativas.

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "question_option_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "option_id",
            sa.Integer(),
            sa.ForeignKey("question_options.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_question_option_images_option_id", "question_option_images", ["option_id"])


def downgrade():
    op.drop_index("ix_question_option_images_option_id", table_name="question_option_images")
    op.drop_table("question_option_images")
