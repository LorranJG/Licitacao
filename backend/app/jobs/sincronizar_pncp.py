import asyncio
import logging
import sys
from datetime import date, timedelta

from app.config import get_settings
from app.database import SessionLocal
from app.models import SyncState
from app.services.licitacao_service import (
    atualizar_status_encerradas,
    salvar_licitacoes_pncp,
)
from app.services.pncp_service import PNCPService, PNCPServiceError
from app.services.sync_status_service import registrar_status_fonte
from app.utils.datas import hoje_local

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("radar.worker")
BACKFILL_STATE_KEY = "pncp_backfill_earliest_date"


def _salvar(dados: list[dict]) -> dict[str, int]:
    with SessionLocal() as db:
        return salvar_licitacoes_pncp(db, dados)


def _proximo_dia_backfill(dias: int) -> date | None:
    if dias <= 0:
        return None

    hoje = hoje_local()
    alvo = hoje - timedelta(days=dias - 1)
    with SessionLocal() as db:
        estado = db.get(SyncState, BACKFILL_STATE_KEY)

    if estado is None:
        proximo = hoje - timedelta(days=1)
    else:
        proximo = date.fromisoformat(estado.valor) - timedelta(days=1)
    return proximo if proximo >= alvo else None


def _registrar_backfill(dia: date) -> None:
    with SessionLocal() as db:
        estado = db.get(SyncState, BACKFILL_STATE_KEY)
        if estado is None:
            db.add(SyncState(chave=BACKFILL_STATE_KEY, valor=dia.isoformat()))
        else:
            estado.valor = dia.isoformat()
        db.commit()


async def executar_backfill_pendente(service: PNCPService, dias: int) -> bool:
    dia = await asyncio.to_thread(_proximo_dia_backfill, dias)
    if dia is None:
        return False

    recebidas, criadas, atualizadas, completo = await _sincronizar_modalidades(
        service,
        tipo="publicacao",
        dia=dia,
    )
    if not completo:
        logger.warning(
            "Backfill %s ficou parcial e será repetido no próximo ciclo.", dia
        )
        return True

    await asyncio.to_thread(_registrar_backfill, dia)
    logger.info(
        "Backfill %s: %s recebidas, %s criadas e %s atualizadas.",
        dia,
        recebidas,
        criadas,
        atualizadas,
    )
    return True


async def _sincronizar_modalidades(
    service: PNCPService,
    *,
    tipo: str,
    dia: date,
) -> tuple[int, int, int, bool]:
    recebidas = 0
    criadas = 0
    atualizadas = 0
    completo = True

    for modalidade in service.modalidades:
        try:
            if tipo == "abertas":
                dados, _ = await service.coletar_abertas(
                    data_final=dia,
                    modalidade_codigo=modalidade,
                )
            elif tipo == "atualizacao":
                dados, _ = await service.coletar_atualizacoes(
                    data_inicial=dia,
                    data_final=dia,
                    modalidade_codigo=modalidade,
                )
            else:
                dados, _ = await service.coletar_contratacoes(
                    data_inicial=dia,
                    data_final=dia,
                    modalidade_codigo=modalidade,
                )
            resultado = await asyncio.to_thread(_salvar, dados)
            recebidas += len(dados)
            criadas += resultado["criadas"]
            atualizadas += resultado["atualizadas"]
        except PNCPServiceError:
            completo = False
            logger.exception(
                "Falha na %s da modalidade %s em %s.",
                tipo,
                modalidade,
                dia,
            )

    return recebidas, criadas, atualizadas, completo


async def executar_ciclo(service: PNCPService) -> None:
    hoje = hoje_local()
    recebidas, criadas, atualizadas, completo = await _sincronizar_modalidades(
        service,
        tipo="atualizacao",
        dia=hoje,
    )
    with SessionLocal() as db:
        encerradas = atualizar_status_encerradas(db, hoje)
        registrar_status_fonte(
            db,
            "status_pncp",
            status="ok" if completo else "parcial",
            recebidas=recebidas,
            criadas=criadas,
            atualizadas=atualizadas,
            mensagem=f"{encerradas} oportunidades encerradas localmente.",
        )

    logger.info(
        "Sincronização %s: %s recebidas, %s criadas, %s atualizadas, "
        "%s encerradas localmente; completa=%s.",
        hoje,
        recebidas,
        criadas,
        atualizadas,
        encerradas,
        completo,
    )


async def executar_abertas(service: PNCPService) -> None:
    settings = get_settings()
    horizonte = hoje_local() + timedelta(days=settings.pncp_open_horizon_days)
    recebidas, criadas, atualizadas, completo = await _sincronizar_modalidades(
        service,
        tipo="abertas",
        dia=horizonte,
    )
    with SessionLocal() as db:
        registrar_status_fonte(
            db,
            "status_pncp",
            status="ok" if completo else "parcial",
            recebidas=recebidas,
            criadas=criadas,
            atualizadas=atualizadas,
            mensagem=f"Varredura de abertas ate {horizonte.isoformat()}.",
        )
    logger.info(
        "Varredura de abertas até %s: %s recebidas, %s criadas e %s "
        "atualizadas; completa=%s.",
        horizonte,
        recebidas,
        criadas,
        atualizadas,
        completo,
    )

async def executar_worker() -> None:
    settings = get_settings()
    service = PNCPService()

    while True:
        inicio = asyncio.get_running_loop().time()
        try:
            await executar_ciclo(service)
        except Exception as exc:
            with SessionLocal() as db:
                registrar_status_fonte(
                    db,
                    "status_pncp",
                    status="erro",
                    mensagem=str(exc)[:500],
                )
            logger.exception("Falha no ciclo de sincronização; o worker continuará ativo.")

        duracao = asyncio.get_running_loop().time() - inicio
        espera = max(5, settings.pncp_sync_interval_seconds - int(duracao))
        logger.info("Próxima sincronização em %s segundos.", espera)
        await asyncio.sleep(espera)


async def executar_backfill_worker() -> None:
    settings = get_settings()
    service = PNCPService()
    logger.info(
        "Backfill aguardará %s segundos para priorizar a sincronização recente.",
        settings.pncp_backfill_start_delay_seconds,
    )
    await asyncio.sleep(settings.pncp_backfill_start_delay_seconds)

    while True:
        try:
            executou = await executar_backfill_pendente(
                service, settings.pncp_initial_backfill_days
            )
        except Exception:
            executou = True
            logger.exception("Falha no backfill; o worker continuará ativo.")

        espera = (
            settings.pncp_backfill_interval_seconds
            if executou
            else max(3600, settings.pncp_backfill_interval_seconds)
        )
        logger.info("Próxima verificação de backfill em %s segundos.", espera)
        await asyncio.sleep(espera)


async def executar_open_worker() -> None:
    settings = get_settings()
    service = PNCPService()
    logger.info(
        "Varredura de abertas aguardará %s segundos.",
        settings.pncp_open_start_delay_seconds,
    )
    await asyncio.sleep(settings.pncp_open_start_delay_seconds)

    while True:
        inicio = asyncio.get_running_loop().time()
        try:
            await executar_abertas(service)
        except Exception:
            logger.exception("Falha na varredura de abertas; o worker continuará.")
        duracao = asyncio.get_running_loop().time() - inicio
        espera = max(
            300, settings.pncp_open_sync_interval_seconds - int(duracao)
        )
        logger.info("Próxima varredura de abertas em %s segundos.", espera)
        await asyncio.sleep(espera)


if __name__ == "__main__":
    from app.observabilidade import init_sentry

    modo = sys.argv[1] if len(sys.argv) > 1 else "live"
    init_sentry(f"pncp-worker-{modo}")
    if modo == "backfill":
        asyncio.run(executar_backfill_worker())
    elif modo == "open":
        asyncio.run(executar_open_worker())
    else:
        asyncio.run(executar_worker())
