from datetime import date
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


def test_filtra_licitacoes_por_divulgacao_e_encerramento() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        db.add_all(
            [
                Licitacao(
                    fonte="PNCP",
                    fonte_id="publicacao-fora",
                    titulo="Divulgacao fora do periodo",
                    status="aberta",
                    data_publicacao=date(2026, 6, 25),
                    data_encerramento=date(2026, 7, 10),
                    dados_originais={},
                ),
                Licitacao(
                    fonte="PNCP",
                    fonte_id="encerramento-fora",
                    titulo="Encerramento fora do periodo",
                    status="aberta",
                    data_publicacao=date(2026, 6, 26),
                    data_encerramento=date(2026, 8, 1),
                    dados_originais={},
                ),
                Licitacao(
                    fonte="PNCP",
                    fonte_id="dentro",
                    titulo="Divulgacao e encerramento dentro dos periodos",
                    status="aberta",
                    data_publicacao=date(2026, 6, 26),
                    data_encerramento=date(2026, 7, 12),
                    dados_originais={},
                ),
            ]
        )
        db.commit()

        filtros = {
            "status": "aberta",
            "data_inicio": date(2026, 6, 26),
            "data_fim": date(2026, 6, 26),
            "encerramento_inicio": date(2026, 7, 1),
            "encerramento_fim": date(2026, 7, 31),
        }
        resultado = listar_licitacoes(db, **filtros)

        assert [item.fonte_id for item in resultado] == ["dentro"]
        assert contar_licitacoes(db, **filtros) == 1


def test_ordena_licitacoes_por_divulgacao_mais_recente() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        db.add_all(
            [
                Licitacao(
                    fonte="PNCP",
                    fonte_id="abertura-recente",
                    titulo="Abertura recente com divulgacao antiga",
                    status="aberta",
                    data_publicacao=date(2026, 6, 20),
                    data_abertura=date(2026, 7, 5),
                    dados_originais={},
                ),
                Licitacao(
                    fonte="PNCP",
                    fonte_id="divulgacao-recente",
                    titulo="Divulgacao mais recente",
                    status="aberta",
                    data_publicacao=date(2026, 6, 26),
                    data_abertura=date(2026, 6, 28),
                    dados_originais={},
                ),
                Licitacao(
                    fonte="PNCP",
                    fonte_id="sem-divulgacao",
                    titulo="Sem data de divulgacao",
                    status="aberta",
                    data_abertura=date(2026, 7, 10),
                    dados_originais={},
                ),
            ]
        )
        db.commit()

        resultado = listar_licitacoes(db, status="aberta")

        assert [item.fonte_id for item in resultado] == [
            "divulgacao-recente",
            "abertura-recente",
            "sem-divulgacao",
        ]
