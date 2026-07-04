import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Annotated

import mercadopago
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies.auth import CurrentUser
from app.models import Usuario
from app.schemas import CheckoutResponse
from app.services.conta_service import registrar_evento
from app.services.rate_limit import rate_limit

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])
DatabaseSession = Annotated[Session, Depends(get_db)]
settings = get_settings()


def _mp_configurado() -> bool:
    return bool(settings.mp_access_token)


@router.post("/checkout", response_model=CheckoutResponse)
def criar_checkout(
    usuario: CurrentUser,
    db: DatabaseSession,
    _rate_limit: None = Depends(
        rate_limit("pagamentos:checkout", max_requests=10, window_seconds=300)
    ),
) -> CheckoutResponse:
    if usuario.acesso_liberado:
        return CheckoutResponse(url=f"{settings.app_public_url.rstrip('/')}/licitacoes")
    if not _mp_configurado():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pagamento ainda não configurado.",
        )

    sdk = mercadopago.SDK(settings.mp_access_token)
    base_url = settings.app_public_url.rstrip("/")
    backend_url = settings.backend_public_url.rstrip("/")

    preference_data = {
        "items": [
            {
                "title": "Radar Licitações — Acesso completo",
                "quantity": 1,
                "unit_price": settings.mp_preco,
                "currency_id": "BRL",
            }
        ],
        "payer": {"email": usuario.email},
        "external_reference": str(usuario.id),
        "back_urls": {
            "success": f"{base_url}/comprar/sucesso",
            "failure": f"{base_url}/comprar?cancelado=1",
            "pending": f"{base_url}/comprar/sucesso",
        },
        "auto_return": "approved",
        "notification_url": f"{backend_url}/pagamentos/webhook",
    }

    response = sdk.preference().create(preference_data)
    if response["status"] != 201:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível iniciar o checkout.",
        )

    preference = response["response"]
    url_key = "init_point" if settings.is_production else "sandbox_init_point"

    usuario.mp_preference_id = preference["id"]
    registrar_evento(
        db,
        "checkout_criado",
        usuario_id=usuario.id,
        dados={"mp_preference_id": preference["id"]},
    )
    db.commit()
    return CheckoutResponse(url=preference[url_key])


def _liberar_acesso(db: Session, usuario_id: str | None, payment_id: str | None) -> None:
    if not usuario_id:
        return
    try:
        usuario = db.get(Usuario, int(usuario_id))
    except (TypeError, ValueError):
        return
    if usuario is None:
        return

    usuario.acesso_liberado = True
    usuario.plano_status = "ativo"
    usuario.acesso_liberado_em = usuario.acesso_liberado_em or datetime.now(timezone.utc)
    if payment_id:
        usuario.mp_payment_id = str(payment_id)
    registrar_evento(
        db,
        "compra_confirmada",
        usuario_id=usuario.id,
        dados={"mp_payment_id": payment_id},
    )
    db.commit()


@router.post("/webhook")
async def mp_webhook(request: Request, db: DatabaseSession) -> dict[str, bool]:
    if not _mp_configurado():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook de pagamento não configurado.",
        )

    payload = await request.body()

    if settings.mp_webhook_secret:
        x_signature = request.headers.get("x-signature", "")
        x_request_id = request.headers.get("x-request-id", "")
        parts = dict(
            part.split("=", 1) for part in x_signature.split(",") if "=" in part
        )
        ts = parts.get("ts", "")
        received = parts.get("v1", "")

        try:
            notification_id = str(json.loads(payload).get("id", ""))
        except (json.JSONDecodeError, AttributeError):
            notification_id = ""

        manifest = f"id:{notification_id};request-id:{x_request_id};ts:{ts}"
        expected = hmac.new(
            settings.mp_webhook_secret.encode(),
            manifest.encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, received):
            raise HTTPException(status_code=400, detail="Assinatura inválida.")

    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, ValueError):
        return {"received": True}

    if data.get("type") != "payment":
        return {"received": True}

    payment_id = data.get("data", {}).get("id")
    if not payment_id:
        return {"received": True}

    sdk = mercadopago.SDK(settings.mp_access_token)
    payment_response = sdk.payment().get(int(payment_id))
    if payment_response["status"] != 200:
        return {"received": True}

    payment = payment_response["response"]
    if payment.get("status") != "approved":
        return {"received": True}

    _liberar_acesso(db, payment.get("external_reference"), str(payment_id))
    return {"received": True}
