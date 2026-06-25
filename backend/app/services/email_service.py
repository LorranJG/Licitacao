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
