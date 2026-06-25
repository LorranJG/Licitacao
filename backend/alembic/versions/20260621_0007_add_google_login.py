"""Adiciona autenticação com Google.

Revision ID: 20260621_0007
Revises: 20260620_0006
Create Date: 2026-06-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260621_0007"
down_revision: Union[str, None] = "20260620_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("usuarios", "senha_hash", existing_type=sa.String(255), nullable=True)
    op.add_column("usuarios", sa.Column("google_sub", sa.String(255), nullable=True))
    op.create_index(
        "ix_usuarios_google_sub", "usuarios", ["google_sub"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_usuarios_google_sub", table_name="usuarios")
    op.drop_column("usuarios", "google_sub")
    op.execute(
        "UPDATE usuarios SET senha_hash = '' WHERE senha_hash IS NULL"
    )
    op.alter_column("usuarios", "senha_hash", existing_type=sa.String(255), nullable=False)
