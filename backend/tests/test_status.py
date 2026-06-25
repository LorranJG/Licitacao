from app.services.normalizador import normalizar_pncp
from app.utils.datas import hoje_local


def test_licitacao_com_encerramento_passado_fica_encerrada() -> None:
    resultado = normalizar_pncp(
        {
            "numeroControlePNCP": "teste-1",
            "objetoCompra": "Serviço de teste",
            "dataEncerramentoProposta": "2020-01-01T18:00:00",
        }
    )

    assert resultado["status"] == "encerrada"


def test_licitacao_com_encerramento_futuro_fica_aberta() -> None:
    resultado = normalizar_pncp(
        {
            "numeroControlePNCP": "teste-2",
            "objetoCompra": "Serviço de teste",
            "dataEncerramentoProposta": f"{hoje_local().year + 1}-01-01T18:00:00",
        }
    )

    assert resultado["status"] == "aberta"
