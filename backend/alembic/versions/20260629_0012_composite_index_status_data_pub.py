"""Composite index status + data_publicacao for default sort query

Revision ID: 20260629_0012
Revises: 20260629_0011
Create Date: 2026-06-29
"""

from alembic import op

revision: str = "20260629_0012"
down_revision: str | None = "20260629_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_licitacoes_status_data_pub
        ON licitacoes (status, data_publicacao DESC NULLS LAST, id DESC)
    """)


def downgrade() -> None:
    op.drop_index("ix_licitacoes_status_data_pub", table_name="licitacoes")
