import asyncio
import logging
import sys
from datetime import date, timedelta

from app.config import get_settings
from app.database import SessionLocal
from app.models import SyncState
from app.services.comprasgov_service import ComprasGovService
from app.services.licitacao_service import salvar_licitacoes_comprasgov
from app.services.sync_status_service import registrar_status_fonte
from app.utils.datas import hoje_local

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("radar.comprasgov")
BACKFILL_STATE_KEY = "comprasgov_backfill_earliest_date"


def _salvar(dados: list[dict], somente_abertas: bool = False) -> dict[str, int]:
    with SessionLocal() as db:
        return salvar_licitacoes_comprasgov(
            db, dados, somente_abertas=somente_abertas
        )


async def executar_live(service: ComprasGovService) -> None:
    settings = get_settings()
    fim = hoje_local()
    inicio = fim - timedelta(days=settings.compras_gov_sync_lookback_days - 1)
    dados, periodo = await service.coletar(
        data_inicial=inicio,
        data_final=fim,
    )
    resultado = await asyncio.to_thread(_salvar, dados, True)
    with SessionLocal() as db:
        registrar_status_fonte(
            db,
            "status_comprasgov",
            status="ok",
            recebidas=len(dados),
            criadas=resultado["criadas"],
            atualizadas=resultado["atualizadas"],
            mensagem=periodo,
        )
    logger.info(
        "Sincronização %s: %s recebidas, %s criadas e %s atualizadas.",
        periodo,
        len(dados),
        resultado["criadas"],
        resultado["atualizadas"],
    )


def _janela_backfill() -> tuple[date, date] | None:
    settings = get_settings()
    hoje = hoje_local()
    alvo = hoje - timedelta(days=settings.compras_gov_initial_backfill_days - 1)
    with SessionLocal() as db:
        estado = db.get(SyncState, BACKFILL_STATE_KEY)

    if estado is None:
        fim = hoje - timedelta(days=settings.compras_gov_sync_lookback_days)
    else:
        fim = date.fromisoformat(estado.valor) - timedelta(days=1)
    if fim < alvo:
        return None

    inicio = max(
        alvo,
        fim - timedelta(days=settings.compras_gov_backfill_chunk_days - 1),
    )
    return inicio, fim


def _registrar_backfill(inicio: date) -> None:
    with SessionLocal() as db:
        estado = db.get(SyncState, BACKFILL_STATE_KEY)
        if estado is None:
            db.add(SyncState(chave=BACKFILL_STATE_KEY, valor=inicio.isoformat()))
        else:
            estado.valor = inicio.isoformat()
        db.commit()


async def executar_backfill(service: ComprasGovService) -> bool:
    janela = await asyncio.to_thread(_janela_backfill)
    if janela is None:
        return False
    inicio, fim = janela
    dados, periodo = await service.coletar(
        data_inicial=inicio,
        data_final=fim,
    )
    resultado = await asyncio.to_thread(_salvar, dados, True)
    await asyncio.to_thread(_registrar_backfill, inicio)
    logger.info(
        "Backfill %s: %s recebidas, %s criadas e %s atualizadas.",
        periodo,
        len(dados),
        resultado["criadas"],
        resultado["atualizadas"],
    )
    return True


async def worker_live() -> None:
    settings = get_settings()
    service = ComprasGovService()
    while True:
        inicio = asyncio.get_running_loop().time()
        try:
            await executar_live(service)
        except Exception as exc:
            with SessionLocal() as db:
                registrar_status_fonte(
                    db,
                    "status_comprasgov",
                    status="erro",
                    mensagem=str(exc)[:500],
                )
            logger.exception("Falha na sincronização; o worker continuará ativo.")
        duracao = asyncio.get_running_loop().time() - inicio
        espera = max(30, settings.compras_gov_sync_interval_seconds - int(duracao))
        logger.info("Próxima sincronização em %s segundos.", espera)
        await asyncio.sleep(espera)


async def worker_backfill() -> None:
    settings = get_settings()
    service = ComprasGovService()
    logger.info(
        "Backfill aguardará %s segundos.",
        settings.compras_gov_backfill_start_delay_seconds,
    )
    await asyncio.sleep(settings.compras_gov_backfill_start_delay_seconds)

    while True:
        try:
            executou = await executar_backfill(service)
        except Exception:
            executou = True
            logger.exception("Falha no backfill; o worker continuará ativo.")
        espera = (
            settings.compras_gov_backfill_interval_seconds if executou else 3600
        )
        logger.info("Próxima verificação de backfill em %s segundos.", espera)
        await asyncio.sleep(espera)


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "live"
    asyncio.run(worker_backfill() if modo == "backfill" else worker_live())
