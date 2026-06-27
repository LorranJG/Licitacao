"""Adiciona controle de acesso por pagamento.

Revision ID: 20260627_0009
Revises: 20260621_0008
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260627_0009"
down_revision: str | None = "20260621_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "acesso_liberado",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
    )
    op.add_column(
        "usuarios",
        sa.Column("acesso_liberado_em", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "plano_status",
            sa.String(30),
            server_default="pendente",
            nullable=False,
        ),
    )
    op.add_column("usuarios", sa.Column("stripe_customer_id", sa.String(255)))
    op.add_column(
        "usuarios", sa.Column("stripe_checkout_session_id", sa.String(255))
    )
    op.create_index(
        "ix_usuarios_stripe_customer_id",
        "usuarios",
        ["stripe_customer_id"],
        unique=True,
    )
    op.create_index(
        "ix_usuarios_stripe_checkout_session_id",
        "usuarios",
        ["stripe_checkout_session_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_usuarios_stripe_checkout_session_id", table_name="usuarios")
    op.drop_index("ix_usuarios_stripe_customer_id", table_name="usuarios")
    op.drop_column("usuarios", "stripe_checkout_session_id")
    op.drop_column("usuarios", "stripe_customer_id")
    op.drop_column("usuarios", "plano_status")
    op.drop_column("usuarios", "acesso_liberado_em")
    op.drop_column("usuarios", "acesso_liberado")
