"""Adiciona perfil da empresa e preferências do usuário.

Revision ID: 20260620_0006
Revises: 20260620_0005
Create Date: 2026-06-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260620_0006"
down_revision: Union[str, None] = "20260620_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("telefone", sa.String(30)))
    op.add_column("usuarios", sa.Column("razao_social", sa.String(255)))
    op.add_column("usuarios", sa.Column("nome_fantasia", sa.String(255)))
    op.add_column("usuarios", sa.Column("cnpj", sa.String(18)))
    op.add_column(
        "usuarios",
        sa.Column("segmentos", sa.JSON(), server_default="[]", nullable=False),
    )
    op.add_column(
        "usuarios",
        sa.Column("ufs_interesse", sa.JSON(), server_default="[]", nullable=False),
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "municipios_interesse", sa.JSON(), server_default="[]", nullable=False
        ),
    )
    op.add_column("usuarios", sa.Column("valor_minimo_interesse", sa.Numeric(18, 2)))
    op.add_column("usuarios", sa.Column("valor_maximo_interesse", sa.Numeric(18, 2)))
    op.add_column(
        "usuarios",
        sa.Column("palavras_chave", sa.JSON(), server_default="[]", nullable=False),
    )
    op.add_column(
        "usuarios",
        sa.Column("palavras_ignoradas", sa.JSON(), server_default="[]", nullable=False),
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "modalidades_interesse", sa.JSON(), server_default="[]", nullable=False
        ),
    )
    op.add_column(
        "usuarios",
        sa.Column("orgaos_interesse", sa.JSON(), server_default="[]", nullable=False),
    )
    op.add_column("usuarios", sa.Column("prazo_minimo_dias", sa.Integer()))
    op.add_column(
        "usuarios",
        sa.Column(
            "alertar_novas_oportunidades",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "alertas_antecedencia_horas",
            sa.JSON(),
            server_default="[168, 72, 24, 2]",
            nullable=False,
        ),
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "frequencia_resumo",
            sa.String(20),
            server_default="diario",
            nullable=False,
        ),
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "horario_inicio_alertas",
            sa.String(5),
            server_default="08:00",
            nullable=False,
        ),
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "horario_fim_alertas",
            sa.String(5),
            server_default="20:00",
            nullable=False,
        ),
    )


def downgrade() -> None:
    for column in [
        "horario_fim_alertas",
        "horario_inicio_alertas",
        "frequencia_resumo",
        "alertas_antecedencia_horas",
        "alertar_novas_oportunidades",
        "prazo_minimo_dias",
        "orgaos_interesse",
        "modalidades_interesse",
        "palavras_ignoradas",
        "palavras_chave",
        "valor_maximo_interesse",
        "valor_minimo_interesse",
        "municipios_interesse",
        "ufs_interesse",
        "segmentos",
        "cnpj",
        "nome_fantasia",
        "razao_social",
        "telefone",
    ]:
        op.drop_column("usuarios", column)
