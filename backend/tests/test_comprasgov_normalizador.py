from app.services.comprasgov_normalizador import (
    normalizar_compra_direta,
    normalizar_licitacao_legada,
)


def test_normaliza_licitacao_legada() -> None:
    resultado = normalizar_licitacao_legada(
        {
            "id_compra": "25444505900032025",
            "objeto": "Contratação de serviços de tecnologia",
            "nome_modalidade": "PREGÃO",
            "situacao_aviso": "Publicado",
            "data_publicacao": "2025-01-10",
            "data_abertura_proposta": "2025-01-31",
            "valor_estimado_total": 1500.25,
            "uasg": 254445,
            "_uasg": {
                "nomeUasg": "INSTITUTO DE TECNOLOGIA",
                "siglaUf": "RJ",
                "nomeMunicipioIbge": "RIO DE JANEIRO",
                "cnpjCpfOrgao": "33781055000135",
            },
        }
    )

    assert resultado["fonte"] == "Compras.gov.br"
    assert resultado["chave_origem"] == "comprasgov:25444505900032025"
    assert resultado["orgao"] == "INSTITUTO DE TECNOLOGIA"
    assert resultado["uf"] == "RJ"


def test_normaliza_compra_direta() -> None:
    resultado = normalizar_compra_direta(
        {
            "idCompra": "42303406900012025",
            "no_ausg": "ESCRITÓRIO DO IBRAM",
            "co_modalidade_licitacao": 6,
            "ds_objeto_licitacao": "Contratação emergencial",
            "vr_estimado": 949733.90,
            "dtPublicacao": "2025-01-10",
        }
    )

    assert resultado["fonte_id"] == "compra-direta:42303406900012025"
    assert resultado["modalidade"] == "Dispensa de Licitação"
    assert str(resultado["valor_estimado"]) == "949733.9"
