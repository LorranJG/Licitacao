from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Usuario

password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)
settings = get_settings()


def gerar_hash_senha(senha: str) -> str:
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str | None) -> bool:
    if not senha_hash:
        return False
    return password_hash.verify(senha, senha_hash)


def criar_token_acesso(usuario: Usuario) -> tuple[str, int]:
    expiracao = datetime.now(timezone.utc) + timedelta(
        hours=settings.jwt_expiration_hours
    )
    token = jwt.encode(
        {"sub": str(usuario.id), "exp": expiracao},
        settings.jwt_secret,
        algorithm="HS256",
    )
    return token, settings.jwt_expiration_hours * 3600


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"],
        )
        usuario_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise unauthorized from exc

    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.ativo:
        raise unauthorized
    return usuario


CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def get_current_user_with_access(usuario: CurrentUser) -> Usuario:
    if not usuario.acesso_liberado:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Compra necessaria para acessar este recurso.",
        )
    return usuario


CurrentUserWithAccess = Annotated[Usuario, Depends(get_current_user_with_access)]
