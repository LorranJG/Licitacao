"""Adiciona chave de deduplicação entre fontes.

Revision ID: 20260619_0003
Revises: 20260618_0002
Create Date: 2026-06-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260619_0003"
down_revision: Union[str, None] = "20260618_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "licitacoes",
        sa.Column("chave_origem", sa.String(length=220), nullable=True),
    )
    op.create_index(
        "ix_licitacoes_chave_origem",
        "licitacoes",
        ["chave_origem"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_licitacoes_chave_origem", table_name="licitacoes")
    op.drop_column("licitacoes", "chave_origem")
