"""Cria tabela de estado da sincronização.

Revision ID: 20260618_0002
Revises: 20260618_0001
Create Date: 2026-06-18
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260618_0002"
down_revision: Union[str, None] = "20260618_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sync_states",
        sa.Column("chave", sa.String(length=100), nullable=False),
        sa.Column("valor", sa.Text(), nullable=False),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("chave"),
    )


def downgrade() -> None:
    op.drop_table("sync_states")
