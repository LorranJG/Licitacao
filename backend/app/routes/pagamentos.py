from datetime import datetime, timezone
from typing import Annotated, Any

import stripe
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


def _stripe_configurado() -> bool:
    return bool(settings.stripe_secret_key and settings.stripe_price_id)


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
    if not _stripe_configurado():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pagamento ainda nao configurado.",
        )

    stripe.api_key = settings.stripe_secret_key
    session = stripe.checkout.Session.create(
        mode="payment",
        customer=usuario.stripe_customer_id or None,
        customer_email=None if usuario.stripe_customer_id else usuario.email,
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        metadata={"usuario_id": str(usuario.id)},
        success_url=(
            f"{settings.app_public_url.rstrip('/')}/comprar/sucesso"
            "?session_id={CHECKOUT_SESSION_ID}"
        ),
        cancel_url=f"{settings.app_public_url.rstrip('/')}/comprar?cancelado=1",
    )
    if not session.url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nao foi possivel iniciar o checkout.",
        )

    usuario.stripe_checkout_session_id = session.id
    if session.customer:
        usuario.stripe_customer_id = str(session.customer)
    registrar_evento(
        db,
        "checkout_criado",
        usuario_id=usuario.id,
        dados={"stripe_session_id": session.id},
    )
    db.commit()
    return CheckoutResponse(url=session.url)


def _session_dict(session: Any) -> dict[str, Any]:
    if isinstance(session, dict):
        return session
    return dict(session)


def _liberar_acesso(db: Session, session: Any) -> None:
    session_data = _session_dict(session)
    metadata = session_data.get("metadata") or {}
    usuario_id = metadata.get("usuario_id")
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
    usuario.acesso_liberado_em = usuario.acesso_liberado_em or datetime.now(
        timezone.utc
    )
    if session_data.get("id"):
        usuario.stripe_checkout_session_id = str(session_data["id"])
    if session_data.get("customer"):
        usuario.stripe_customer_id = str(session_data["customer"])
    registrar_evento(
        db,
        "compra_confirmada",
        usuario_id=usuario.id,
        dados={
            "stripe_session_id": session_data.get("id"),
            "payment_status": session_data.get("payment_status"),
        },
    )
    db.commit()


@router.post("/webhook")
async def stripe_webhook(request: Request, db: DatabaseSession) -> dict[str, bool]:
    if not settings.stripe_secret_key or not settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook de pagamento nao configurado.",
        )

    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Assinatura ausente.")

    stripe.api_key = settings.stripe_secret_key
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.stripe_webhook_secret
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Webhook invalido.") from exc
    except Exception as exc:
        if exc.__class__.__name__ != "SignatureVerificationError":
            raise
        raise HTTPException(status_code=400, detail="Webhook invalido.") from exc

    if event["type"] in {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    }:
        session = event["data"]["object"]
        session_data = _session_dict(session)
        if session_data.get("payment_status") in {"paid", "no_payment_required"}:
            _liberar_acesso(db, session)

    return {"received": True}
