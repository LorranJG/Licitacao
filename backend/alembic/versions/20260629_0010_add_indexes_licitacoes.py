"""Adiciona índices em data_publicacao e criado_em de licitacoes.

Revision ID: 20260629_0010
Revises: 20260627_0009
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260629_0010"
down_revision: str | None = "20260627_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_licitacoes_data_publicacao",
        "licitacoes",
        ["data_publicacao"],
    )
    op.create_index(
        "ix_licitacoes_criado_em",
        "licitacoes",
        ["criado_em"],
    )


def downgrade() -> None:
    op.drop_index("ix_licitacoes_criado_em", table_name="licitacoes")
    op.drop_index("ix_licitacoes_data_publicacao", table_name="licitacoes")
