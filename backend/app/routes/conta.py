from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.dependencies.auth import CurrentUser
from app.models import Favorito, Lembrete, Licitacao
from app.schemas import (
    FavoritoResponse,
    FavoritoStatusResponse,
    LembreteCreateRequest,
    LembreteResponse,
)
from app.services.conta_service import registrar_evento

router = APIRouter(tags=["Conta"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/favoritos", response_model=list[FavoritoResponse])
def listar_favoritos(
    usuario: CurrentUser, db: DatabaseSession
) -> list[Favorito]:
    return list(
        db.scalars(
            select(Favorito)
            .options(selectinload(Favorito.licitacao))
            .where(Favorito.usuario_id == usuario.id)
            .order_by(Favorito.criado_em.desc())
        ).all()
    )


@router.get(
    "/favoritos/{licitacao_id}/status",
    response_model=FavoritoStatusResponse,
)
def status_favorito(
    licitacao_id: int, usuario: CurrentUser, db: DatabaseSession
) -> FavoritoStatusResponse:
    favorito = db.scalar(
        select(Favorito).where(
            Favorito.usuario_id == usuario.id,
            Favorito.licitacao_id == licitacao_id,
        )
    )
    return FavoritoStatusResponse(favorito=favorito is not None)


@router.post(
    "/favoritos/{licitacao_id}",
    response_model=FavoritoResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_favorito(
    licitacao_id: int, usuario: CurrentUser, db: DatabaseSession
) -> Favorito:
    licitacao = db.get(Licitacao, licitacao_id)
    if licitacao is None:
        raise HTTPException(status_code=404, detail="Licitação não encontrada.")
    favorito = db.scalar(
        select(Favorito)
        .options(selectinload(Favorito.licitacao))
        .where(
            Favorito.usuario_id == usuario.id,
            Favorito.licitacao_id == licitacao_id,
        )
    )
    if favorito:
        return favorito
    favorito = Favorito(usuario_id=usuario.id, licitacao_id=licitacao_id)
    db.add(favorito)
    registrar_evento(
        db,
        "licitacao_favoritada",
        usuario_id=usuario.id,
        dados={"licitacao_id": licitacao_id},
    )
    db.commit()
    return db.scalar(
        select(Favorito)
        .options(selectinload(Favorito.licitacao))
        .where(Favorito.id == favorito.id)
    )


@router.delete("/favoritos/{licitacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_favorito(
    licitacao_id: int, usuario: CurrentUser, db: DatabaseSession
) -> Response:
    favorito = db.scalar(
        select(Favorito).where(
            Favorito.usuario_id == usuario.id,
            Favorito.licitacao_id == licitacao_id,
        )
    )
    if favorito:
        db.delete(favorito)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/lembretes", response_model=list[LembreteResponse])
def listar_lembretes(
    usuario: CurrentUser, db: DatabaseSession
) -> list[Lembrete]:
    return list(
        db.scalars(
            select(Lembrete)
            .options(selectinload(Lembrete.licitacao))
            .where(Lembrete.usuario_id == usuario.id)
            .order_by(Lembrete.lembrar_em.asc())
        ).all()
    )


@router.post(
    "/lembretes",
    response_model=LembreteResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_lembrete(
    payload: LembreteCreateRequest,
    usuario: CurrentUser,
    db: DatabaseSession,
) -> Lembrete:
    lembrar_em = payload.lembrar_em
    if lembrar_em.tzinfo is None:
        lembrar_em = lembrar_em.replace(tzinfo=timezone.utc)
    if lembrar_em <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O lembrete precisa estar no futuro.",
        )
    if usuario.telegram_chat_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conecte seu Telegram antes de criar um lembrete.",
        )
    if db.get(Licitacao, payload.licitacao_id) is None:
        raise HTTPException(status_code=404, detail="Licitação não encontrada.")
    lembrete = Lembrete(
        usuario_id=usuario.id,
        licitacao_id=payload.licitacao_id,
        lembrar_em=lembrar_em,
        mensagem=payload.mensagem.strip() if payload.mensagem else None,
    )
    db.add(lembrete)
    db.commit()
    return db.scalar(
        select(Lembrete)
        .options(selectinload(Lembrete.licitacao))
        .where(Lembrete.id == lembrete.id)
    )


@router.delete("/lembretes/{lembrete_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_lembrete(
    lembrete_id: int, usuario: CurrentUser, db: DatabaseSession
) -> Response:
    lembrete = db.scalar(
        select(Lembrete).where(
            Lembrete.id == lembrete_id,
            Lembrete.usuario_id == usuario.id,
        )
    )
    if lembrete is None:
        raise HTTPException(status_code=404, detail="Lembrete não encontrado.")
    db.delete(lembrete)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
