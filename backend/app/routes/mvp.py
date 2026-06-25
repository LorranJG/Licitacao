from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import CurrentUser
from app.models import AlertaBusca, BuscaSalva, EventoProduto, Licitacao, SyncState
from app.schemas import (
    AtualizacaoFonteResponse,
    BuscaSalvaCreateRequest,
    BuscaSalvaResponse,
    BuscaSalvaUpdateRequest,
    EventoCreateRequest,
    MessageResponse,
    StatusDadosResponse,
)
from app.services.conta_service import registrar_evento
from app.services.licitacao_service import contar_licitacoes

router = APIRouter(tags=["MVP"])
DatabaseSession = Annotated[Session, Depends(get_db)]
FILTROS_PERMITIDOS = {
    "palavra_chave",
    "uf",
    "municipio",
    "modalidade",
    "status",
    "fonte",
    "valor_minimo",
    "valor_maximo",
}


def _normalizar_filtros(filtros: dict[str, Any]) -> dict[str, Any]:
    normalizados: dict[str, Any] = {}
    for chave, valor in filtros.items():
        if chave not in FILTROS_PERMITIDOS or valor in (None, "", "todos"):
            continue
        texto = str(valor).strip()
        if not texto:
            continue
        if chave in {"valor_minimo", "valor_maximo"}:
            try:
                normalizados[chave] = Decimal(texto)
            except InvalidOperation as exc:
                raise HTTPException(422, "Informe valores válidos.") from exc
        else:
            normalizados[chave] = texto
    if (
        normalizados.get("valor_minimo") is not None
        and normalizados.get("valor_maximo") is not None
        and normalizados["valor_minimo"] > normalizados["valor_maximo"]
    ):
        raise HTTPException(422, "O valor mínimo não pode superar o máximo.")
    return normalizados


def _response(db: Session, busca: BuscaSalva) -> BuscaSalvaResponse:
    filtros = _normalizar_filtros(busca.filtros or {})
    total = contar_licitacoes(db, **filtros)
    return BuscaSalvaResponse(
        id=busca.id,
        nome=busca.nome,
        filtros=busca.filtros or {},
        alertas_ativos=busca.alertas_ativos,
        ultima_verificacao_em=busca.ultima_verificacao_em,
        criado_em=busca.criado_em,
        total_correspondencias=total,
    )


@router.get("/buscas-salvas", response_model=list[BuscaSalvaResponse])
def listar_buscas(usuario: CurrentUser, db: DatabaseSession) -> list[BuscaSalvaResponse]:
    buscas = db.scalars(
        select(BuscaSalva)
        .where(BuscaSalva.usuario_id == usuario.id)
        .order_by(BuscaSalva.criado_em.desc())
    ).all()
    return [_response(db, busca) for busca in buscas]


@router.post(
    "/buscas-salvas",
    response_model=BuscaSalvaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_busca(
    payload: BuscaSalvaCreateRequest,
    usuario: CurrentUser,
    db: DatabaseSession,
) -> BuscaSalvaResponse:
    filtros = _normalizar_filtros(payload.filtros)
    if not filtros:
        raise HTTPException(422, "Use pelo menos um filtro antes de salvar.")
    if db.scalar(
        select(func.count(BuscaSalva.id)).where(BuscaSalva.usuario_id == usuario.id)
    ) >= 20:
        raise HTTPException(409, "Você pode manter até 20 buscas salvas.")
    busca = BuscaSalva(
        usuario_id=usuario.id,
        nome=payload.nome.strip(),
        filtros={chave: str(valor) for chave, valor in filtros.items()},
        alertas_ativos=payload.alertas_ativos,
        ultima_verificacao_em=datetime.now(timezone.utc),
    )
    db.add(busca)
    registrar_evento(db, "busca_salva_criada", usuario_id=usuario.id)
    db.commit()
    db.refresh(busca)
    return _response(db, busca)


@router.put("/buscas-salvas/{busca_id}", response_model=BuscaSalvaResponse)
def atualizar_busca(
    busca_id: int,
    payload: BuscaSalvaUpdateRequest,
    usuario: CurrentUser,
    db: DatabaseSession,
) -> BuscaSalvaResponse:
    busca = db.scalar(
        select(BuscaSalva).where(
            BuscaSalva.id == busca_id, BuscaSalva.usuario_id == usuario.id
        )
    )
    if busca is None:
        raise HTTPException(404, "Busca salva não encontrada.")
    busca.nome = payload.nome.strip()
    busca.alertas_ativos = payload.alertas_ativos
    db.commit()
    db.refresh(busca)
    return _response(db, busca)


@router.delete("/buscas-salvas/{busca_id}", status_code=204)
def excluir_busca(
    busca_id: int, usuario: CurrentUser, db: DatabaseSession
) -> Response:
    busca = db.scalar(
        select(BuscaSalva).where(
            BuscaSalva.id == busca_id, BuscaSalva.usuario_id == usuario.id
        )
    )
    if busca is None:
        raise HTTPException(404, "Busca salva não encontrada.")
    db.delete(busca)
    db.commit()
    return Response(status_code=204)


@router.post("/eventos", response_model=MessageResponse, status_code=201)
def criar_evento(
    payload: EventoCreateRequest,
    usuario: CurrentUser,
    db: DatabaseSession,
) -> MessageResponse:
    registrar_evento(
        db, payload.nome, usuario_id=usuario.id, dados=payload.dados
    )
    db.commit()
    return MessageResponse(message="Evento registrado.")


def _fonte_status(db: Session, chave: str, nome: str) -> AtualizacaoFonteResponse:
    estado = db.get(SyncState, chave)
    if estado is None:
        return AtualizacaoFonteResponse(
            fonte=nome, ultima_execucao_em=None, status="sem_dados"
        )
    try:
        import json

        dados = json.loads(estado.valor)
        return AtualizacaoFonteResponse(fonte=nome, **dados)
    except (ValueError, TypeError):
        return AtualizacaoFonteResponse(
            fonte=nome,
            ultima_execucao_em=estado.atualizado_em,
            status="desconhecido",
            mensagem=estado.valor[:300],
        )


@router.get("/status-dados", response_model=StatusDadosResponse)
def status_dados(db: DatabaseSession) -> StatusDadosResponse:
    return StatusDadosResponse(
        ultima_licitacao_atualizada_em=db.scalar(func.max(Licitacao.atualizado_em)),
        total_licitacoes=int(db.scalar(select(func.count(Licitacao.id))) or 0),
        fontes=[
            _fonte_status(db, "status_pncp", "PNCP"),
            _fonte_status(db, "status_comprasgov", "Compras.gov.br"),
        ],
    )
