from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Licitacao
from app.services.licitacao_service import contar_licitacoes, listar_licitacoes


def test_filtra_licitacoes_por_faixa_de_valor() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        db.add_all(
            [
                Licitacao(
                    fonte="PNCP",
                    fonte_id="baixo",
                    titulo="Compra de baixo valor",
                    status="aberta",
                    valor_estimado=Decimal("5000"),
                    dados_originais={},
                ),
                Licitacao(
                    fonte="PNCP",
                    fonte_id="faixa",
                    titulo="Compra dentro da faixa",
                    status="aberta",
                    valor_estimado=Decimal("25000"),
                    dados_originais={},
                ),
                Licitacao(
                    fonte="PNCP",
                    fonte_id="alto",
                    titulo="Compra de alto valor",
                    status="aberta",
                    valor_estimado=Decimal("80000"),
                    dados_originais={},
                ),
                Licitacao(
                    fonte="PNCP",
                    fonte_id="sem-valor",
                    titulo="Compra sem valor informado",
                    status="aberta",
                    dados_originais={},
                ),
            ]
        )
        db.commit()

        resultado = listar_licitacoes(
            db,
            status="aberta",
            valor_minimo=Decimal("10000"),
            valor_maximo=Decimal("50000"),
        )

        assert [item.fonte_id for item in resultado] == ["faixa"]
        assert (
            contar_licitacoes(
                db,
                status="aberta",
                valor_minimo=Decimal("10000"),
                valor_maximo=Decimal("50000"),
            )
            == 1
        )
