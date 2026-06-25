from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import parse_qs, urlparse

from app.utils.datas import hoje_local, parse_date, parse_datetime


def _decimal(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _status_pncp(bruto: dict[str, Any]) -> str:
    situacao = str(bruto.get("situacaoCompraNome") or "").lower()
    encerramento = parse_date(bruto.get("dataEncerramentoProposta"))

    if any(termo in situacao for termo in ("cancel", "anulad", "revogad")):
        return "cancelada"
    if "suspens" in situacao:
        return "suspensa"
    if encerramento and encerramento < hoje_local():
        return "encerrada"
    if encerramento:
        return "aberta"
    return situacao.strip() or "divulgada"


def _link_pncp(bruto: dict[str, Any]) -> str | None:
    if bruto.get("linkSistemaOrigem"):
        return str(bruto["linkSistemaOrigem"])

    orgao = bruto.get("orgaoEntidade") or {}
    cnpj = orgao.get("cnpj")
    ano = bruto.get("anoCompra")
    sequencial = bruto.get("sequencialCompra")
    if cnpj and ano and sequencial:
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"
    return None


def extrair_chave_comprasgov_link(link: str | None) -> str | None:
    if not link or "comprasnet-web" not in link:
        return None
    compra = parse_qs(urlparse(link).query).get("compra", [None])[0]
    return f"comprasgov:{compra}" if compra else None


def normalizar_pncp(bruto: dict[str, Any]) -> dict[str, Any]:
    orgao = bruto.get("orgaoEntidade") or {}
    unidade = bruto.get("unidadeOrgao") or {}
    objeto = bruto.get("objetoCompra")
    fonte_id = (
        bruto.get("numeroControlePNCP")
        or bruto.get("numeroControlePncp")
        or f"{orgao.get('cnpj', 'sem-cnpj')}-{bruto.get('anoCompra', 'sem-ano')}-"
        f"{bruto.get('sequencialCompra', 'sem-sequencial')}"
    )
    modalidade = bruto.get("modalidadeNome")
    titulo = objeto or (
        f"{modalidade or 'Contratação pública'} — "
        f"{orgao.get('razaoSocial') or unidade.get('nomeUnidade') or 'Órgão público'}"
    )

    link_original = _link_pncp(bruto)
    return {
        "fonte": "PNCP",
        "fonte_id": str(fonte_id),
        "chave_origem": extrair_chave_comprasgov_link(link_original),
        "titulo": str(titulo).strip(),
        "objeto": str(objeto).strip() if objeto else None,
        "orgao": orgao.get("razaoSocial") or unidade.get("nomeUnidade"),
        "cnpj_orgao": orgao.get("cnpj"),
        "modalidade": modalidade,
        "status": _status_pncp(bruto),
        "uf": unidade.get("ufSigla"),
        "municipio": unidade.get("municipioNome"),
        "valor_estimado": _decimal(bruto.get("valorTotalEstimado")),
        "data_publicacao": parse_date(bruto.get("dataPublicacaoPncp")),
        "data_abertura": parse_date(bruto.get("dataAberturaProposta")),
        "data_encerramento": parse_date(bruto.get("dataEncerramentoProposta")),
        "data_atualizacao": parse_datetime(
            bruto.get("dataAtualizacaoGlobal") or bruto.get("dataAtualizacao")
        ),
        "link_original": link_original,
        "dados_originais": bruto,
    }
