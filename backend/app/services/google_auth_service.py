from typing import Any

import httpx

from app.config import get_settings
from app.services.http_client import client

settings = get_settings()


class GoogleAuthError(RuntimeError):
    pass


def validar_google_id_token(token: str, nonce: str) -> dict[str, Any]:
    if not settings.google_client_id:
        raise GoogleAuthError("Login com Google não configurado.")

    try:
        with client(timeout=10) as http_client:
            response = http_client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": token},
            )
        response.raise_for_status()
        claims = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise GoogleAuthError("Token do Google inválido ou expirado.") from exc

    if claims.get("aud") != settings.google_client_id:
        raise GoogleAuthError("O token do Google pertence a outra aplicação.")
    if claims.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        raise GoogleAuthError("O emissor do token do Google é inválido.")
    if claims.get("nonce") != nonce:
        raise GoogleAuthError("A validação de segurança do Google falhou.")
    if str(claims.get("email_verified")).lower() != "true":
        raise GoogleAuthError("O e-mail da conta Google não está verificado.")
    if not claims.get("sub") or not claims.get("email"):
        raise GoogleAuthError("O Google não retornou os dados necessários.")
    return claims
