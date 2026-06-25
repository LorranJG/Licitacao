import argparse
import asyncio
from datetime import date

from app.database import SessionLocal
from app.services.licitacao_service import salvar_licitacoes_pncp
from app.services.pncp_service import PNCPService


async def executar(data_inicial: date | None, data_final: date | None) -> None:
    service = PNCPService()
    dados, periodo = await service.coletar_contratacoes(
        data_inicial=data_inicial,
        data_final=data_final,
    )
    with SessionLocal() as db:
        resultado = salvar_licitacoes_pncp(db, dados)
    print(
        f"Coleta concluída ({periodo}): {len(dados)} recebidas, "
        f"{resultado['criadas']} criadas e {resultado['atualizadas']} atualizadas."
    )


def parse_data(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coleta licitações do PNCP.")
    parser.add_argument("--data-inicial", help="Data no formato AAAA-MM-DD")
    parser.add_argument("--data-final", help="Data no formato AAAA-MM-DD")
    args = parser.parse_args()
    asyncio.run(executar(parse_data(args.data_inicial), parse_data(args.data_final)))

