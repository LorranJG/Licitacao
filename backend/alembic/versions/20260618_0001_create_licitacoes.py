"""Cria a tabela de licitações.

Revision ID: 20260618_0001
Revises:
Create Date: 2026-06-18
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260618_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "licitacoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fonte", sa.String(length=50), nullable=False),
        sa.Column("fonte_id", sa.String(length=160), nullable=False),
        sa.Column("titulo", sa.Text(), nullable=False),
        sa.Column("objeto", sa.Text(), nullable=True),
        sa.Column("orgao", sa.String(length=255), nullable=True),
        sa.Column("cnpj_orgao", sa.String(length=20), nullable=True),
        sa.Column("modalidade", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=True),
        sa.Column("uf", sa.String(length=2), nullable=True),
        sa.Column("municipio", sa.String(length=160), nullable=True),
        sa.Column("valor_estimado", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("data_publicacao", sa.Date(), nullable=True),
        sa.Column("data_abertura", sa.Date(), nullable=True),
        sa.Column("data_encerramento", sa.Date(), nullable=True),
        sa.Column("link_original", sa.Text(), nullable=True),
        sa.Column("dados_originais", sa.JSON(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fonte", "fonte_id", name="uq_licitacoes_fonte_fonte_id"),
    )
    op.create_index("ix_licitacoes_data_abertura", "licitacoes", ["data_abertura"])
    op.create_index("ix_licitacoes_fonte", "licitacoes", ["fonte"])
    op.create_index("ix_licitacoes_modalidade", "licitacoes", ["modalidade"])
    op.create_index("ix_licitacoes_status", "licitacoes", ["status"])
    op.create_index("ix_licitacoes_uf", "licitacoes", ["uf"])


def downgrade() -> None:
    op.drop_index("ix_licitacoes_uf", table_name="licitacoes")
    op.drop_index("ix_licitacoes_status", table_name="licitacoes")
    op.drop_index("ix_licitacoes_modalidade", table_name="licitacoes")
    op.drop_index("ix_licitacoes_fonte", table_name="licitacoes")
    op.drop_index("ix_licitacoes_data_abertura", table_name="licitacoes")
    op.drop_table("licitacoes")

