from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from app.utils.datas import hoje_local, parse_date, parse_datetime

FONTE_COMPRAS_GOV = "Compras.gov.br"

MODALIDADES_COMPRA_DIRETA = {
    6: "Dispensa de Licitação",
    7: "Inexigibilidade de Licitação",
}


def _texto(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return " ".join(str(value).split())


def _decimal(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        if isinstance(value, str):
            value = value.strip()
            if "," in value and "." in value:
                value = value.replace(".", "").replace(",", ".")
            elif "," in value:
                value = value.replace(",", ".")
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _status(texto: Any, data_referencia: date | None) -> str:
    situacao = str(texto or "").lower()
    if any(item in situacao for item in ("cancel", "revog", "anulad")):
        return "cancelada"
    if "suspens" in situacao:
        return "suspensa"
    if any(item in situacao for item in ("encerr", "homolog", "resultado")):
        return "encerrada"
    if data_referencia and data_referencia < hoje_local():
        return "encerrada"
    return "aberta"


def _link(id_compra: str) -> str:
    return (
        "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/"
        f"landing?destino=acompanhamento-compra&compra={id_compra}"
    )


def _dados_uasg(bruto: dict[str, Any]) -> dict[str, Any]:
    dados = bruto.get("_uasg")
    return dados if isinstance(dados, dict) else {}


def normalizar_licitacao_legada(bruto: dict[str, Any]) -> dict[str, Any]:
    uasg = _dados_uasg(bruto)
    id_compra = str(bruto.get("id_compra") or bruto.get("identificador"))
    objeto = _texto(bruto.get("objeto"))
    abertura = parse_date(bruto.get("data_abertura_proposta"))
    modalidade = _texto(bruto.get("nome_modalidade"))

    return {
        "fonte": FONTE_COMPRAS_GOV,
        "fonte_id": f"licitacao:{id_compra}",
        "chave_origem": f"comprasgov:{id_compra}",
        "titulo": objeto or f"{modalidade or 'Licitação'} — UASG {bruto.get('uasg')}",
        "objeto": objeto,
        "orgao": uasg.get("nomeUasg") or f"UASG {bruto.get('uasg')}",
        "cnpj_orgao": uasg.get("cnpjCpfOrgao") or uasg.get("cnpjCpfUasg"),
        "modalidade": modalidade,
        "status": _status(bruto.get("situacao_aviso"), abertura),
        "uf": uasg.get("siglaUf"),
        "municipio": uasg.get("nomeMunicipioIbge"),
        "valor_estimado": _decimal(bruto.get("valor_estimado_total")),
        "data_publicacao": parse_date(bruto.get("data_publicacao")),
        "data_abertura": abertura,
        "data_encerramento": abertura if abertura and abertura < hoje_local() else None,
        "data_atualizacao": parse_datetime(bruto.get("dt_alteracao")),
        "link_original": _link(id_compra),
        "dados_originais": bruto,
    }


def normalizar_compra_direta(bruto: dict[str, Any]) -> dict[str, Any]:
    uasg = _dados_uasg(bruto)
    id_compra = str(bruto.get("idCompra"))
    objeto = _texto(bruto.get("ds_objeto_licitacao"))
    publicacao = parse_date(bruto.get("dtPublicacao"))
    codigo_modalidade = bruto.get("co_modalidade_licitacao")

    return {
        "fonte": FONTE_COMPRAS_GOV,
        "fonte_id": f"compra-direta:{id_compra}",
        "chave_origem": f"comprasgov:{id_compra}",
        "titulo": objeto or f"Compra direta — {bruto.get('no_ausg') or id_compra}",
        "objeto": objeto,
        "orgao": bruto.get("no_ausg") or uasg.get("nomeUasg"),
        "cnpj_orgao": uasg.get("cnpjCpfOrgao") or uasg.get("cnpjCpfUasg"),
        "modalidade": MODALIDADES_COMPRA_DIRETA.get(
            codigo_modalidade, f"Compra direta — modalidade {codigo_modalidade}"
        ),
        "status": "encerrada" if not publicacao or publicacao <= hoje_local() else "divulgada",
        "uf": uasg.get("siglaUf"),
        "municipio": uasg.get("nomeMunicipioIbge"),
        "valor_estimado": _decimal(bruto.get("vr_estimado")),
        "data_publicacao": publicacao,
        "data_abertura": parse_date(bruto.get("dtDeclaracaoDispensa")),
        "data_encerramento": parse_date(bruto.get("dtRatificacao")) or publicacao,
        "data_atualizacao": parse_datetime(bruto.get("dt_alteracao")),
        "link_original": _link(id_compra),
        "dados_originais": bruto,
    }


def normalizar_comprasgov(bruto: dict[str, Any]) -> dict[str, Any]:
    if bruto.get("_tipo_registro") == "compra_direta":
        return normalizar_compra_direta(bruto)
    return normalizar_licitacao_legada(bruto)
