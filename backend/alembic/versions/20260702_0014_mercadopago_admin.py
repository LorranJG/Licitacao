"""Substitui campos Stripe por Mercado Pago e adiciona is_admin.

Revision ID: 20260702_0014
Revises: 20260630_0013
Create Date: 2026-07-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260702_0014"
down_revision: str | None = "20260630_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("is_admin", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column("usuarios", sa.Column("mp_preference_id", sa.String(255)))
    op.add_column("usuarios", sa.Column("mp_payment_id", sa.String(255)))
    op.create_index(
        "ix_usuarios_mp_payment_id", "usuarios", ["mp_payment_id"], unique=True
    )

    op.drop_index("ix_usuarios_stripe_checkout_session_id", table_name="usuarios")
    op.drop_index("ix_usuarios_stripe_customer_id", table_name="usuarios")
    op.drop_column("usuarios", "stripe_checkout_session_id")
    op.drop_column("usuarios", "stripe_customer_id")


def downgrade() -> None:
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

    op.drop_index("ix_usuarios_mp_payment_id", table_name="usuarios")
    op.drop_column("usuarios", "mp_payment_id")
    op.drop_column("usuarios", "mp_preference_id")
    op.drop_column("usuarios", "is_admin")
