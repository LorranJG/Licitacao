import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import SessionLocal
from app.models import Lembrete
from app.services.telegram_service import (
    TelegramServiceError,
    enviar_mensagem,
    formatar_lembrete,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("radar.lembretes")
settings = get_settings()


async def enviar_pendentes() -> int:
    agora = datetime.now(timezone.utc)
    with SessionLocal() as db:
        lembretes = list(
            db.scalars(
                select(Lembrete)
                .options(
                    selectinload(Lembrete.usuario),
                    selectinload(Lembrete.licitacao),
                )
                .where(
                    Lembrete.enviado_em.is_(None),
                    Lembrete.lembrar_em <= agora,
                )
                .order_by(Lembrete.lembrar_em)
                .limit(100)
            ).all()
        )
        enviados = 0
        for lembrete in lembretes:
            chat_id = lembrete.usuario.telegram_chat_id
            if chat_id is None:
                lembrete.erro_envio = "Telegram não conectado."
                continue
            try:
                await enviar_mensagem(
                    chat_id,
                    formatar_lembrete(lembrete.licitacao, lembrete.mensagem),
                    botoes=[
                        [
                            {
                                "text": "Abrir licitação",
                                "url": f"{settings.app_public_url}/licitacoes/"
                                f"{lembrete.licitacao_id}",
                            }
                        ]
                    ],
                )
                lembrete.enviado_em = datetime.now(timezone.utc)
                lembrete.erro_envio = None
                enviados += 1
            except TelegramServiceError as exc:
                lembrete.erro_envio = str(exc)[:1000]
                logger.exception("Falha ao enviar lembrete %s.", lembrete.id)
        db.commit()
    return enviados


async def executar_worker() -> None:
    while True:
        try:
            enviados = await enviar_pendentes()
            if enviados:
                logger.info("%s lembretes enviados.", enviados)
        except Exception:
            logger.exception("Falha no ciclo de lembretes.")
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(executar_worker())
