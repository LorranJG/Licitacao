"""Adiciona índice GIN para busca full-text em licitacoes.

Revision ID: 20260629_0011
Revises: 20260629_0010
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260629_0011"
down_revision: str | None = "20260629_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_licitacoes_busca_fts
        ON licitacoes
        USING GIN (
            to_tsvector('portuguese'::regconfig,
                coalesce(titulo, '') || ' ' || coalesce(objeto, '') || ' ' || coalesce(orgao, ''))
        )
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_licitacoes_busca_fts")
