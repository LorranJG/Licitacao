"""Integração opcional com o Sentry para captura de erros.

Ativa apenas quando SENTRY_DSN está definido; caso contrário é no-op, então
não afeta desenvolvimento local nem ambientes sem o DSN configurado.
"""
import logging

from app.config import get_settings

logger = logging.getLogger("radar.observabilidade")


def init_sentry(componente: str) -> None:
    settings = get_settings()
    if not settings.sentry_dsn:
        return
    try:
        import sentry_sdk
    except ImportError:
        logger.warning("sentry-sdk não instalado; captura de erros desativada.")
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=0.0,
        send_default_pii=False,
    )
    sentry_sdk.set_tag("componente", componente)
    logger.info("Sentry ativo para o componente '%s'.", componente)
