import asyncio

import httpx

from app.config import get_settings


async def configurar() -> None:
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError("Defina TELEGRAM_BOT_TOKEN.")
    if not settings.telegram_webhook_secret:
        raise RuntimeError("Defina TELEGRAM_WEBHOOK_SECRET.")
    webhook_url = f"{settings.backend_public_url.rstrip('/')}/telegram/webhook"
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            (
                "https://api.telegram.org/bot"
                f"{settings.telegram_bot_token}/setWebhook"
            ),
            json={
                "url": webhook_url,
                "secret_token": settings.telegram_webhook_secret,
                "allowed_updates": ["message"],
                "drop_pending_updates": True,
            },
        )
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    asyncio.run(configurar())
