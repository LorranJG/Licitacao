from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies.auth import CurrentUserWithAccess
from app.schemas import TelegramLinkResponse, TelegramStatusResponse
from app.services.telegram_service import (
    TelegramNotConfiguredError,
    criar_link_telegram,
    processar_update,
)

router = APIRouter(prefix="/telegram", tags=["Telegram"])
DatabaseSession = Annotated[Session, Depends(get_db)]
settings = get_settings()


@router.get("/status", response_model=TelegramStatusResponse)
def status_telegram(usuario: CurrentUserWithAccess) -> TelegramStatusResponse:
    return TelegramStatusResponse(
        conectado=usuario.telegram_chat_id is not None,
        username=usuario.telegram_username,
    )


@router.post("/link", response_model=TelegramLinkResponse)
def gerar_link(
    usuario: CurrentUserWithAccess, db: DatabaseSession
) -> TelegramLinkResponse:
    try:
        url, expira_em = criar_link_telegram(db, usuario)
    except TelegramNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return TelegramLinkResponse(url=url, expira_em=expira_em)


@router.delete("/link", status_code=status.HTTP_204_NO_CONTENT)
def desconectar(usuario: CurrentUserWithAccess, db: DatabaseSession) -> Response:
    usuario.telegram_chat_id = None
    usuario.telegram_username = None
    usuario.telegram_link_token_hash = None
    usuario.telegram_link_expires_at = None
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/webhook", include_in_schema=False)
async def webhook(
    update: dict[str, Any],
    db: DatabaseSession,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
) -> dict[str, bool]:
    if not settings.telegram_bot_token or not settings.telegram_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram não configurado.",
        )
    if (
        x_telegram_bot_api_secret_token != settings.telegram_webhook_secret
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await processar_update(db, update)
    return {"ok": True}
