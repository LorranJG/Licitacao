from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ColetaComprasGovRequest,
    ColetaComprasGovResponse,
    ColetaPNCPRequest,
    ColetaPNCPResponse,
    IndicadoresResponse,
    LicitacaoDetalheResponse,
    LicitacaoResponse,
)
from app.services.licitacao_service import (
    buscar_licitacao,
    contar_licitacoes,
    detalhar_licitacao,
    listar_licitacoes,
    obter_indicadores,
    salvar_licitacoes_comprasgov,
    salvar_licitacoes_pncp,
)
from app.services.comprasgov_service import (
    ComprasGovService,
    ComprasGovServiceError,
)
from app.services.pncp_service import PNCPService, PNCPServiceError

router = APIRouter(prefix="/licitacoes", tags=["Licitações"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[LicitacaoResponse])
def listar(
    response: Response,
    db: DatabaseSession,
    palavra_chave: str | None = None,
    uf: str | None = Query(default=None, min_length=2, max_length=2),
    municipio: str | None = None,
    modalidade: str | None = None,
    status_licitacao: str | None = Query(default=None, alias="status"),
    data_inicio: date | None = None,
    data_fim: date | None = None,
    fonte: str | None = None,
    valor_minimo: Decimal | None = Query(default=None, ge=0),
    valor_maximo: Decimal | None = Query(default=None, ge=0),
    limite: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[LicitacaoResponse]:
    if (
        valor_minimo is not None
        and valor_maximo is not None
        and valor_minimo > valor_maximo
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O valor mínimo não pode ser maior que o valor máximo.",
        )

    filtros = {
        "palavra_chave": palavra_chave,
        "uf": uf,
        "municipio": municipio,
        "modalidade": modalidade,
        "status": status_licitacao,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "fonte": fonte,
        "valor_minimo": valor_minimo,
        "valor_maximo": valor_maximo,
    }
    total = contar_licitacoes(db, **filtros)
    response.headers["X-Total-Count"] = str(total)
    return listar_licitacoes(
        db,
        **filtros,
        limite=limite,
        offset=offset,
    )


@router.post(
    "/coletar/pncp",
    response_model=ColetaPNCPResponse,
    status_code=status.HTTP_201_CREATED,
)
async def coletar_pncp(
    payload: ColetaPNCPRequest,
    db: DatabaseSession,
) -> ColetaPNCPResponse:
    try:
        service = PNCPService()
        dados, periodo = await service.coletar_contratacoes(
            data_inicial=payload.data_inicial,
            data_final=payload.data_final,
            modalidade_codigo=payload.modalidade_codigo,
        )
        resultado = salvar_licitacoes_pncp(db, dados)
        return ColetaPNCPResponse(
            recebidas=len(dados),
            criadas=resultado["criadas"],
            atualizadas=resultado["atualizadas"],
            periodo=periodo,
        )
    except PNCPServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.post(
    "/coletar/compras-gov",
    response_model=ColetaComprasGovResponse,
    status_code=status.HTTP_201_CREATED,
)
async def coletar_compras_gov(
    payload: ColetaComprasGovRequest,
    db: DatabaseSession,
) -> ColetaComprasGovResponse:
    try:
        service = ComprasGovService()
        dados, periodo = await service.coletar(
            data_inicial=payload.data_inicial,
            data_final=payload.data_final,
        )
        resultado = salvar_licitacoes_comprasgov(db, dados)
        return ColetaComprasGovResponse(
            recebidas=len(dados),
            criadas=resultado["criadas"],
            atualizadas=resultado["atualizadas"],
            periodo=periodo,
        )
    except ComprasGovServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get("/indicadores/resumo", response_model=IndicadoresResponse)
def indicadores(
    db: DatabaseSession,
    status_licitacao: str | None = Query(default="aberta", alias="status"),
) -> IndicadoresResponse:
    return obter_indicadores(db, status=status_licitacao)


@router.get("/{licitacao_id}", response_model=LicitacaoDetalheResponse)
def detalhar(licitacao_id: int, db: DatabaseSession) -> LicitacaoDetalheResponse:
    licitacao = buscar_licitacao(db, licitacao_id)
    if licitacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licitação não encontrada.",
        )
    return detalhar_licitacao(licitacao)
