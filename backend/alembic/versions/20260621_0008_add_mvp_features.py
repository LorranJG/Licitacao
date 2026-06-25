"""Adiciona buscas salvas, segurança da conta, alertas e métricas.

Revision ID: 20260621_0008
Revises: 20260621_0007
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260621_0008"
down_revision: str | None = "20260621_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("email_verificado_em", sa.DateTime(timezone=True)))
    op.add_column("usuarios", sa.Column("token_verificacao_hash", sa.String(64)))
    op.add_column("usuarios", sa.Column("token_verificacao_expira_em", sa.DateTime(timezone=True)))
    op.add_column("usuarios", sa.Column("token_redefinicao_hash", sa.String(64)))
    op.add_column("usuarios", sa.Column("token_redefinicao_expira_em", sa.DateTime(timezone=True)))
    op.create_index("ix_usuarios_token_verificacao_hash", "usuarios", ["token_verificacao_hash"], unique=True)
    op.create_index("ix_usuarios_token_redefinicao_hash", "usuarios", ["token_redefinicao_hash"], unique=True)

    op.create_table(
        "buscas_salvas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("filtros", sa.JSON(), nullable=False),
        sa.Column("alertas_ativos", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("ultima_verificacao_em", sa.DateTime(timezone=True)),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_buscas_salvas_usuario_id", "buscas_salvas", ["usuario_id"])

    op.create_table(
        "alertas_busca",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("busca_id", sa.Integer(), sa.ForeignKey("buscas_salvas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("licitacao_id", sa.Integer(), sa.ForeignKey("licitacoes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enviado_em", sa.DateTime(timezone=True)),
        sa.Column("erro_envio", sa.Text()),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("busca_id", "licitacao_id", name="uq_alertas_busca_licitacao"),
    )
    op.create_index("ix_alertas_busca_busca_id", "alertas_busca", ["busca_id"])
    op.create_index("ix_alertas_busca_licitacao_id", "alertas_busca", ["licitacao_id"])

    op.create_table(
        "eventos_produto",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL")),
        sa.Column("nome", sa.String(80), nullable=False),
        sa.Column("dados", sa.JSON(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_eventos_produto_usuario_id", "eventos_produto", ["usuario_id"])
    op.create_index("ix_eventos_produto_nome", "eventos_produto", ["nome"])
    op.create_index("ix_eventos_produto_criado_em", "eventos_produto", ["criado_em"])


def downgrade() -> None:
    op.drop_table("eventos_produto")
    op.drop_table("alertas_busca")
    op.drop_table("buscas_salvas")
    op.drop_index("ix_usuarios_token_redefinicao_hash", table_name="usuarios")
    op.drop_index("ix_usuarios_token_verificacao_hash", table_name="usuarios")
    op.drop_column("usuarios", "token_redefinicao_expira_em")
    op.drop_column("usuarios", "token_redefinicao_hash")
    op.drop_column("usuarios", "token_verificacao_expira_em")
    op.drop_column("usuarios", "token_verificacao_hash")
    op.drop_column("usuarios", "email_verificado_em")
