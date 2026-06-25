"""Adiciona usuários, favoritos, lembretes e vínculo Telegram.

Revision ID: 20260620_0005
Revises: 20260619_0004
Create Date: 2026-06-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260620_0005"
down_revision: Union[str, None] = "20260619_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "ativo",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("telegram_chat_id", sa.BigInteger(), nullable=True),
        sa.Column("telegram_username", sa.String(length=160), nullable=True),
        sa.Column("telegram_link_token_hash", sa.String(length=64), nullable=True),
        sa.Column(
            "telegram_link_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
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
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)
    op.create_index(
        "ix_usuarios_telegram_chat_id",
        "usuarios",
        ["telegram_chat_id"],
        unique=True,
    )
    op.create_index(
        "ix_usuarios_telegram_link_token_hash",
        "usuarios",
        ["telegram_link_token_hash"],
        unique=True,
    )

    op.create_table(
        "favoritos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("licitacao_id", sa.Integer(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["licitacao_id"], ["licitacoes.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuarios.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "usuario_id",
            "licitacao_id",
            name="uq_favoritos_usuario_licitacao",
        ),
    )
    op.create_index("ix_favoritos_licitacao_id", "favoritos", ["licitacao_id"])
    op.create_index("ix_favoritos_usuario_id", "favoritos", ["usuario_id"])

    op.create_table(
        "lembretes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("licitacao_id", sa.Integer(), nullable=False),
        sa.Column("lembrar_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mensagem", sa.String(length=500), nullable=True),
        sa.Column("enviado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("erro_envio", sa.Text(), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["licitacao_id"], ["licitacoes.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuarios.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lembretes_lembrar_em", "lembretes", ["lembrar_em"])
    op.create_index("ix_lembretes_licitacao_id", "lembretes", ["licitacao_id"])
    op.create_index("ix_lembretes_usuario_id", "lembretes", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_lembretes_usuario_id", table_name="lembretes")
    op.drop_index("ix_lembretes_licitacao_id", table_name="lembretes")
    op.drop_index("ix_lembretes_lembrar_em", table_name="lembretes")
    op.drop_table("lembretes")
    op.drop_index("ix_favoritos_usuario_id", table_name="favoritos")
    op.drop_index("ix_favoritos_licitacao_id", table_name="favoritos")
    op.drop_table("favoritos")
    op.drop_index("ix_usuarios_telegram_link_token_hash", table_name="usuarios")
    op.drop_index("ix_usuarios_telegram_chat_id", table_name="usuarios")
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_table("usuarios")
