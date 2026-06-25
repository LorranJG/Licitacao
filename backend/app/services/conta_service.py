import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import EventoProduto, Usuario
from app.services.email_service import enviar_email

settings = get_settings()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def criar_token_verificacao(db: Session, usuario: Usuario) -> str:
    token = secrets.token_urlsafe(32)
    usuario.token_verificacao_hash = hash_token(token)
    usuario.token_verificacao_expira_em = datetime.now(timezone.utc) + timedelta(
        hours=24
    )
    db.commit()
    return token


def criar_token_redefinicao(db: Session, usuario: Usuario) -> str:
    token = secrets.token_urlsafe(32)
    usuario.token_redefinicao_hash = hash_token(token)
    usuario.token_redefinicao_expira_em = datetime.now(timezone.utc) + timedelta(
        minutes=30
    )
    db.commit()
    return token


def enviar_verificacao(usuario: Usuario, token: str) -> bool:
    url = f"{settings.app_public_url.rstrip('/')}/verificar-email?token={token}"
    return enviar_email(
        destinatario=usuario.email,
        assunto="Confirme seu e-mail no Radar Licitações",
        html=(
            f"<p>Olá, {usuario.nome}.</p>"
            f"<p>Confirme seu e-mail acessando <a href='{url}'>este link</a>.</p>"
            "<p>O link expira em 24 horas.</p>"
        ),
    )


def enviar_redefinicao(usuario: Usuario, token: str) -> bool:
    url = f"{settings.app_public_url.rstrip('/')}/redefinir-senha?token={token}"
    return enviar_email(
        destinatario=usuario.email,
        assunto="Redefina sua senha do Radar Licitações",
        html=(
            f"<p>Olá, {usuario.nome}.</p>"
            f"<p>Crie uma nova senha acessando <a href='{url}'>este link</a>.</p>"
            "<p>O link expira em 30 minutos. Ignore esta mensagem se não foi você.</p>"
        ),
    )


def registrar_evento(
    db: Session,
    nome: str,
    *,
    usuario_id: int | None = None,
    dados: dict | None = None,
) -> None:
    db.add(
        EventoProduto(
            usuario_id=usuario_id,
            nome=nome,
            dados=dados or {},
        )
    )
