"""Adiciona data de atualização da fonte.

Revision ID: 20260619_0004
Revises: 20260619_0003
Create Date: 2026-06-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260619_0004"
down_revision: Union[str, None] = "20260619_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "licitacoes",
        sa.Column("data_atualizacao", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("licitacoes", "data_atualizacao")
