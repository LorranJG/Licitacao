from datetime import date
from decimal import Decimal

from app.models import Licitacao
from app.services.licitacao_service import gerar_resumo_automatico


def test_resumo_automatico_reune_dados_principais() -> None:
    licitacao = Licitacao(
        fonte="PNCP",
        fonte_id="teste-resumo",
        titulo="Aquisição de software",
        objeto="Contratação de plataforma de gestão.",
        orgao="Prefeitura de Teste",
        modalidade="Pregão eletrônico",
        status="aberta",
        uf="SP",
        municipio="São Paulo",
        valor_estimado=Decimal("150000"),
        data_encerramento=date(2026, 7, 10),
        dados_originais={},
    )

    resumo = gerar_resumo_automatico(licitacao)

    assert resumo["texto"] == "Contratação de plataforma de gestão."
    assert "Órgão responsável: Prefeitura de Teste" in resumo["pontos_chave"]
    assert "Prazo para propostas: 10/07/2026" in resumo["pontos_chave"]
    assert len(resumo["pontos_atencao"]) == 1
