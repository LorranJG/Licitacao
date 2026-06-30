import logging

import httpx

from app.config import get_settings
from app.services.http_client import client

logger = logging.getLogger("radar.email")
settings = get_settings()


def enviar_email(*, destinatario: str, assunto: str, html: str) -> bool:
    if not settings.resend_api_key:
        logger.info("E-mail não enviado (RESEND_API_KEY ausente): %s", assunto)
        return False
    try:
        with client(timeout=15) as http_client:
            response = http_client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": settings.email_from,
                    "to": [destinatario],
                    "subject": assunto,
                    "html": html,
                },
            )
        response.raise_for_status()
        return True
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Falha ao enviar e-mail '%s' para %s: HTTP %s — %s",
            assunto,
            destinatario,
            exc.response.status_code,
            exc.response.text[:200],
        )
        return False
    except httpx.RequestError as exc:
        logger.error("Erro de rede ao enviar e-mail '%s': %s", assunto, exc)
        return False
