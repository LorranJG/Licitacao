from app.services.normalizador import normalizar_pncp


def test_normaliza_payload_pncp() -> None:
    bruto = {
        "numeroControlePNCP": "12345678000199-1-000001/2026",
        "objetoCompra": "Aquisição de materiais de escritório",
        "modalidadeNome": "Pregão - Eletrônico",
        "valorTotalEstimado": 12500.5,
        "dataPublicacaoPncp": "2026-06-18T10:30:00",
        "dataAberturaProposta": "2026-06-20T09:00:00",
        "dataEncerramentoProposta": "2026-06-30T18:00:00",
        "anoCompra": 2026,
        "sequencialCompra": 1,
        "orgaoEntidade": {
            "cnpj": "12345678000199",
            "razaoSocial": "Prefeitura Exemplo",
        },
        "unidadeOrgao": {
            "ufSigla": "SP",
            "municipioNome": "São Paulo",
        },
    }

    resultado = normalizar_pncp(bruto)

    assert resultado["fonte"] == "PNCP"
    assert resultado["fonte_id"] == bruto["numeroControlePNCP"]
    assert resultado["uf"] == "SP"
    assert resultado["valor_estimado"] is not None
    assert resultado["link_original"].endswith("/12345678000199/2026/1")

