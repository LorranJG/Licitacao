"""Add indexes on orgao and municipio columns.

Revision ID: 20260630_0013
Revises: 20260629_0012
Create Date: 2026-06-30
"""

from alembic import op

revision: str = "20260630_0013"
down_revision: str | None = "20260629_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_licitacoes_orgao", "licitacoes", ["orgao"])
    op.create_index("ix_licitacoes_municipio", "licitacoes", ["municipio"])


def downgrade() -> None:
    op.drop_index("ix_licitacoes_orgao", table_name="licitacoes")
    op.drop_index("ix_licitacoes_municipio", table_name="licitacoes")
