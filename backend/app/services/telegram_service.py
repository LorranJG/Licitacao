from __future__ import annotations

import hashlib
import html
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Licitacao, Usuario
from app.services.http_client import async_client

settings = get_settings()


class TelegramNotConfiguredError(RuntimeError):
    pass


class TelegramServiceError(RuntimeError):
    pass


def hash_link_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def criar_link_telegram(db: Session, usuario: Usuario) -> tuple[str, datetime]:
    if not settings.telegram_bot_username:
        raise TelegramNotConfiguredError(
            "Defina TELEGRAM_BOT_USERNAME para habilitar o vínculo."
        )
    token = secrets.token_urlsafe(32)
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=15)
    usuario.telegram_link_token_hash = hash_link_token(token)
    usuario.telegram_link_expires_at = expira_em
    db.commit()
    return (
        f"https://t.me/{settings.telegram_bot_username}?start={token}",
        expira_em,
    )


async def enviar_mensagem(
    chat_id: int,
    texto: str,
    *,
    botoes: list[list[dict[str, str]]] | None = None,
) -> None:
    if not settings.telegram_bot_token:
        raise TelegramNotConfiguredError(
            "Defina TELEGRAM_BOT_TOKEN para enviar mensagens."
        )
    payload: dict[str, Any] = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if botoes:
        payload["reply_markup"] = {"inline_keyboard": botoes}
    async with async_client(timeout=20) as client:
        response = await client.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            json=payload,
        )
    if response.is_error:
        raise TelegramServiceError(
            f"Telegram retornou {response.status_code}: {response.text[:300]}"
        )


def _formatar_favoritos(db: Session, usuario: Usuario) -> tuple[str, list]:
    from app.models import Favorito

    favoritos = list(
        db.scalars(
            select(Favorito)
            .where(Favorito.usuario_id == usuario.id)
            .order_by(Favorito.criado_em.desc())
            .limit(10)
        ).all()
    )
    if not favoritos:
        return "Você ainda não possui licitações favoritas.", []
    linhas = ["<b>Seus favoritos mais recentes</b>"]
    botoes: list[list[dict[str, str]]] = []
    for favorito in favoritos:
        licitacao = favorito.licitacao
        linhas.append(f"\n• {html.escape(licitacao.titulo[:100])}")
        botoes.append(
            [
                {
                    "text": f"Ver #{licitacao.id}",
                    "url": f"{settings.app_public_url}/licitacoes/{licitacao.id}",
                }
            ]
        )
    return "\n".join(linhas), botoes


async def processar_update(db: Session, update: dict[str, Any]) -> None:
    message = update.get("message")
    if not isinstance(message, dict):
        return
    text = str(message.get("text") or "").strip()
    chat = message.get("chat") or {}
    sender = message.get("from") or {}
    chat_id = chat.get("id")
    if not isinstance(chat_id, int):
        return

    if text.startswith("/start"):
        _, _, token = text.partition(" ")
        if not token:
            await enviar_mensagem(
                chat_id,
                "Abra o link gerado na sua conta do Radar Licitações para conectar este Telegram.",
            )
            return
        usuario = db.scalar(
            select(Usuario).where(
                Usuario.telegram_link_token_hash == hash_link_token(token)
            )
        )
        agora = datetime.now(timezone.utc)
        usuario_conectado = db.scalar(
            select(Usuario).where(Usuario.telegram_chat_id == chat_id)
        )
        if usuario_conectado is not None:
            await enviar_mensagem(
                chat_id,
                "Este Telegram já está conectado ao Radar Licitações.",
            )
            return
        if (
            usuario is None
            or usuario.telegram_link_expires_at is None
            or usuario.telegram_link_expires_at < agora
        ):
            await enviar_mensagem(
                chat_id,
                "Este link expirou ou já foi usado. Gere um novo link no Radar Licitações.",
            )
            return
        usuario.telegram_chat_id = chat_id
        usuario.telegram_username = sender.get("username")
        usuario.telegram_link_token_hash = None
        usuario.telegram_link_expires_at = None
        db.commit()
        await enviar_mensagem(
            chat_id,
            (
                f"Olá, <b>{html.escape(usuario.nome)}</b>! Seu Telegram foi conectado.\n\n"
                "Você receberá aqui os lembretes criados no Radar Licitações.\n"
                "Comandos: /favoritos, /prazos e /ajuda."
            ),
        )
        return

    usuario = db.scalar(select(Usuario).where(Usuario.telegram_chat_id == chat_id))
    if usuario is None:
        await enviar_mensagem(
            chat_id,
            "Este Telegram ainda não está conectado a uma conta do Radar Licitações.",
        )
        return

    if text.startswith("/favoritos"):
        mensagem, botoes = _formatar_favoritos(db, usuario)
        await enviar_mensagem(chat_id, mensagem, botoes=botoes)
    elif text.startswith("/prazos"):
        await enviar_mensagem(
            chat_id,
            (
                "Seus lembretes aparecem na área <b>Minha conta</b> do Radar. "
                "Eu enviarei uma mensagem quando cada horário chegar."
            ),
            botoes=[
                [
                    {
                        "text": "Abrir meus lembretes",
                        "url": f"{settings.app_public_url}/conta",
                    }
                ]
            ],
        )
    else:
        await enviar_mensagem(
            chat_id,
            (
                "<b>Radar Licitações</b>\n"
                "/favoritos — listar oportunidades salvas\n"
                "/prazos — abrir seus lembretes\n"
                "/ajuda — mostrar esta mensagem"
            ),
        )


def formatar_lembrete(licitacao: Licitacao, mensagem: str | None) -> str:
    partes = [
        "⏰ <b>Lembrete de licitação</b>",
        f"\n<b>{html.escape(licitacao.titulo)}</b>",
    ]
    if licitacao.orgao:
        partes.append(f"Órgão: {html.escape(licitacao.orgao)}")
    if licitacao.data_encerramento:
        partes.append(
            f"Encerramento informado: {licitacao.data_encerramento.strftime('%d/%m/%Y')}"
        )
    if mensagem:
        partes.append(f"\nSua anotação: {html.escape(mensagem)}")
    partes.append("\nConfirme sempre as datas e regras no edital oficial.")
    return "\n".join(partes)
