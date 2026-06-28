from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import (
    CurrentUser,
    criar_token_acesso,
    gerar_hash_senha,
    verificar_senha,
)
from app.models import Usuario
from app.schemas import (
    AlterarSenhaRequest,
    ConfirmarEmailRequest,
    GoogleLoginRequest,
    MessageResponse,
    RedefinirSenhaRequest,
    SolicitarRedefinicaoRequest,
    TokenResponse,
    UsuarioLoginRequest,
    UsuarioRegistroRequest,
    UsuarioResponse,
    UsuarioUpdateRequest,
)
from app.services.google_auth_service import GoogleAuthError, validar_google_id_token
from app.services.conta_service import (
    criar_token_redefinicao,
    criar_token_verificacao,
    enviar_redefinicao,
    enviar_verificacao,
    hash_token,
    registrar_evento,
)
from app.services.rate_limit import rate_limit

router = APIRouter(prefix="/auth", tags=["Autenticação"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def _token_expirado(expira_em: datetime | None, agora: datetime) -> bool:
    if expira_em is None:
        return True
    if expira_em.tzinfo is None:
        expira_em = expira_em.replace(tzinfo=timezone.utc)
    return expira_em < agora


def _usuario_response(usuario: Usuario) -> UsuarioResponse:
    return UsuarioResponse(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        telefone=usuario.telefone,
        razao_social=usuario.razao_social,
        nome_fantasia=usuario.nome_fantasia,
        cnpj=usuario.cnpj,
        segmentos=usuario.segmentos or [],
        ufs_interesse=usuario.ufs_interesse or [],
        municipios_interesse=usuario.municipios_interesse or [],
        valor_minimo_interesse=usuario.valor_minimo_interesse,
        valor_maximo_interesse=usuario.valor_maximo_interesse,
        palavras_chave=usuario.palavras_chave or [],
        palavras_ignoradas=usuario.palavras_ignoradas or [],
        modalidades_interesse=usuario.modalidades_interesse or [],
        orgaos_interesse=usuario.orgaos_interesse or [],
        prazo_minimo_dias=usuario.prazo_minimo_dias,
        alertar_novas_oportunidades=usuario.alertar_novas_oportunidades,
        alertas_antecedencia_horas=usuario.alertas_antecedencia_horas or [],
        frequencia_resumo=usuario.frequencia_resumo,
        horario_inicio_alertas=usuario.horario_inicio_alertas,
        horario_fim_alertas=usuario.horario_fim_alertas,
        google_conectado=usuario.google_sub is not None,
        tem_senha=usuario.senha_hash is not None,
        telegram_conectado=usuario.telegram_chat_id is not None,
        telegram_username=usuario.telegram_username,
        email_verificado=usuario.email_verificado_em is not None,
        acesso_liberado=usuario.acesso_liberado,
        plano_status=usuario.plano_status,
        acesso_liberado_em=usuario.acesso_liberado_em,
    )


def _token_response(usuario: Usuario) -> TokenResponse:
    token, expires_in = criar_token_acesso(usuario)
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        usuario=_usuario_response(usuario),
    )


@router.post(
    "/registrar",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def registrar(
    payload: UsuarioRegistroRequest,
    db: DatabaseSession,
    _rate_limit: None = Depends(
        rate_limit("auth:registrar", max_requests=5, window_seconds=600)
    ),
) -> TokenResponse:
    email = payload.email.strip().lower()
    if "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Informe um e-mail válido.",
        )
    existente = db.scalar(
        select(Usuario).where(func.lower(Usuario.email) == email)
    )
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma conta com este e-mail.",
        )
    usuario = Usuario(
        nome=payload.nome.strip(),
        email=email,
        senha_hash=gerar_hash_senha(payload.senha),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    token = criar_token_verificacao(db, usuario)
    enviar_verificacao(usuario, token)
    registrar_evento(db, "cadastro_concluido", usuario_id=usuario.id)
    db.commit()
    return _token_response(usuario)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UsuarioLoginRequest,
    db: DatabaseSession,
    _rate_limit: None = Depends(
        rate_limit("auth:login", max_requests=10, window_seconds=300)
    ),
) -> TokenResponse:
    email = payload.email.strip().lower()
    usuario = db.scalar(
        select(Usuario).where(func.lower(Usuario.email) == email)
    )
    if usuario is None or not verificar_senha(payload.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )
    return _token_response(usuario)


@router.post("/google", response_model=TokenResponse)
def login_google(
    payload: GoogleLoginRequest,
    db: DatabaseSession,
    _rate_limit: None = Depends(
        rate_limit("auth:google", max_requests=20, window_seconds=300)
    ),
) -> TokenResponse:
    try:
        claims = validar_google_id_token(payload.id_token, payload.nonce)
    except GoogleAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    google_sub = str(claims["sub"])
    email = str(claims["email"]).strip().lower()
    usuario = db.scalar(select(Usuario).where(Usuario.google_sub == google_sub))
    if usuario is None:
        usuario = db.scalar(
            select(Usuario).where(func.lower(Usuario.email) == email)
        )
    if usuario is None:
        usuario = Usuario(
            nome=str(claims.get("name") or email.split("@", 1)[0]),
            email=email,
            senha_hash=None,
            google_sub=google_sub,
            email_verificado_em=datetime.now(timezone.utc),
        )
        db.add(usuario)
    else:
        if usuario.google_sub and usuario.google_sub != google_sub:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este e-mail já está vinculado a outra conta Google.",
            )
        usuario.google_sub = google_sub
        usuario.email_verificado_em = usuario.email_verificado_em or datetime.now(
            timezone.utc
        )
    db.commit()
    db.refresh(usuario)
    return _token_response(usuario)


@router.get("/me", response_model=UsuarioResponse)
def me(usuario: CurrentUser) -> UsuarioResponse:
    return _usuario_response(usuario)


@router.put("/me", response_model=UsuarioResponse)
def atualizar_me(
    payload: UsuarioUpdateRequest,
    usuario: CurrentUser,
    db: DatabaseSession,
) -> UsuarioResponse:
    if (
        payload.valor_minimo_interesse is not None
        and payload.valor_maximo_interesse is not None
        and payload.valor_minimo_interesse > payload.valor_maximo_interesse
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O valor mínimo não pode ser maior que o valor máximo.",
        )
    for field, value in payload.model_dump().items():
        if isinstance(value, str):
            value = value.strip() or None
        elif isinstance(value, list):
            value = list(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))
        setattr(usuario, field, value)
    db.commit()
    db.refresh(usuario)
    return _usuario_response(usuario)


@router.post("/alterar-senha", response_model=MessageResponse)
def alterar_senha(
    payload: AlterarSenhaRequest,
    usuario: CurrentUser,
    db: DatabaseSession,
    _rate_limit: None = Depends(
        rate_limit("auth:alterar-senha", max_requests=5, window_seconds=300)
    ),
) -> MessageResponse:
    if usuario.senha_hash and not verificar_senha(
        payload.senha_atual or "", usuario.senha_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha atual está incorreta.",
        )
    if payload.senha_atual and payload.senha_atual == payload.nova_senha:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A nova senha precisa ser diferente da senha atual.",
        )
    usuario.senha_hash = gerar_hash_senha(payload.nova_senha)
    db.commit()
    return MessageResponse(message="Senha alterada com sucesso.")


@router.post("/solicitar-redefinicao", response_model=MessageResponse)
def solicitar_redefinicao(
    payload: SolicitarRedefinicaoRequest,
    db: DatabaseSession,
    _rate_limit: None = Depends(
        rate_limit("auth:solicitar-redefinicao", max_requests=5, window_seconds=600)
    ),
) -> MessageResponse:
    email = payload.email.strip().lower()
    usuario = db.scalar(select(Usuario).where(func.lower(Usuario.email) == email))
    if usuario and usuario.ativo:
        token = criar_token_redefinicao(db, usuario)
        enviar_redefinicao(usuario, token)
    return MessageResponse(
        message="Se o e-mail estiver cadastrado, enviaremos as instruções."
    )


@router.post("/redefinir-senha", response_model=MessageResponse)
def redefinir_senha(
    payload: RedefinirSenhaRequest,
    db: DatabaseSession,
    _rate_limit: None = Depends(
        rate_limit("auth:redefinir-senha", max_requests=5, window_seconds=600)
    ),
) -> MessageResponse:
    agora = datetime.now(timezone.utc)
    usuario = db.scalar(
        select(Usuario).where(Usuario.token_redefinicao_hash == hash_token(payload.token))
    )
    if (
        usuario is None
        or _token_expirado(usuario.token_redefinicao_expira_em, agora)
    ):
        raise HTTPException(400, "O link é inválido ou expirou.")
    usuario.senha_hash = gerar_hash_senha(payload.nova_senha)
    usuario.token_redefinicao_hash = None
    usuario.token_redefinicao_expira_em = None
    registrar_evento(db, "senha_redefinida", usuario_id=usuario.id)
    db.commit()
    return MessageResponse(message="Senha redefinida. Você já pode entrar.")


@router.post("/confirmar-email", response_model=MessageResponse)
def confirmar_email(
    payload: ConfirmarEmailRequest,
    db: DatabaseSession,
    _rate_limit: None = Depends(
        rate_limit("auth:confirmar-email", max_requests=20, window_seconds=600)
    ),
) -> MessageResponse:
    agora = datetime.now(timezone.utc)
    usuario = db.scalar(
        select(Usuario).where(Usuario.token_verificacao_hash == hash_token(payload.token))
    )
    if (
        usuario is None
        or _token_expirado(usuario.token_verificacao_expira_em, agora)
    ):
        raise HTTPException(400, "O link é inválido ou expirou.")
    usuario.email_verificado_em = agora
    usuario.token_verificacao_hash = None
    usuario.token_verificacao_expira_em = None
    registrar_evento(db, "email_verificado", usuario_id=usuario.id)
    db.commit()
    return MessageResponse(message="E-mail confirmado com sucesso.")


@router.post("/reenviar-verificacao", response_model=MessageResponse)
def reenviar_verificacao(
    usuario: CurrentUser, db: DatabaseSession
) -> MessageResponse:
    if usuario.email_verificado_em:
        return MessageResponse(message="Seu e-mail já está confirmado.")
    token = criar_token_verificacao(db, usuario)
    enviado = enviar_verificacao(usuario, token)
    return MessageResponse(
        message=(
            "E-mail de confirmação enviado."
            if enviado
            else "Confirmação preparada. Configure o serviço de e-mail para o envio."
        )
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def excluir_conta(
    usuario: CurrentUser, db: DatabaseSession
) -> Response:
    db.delete(usuario)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
