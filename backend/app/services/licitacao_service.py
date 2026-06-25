from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
import re
from typing import Any

from sqlalchemy import Select, func, or_, select, update
from sqlalchemy.orm import Session

from app.models import Licitacao
from app.services.comprasgov_normalizador import normalizar_comprasgov
from app.services.normalizador import normalizar_pncp
from app.services.normalizador import extrair_chave_comprasgov_link
from app.utils.datas import hoje_local


def _aplicar_filtros(
    query: Select,
    *,
    palavra_chave: str | None = None,
    uf: str | None = None,
    municipio: str | None = None,
    modalidade: str | None = None,
    status: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    fonte: str | None = None,
    valor_minimo: Decimal | None = None,
    valor_maximo: Decimal | None = None,
    criado_apos: datetime | None = None,
) -> Select:
    if palavra_chave:
        termo = f"%{palavra_chave.strip()}%"
        query = query.where(
            or_(
                Licitacao.titulo.ilike(termo),
                Licitacao.objeto.ilike(termo),
                Licitacao.orgao.ilike(termo),
            )
        )
    if uf:
        query = query.where(Licitacao.uf == uf.upper())
    if municipio:
        query = query.where(Licitacao.municipio.ilike(f"%{municipio.strip()}%"))
    if modalidade:
        query = query.where(Licitacao.modalidade.ilike(f"%{modalidade.strip()}%"))
    if status:
        query = query.where(Licitacao.status.ilike(status.strip()))
    if data_inicio:
        query = query.where(Licitacao.data_publicacao >= data_inicio)
    if data_fim:
        query = query.where(Licitacao.data_publicacao <= data_fim)
    if valor_minimo is not None:
        query = query.where(Licitacao.valor_estimado >= valor_minimo)
    if valor_maximo is not None:
        query = query.where(Licitacao.valor_estimado <= valor_maximo)
    if fonte:
        fonte_normalizada = fonte.strip()
        if fonte_normalizada.casefold() == "compras.gov.br":
            query = query.where(
                or_(
                    Licitacao.fonte.ilike("Compras.gov.br"),
                    Licitacao.chave_origem.ilike("comprasgov:%"),
                    Licitacao.link_original.ilike("%comprasnet-web%"),
                )
            )
        else:
            query = query.where(Licitacao.fonte.ilike(fonte_normalizada))
    if criado_apos:
        query = query.where(Licitacao.criado_em > criado_apos)
    return query


def listar_licitacoes(
    db: Session,
    *,
    palavra_chave: str | None = None,
    uf: str | None = None,
    municipio: str | None = None,
    modalidade: str | None = None,
    status: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    fonte: str | None = None,
    valor_minimo: Decimal | None = None,
    valor_maximo: Decimal | None = None,
    limite: int = 50,
    offset: int = 0,
    criado_apos: datetime | None = None,
) -> list[Licitacao]:
    query = _aplicar_filtros(
        select(Licitacao),
        palavra_chave=palavra_chave,
        uf=uf,
        municipio=municipio,
        modalidade=modalidade,
        status=status,
        data_inicio=data_inicio,
        data_fim=data_fim,
        fonte=fonte,
        valor_minimo=valor_minimo,
        valor_maximo=valor_maximo,
        criado_apos=criado_apos,
    )

    query = (
        query.order_by(
            Licitacao.data_abertura.desc(),
            Licitacao.data_publicacao.desc(),
            Licitacao.id.desc(),
        )
        .offset(offset)
        .limit(limite)
    )
    return list(db.scalars(query).all())


def contar_licitacoes(
    db: Session,
    *,
    palavra_chave: str | None = None,
    uf: str | None = None,
    municipio: str | None = None,
    modalidade: str | None = None,
    status: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    fonte: str | None = None,
    valor_minimo: Decimal | None = None,
    valor_maximo: Decimal | None = None,
    criado_apos: datetime | None = None,
) -> int:
    query = _aplicar_filtros(
        select(func.count(Licitacao.id)),
        palavra_chave=palavra_chave,
        uf=uf,
        municipio=municipio,
        modalidade=modalidade,
        status=status,
        data_inicio=data_inicio,
        data_fim=data_fim,
        fonte=fonte,
        valor_minimo=valor_minimo,
        valor_maximo=valor_maximo,
        criado_apos=criado_apos,
    )
    return int(db.scalar(query) or 0)


def buscar_licitacao(db: Session, licitacao_id: int) -> Licitacao | None:
    return db.get(Licitacao, licitacao_id)


def _prazo_encerramento(licitacao: Licitacao) -> datetime | None:
    bruto = licitacao.dados_originais or {}
    valor = (
        bruto.get("dataEncerramentoProposta")
        or bruto.get("data_encerramento_proposta")
        or bruto.get("dt_fim_proposta")
    )
    if valor:
        try:
            prazo = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
            if prazo.tzinfo is None:
                prazo = prazo.replace(tzinfo=timezone(timedelta(hours=-3)))
            return prazo
        except ValueError:
            pass
    if licitacao.data_encerramento:
        return datetime.combine(
            licitacao.data_encerramento,
            time(23, 59, 59),
            tzinfo=timezone(timedelta(hours=-3)),
        )
    return None


def _extrair_documentos(licitacao: Licitacao) -> list[dict[str, str]]:
    bruto = licitacao.dados_originais or {}
    candidatos = [
        ("Portal oficial", licitacao.link_original, "portal"),
        ("Processo eletrônico", bruto.get("linkProcessoEletronico"), "processo"),
    ]
    complemento = str(bruto.get("informacaoComplementar") or "")
    for indice, url in enumerate(re.findall(r"https?://[^\s,;]+", complemento), 1):
        candidatos.append(
            (f"Link complementar {indice}", url.rstrip(".)"), "complementar")
        )

    documentos: list[dict[str, str]] = []
    urls_vistas: set[str] = set()
    for titulo, url, tipo in candidatos:
        if not url:
            continue
        url_texto = str(url)
        if url_texto in urls_vistas:
            continue
        urls_vistas.add(url_texto)
        documentos.append({"titulo": titulo, "url": url_texto, "tipo": tipo})
    return documentos


def gerar_resumo_automatico(licitacao: Licitacao) -> dict[str, Any]:
    local = " / ".join(
        parte for parte in (licitacao.municipio, licitacao.uf) if parte
    )
    valor_formatado = None
    if licitacao.valor_estimado is not None:
        valor_formatado = f"{licitacao.valor_estimado:,.2f}"
        valor_formatado = (
            valor_formatado.replace(",", "_").replace(".", ",").replace("_", ".")
        )

    pontos_chave = [
        item
        for item in (
            f"Órgão responsável: {licitacao.orgao}" if licitacao.orgao else None,
            f"Modalidade: {licitacao.modalidade}" if licitacao.modalidade else None,
            f"Local: {local}" if local else None,
            (
                f"Valor estimado: R$ {valor_formatado}" if valor_formatado else None
            ),
            (
                f"Prazo para propostas: {licitacao.data_encerramento:%d/%m/%Y}"
                if licitacao.data_encerramento
                else None
            ),
        )
        if item
    ]

    pontos_atencao: list[str] = []
    if licitacao.valor_estimado is None:
        pontos_atencao.append("O valor estimado não foi informado na publicação.")
    if not licitacao.data_encerramento:
        pontos_atencao.append("O prazo final não foi informado na fonte consultada.")
    if licitacao.status and licitacao.status.casefold() != "aberta":
        pontos_atencao.append(f"A situação atual registrada é “{licitacao.status}”.")
    if not licitacao.link_original:
        pontos_atencao.append("Não há link oficial disponível neste registro.")
    if not pontos_atencao:
        pontos_atencao.append(
            "Confirme habilitação, anexos e condições diretamente no edital oficial."
        )

    objeto = licitacao.objeto or licitacao.titulo
    texto = " ".join(objeto.split())
    if len(texto) > 420:
        texto = f"{texto[:417].rstrip()}..."

    return {
        "texto": texto,
        "pontos_chave": pontos_chave,
        "pontos_atencao": pontos_atencao,
    }


def detalhar_licitacao(licitacao: Licitacao) -> dict[str, Any]:
    dados = {
        coluna.name: getattr(licitacao, coluna.name)
        for coluna in Licitacao.__table__.columns
        if coluna.name != "chave_origem"
    }
    dados["prazo_encerramento"] = _prazo_encerramento(licitacao)
    dados["documentos"] = _extrair_documentos(licitacao)
    dados["resumo_automatico"] = gerar_resumo_automatico(licitacao)
    return dados


def obter_indicadores(db: Session, status: str | None = "aberta") -> dict[str, Any]:
    filtros = []
    if status and status.casefold() != "todos":
        filtros.append(Licitacao.status.ilike(status.strip()))

    total = int(db.scalar(select(func.count(Licitacao.id)).where(*filtros)) or 0)
    total_abertas = int(
        db.scalar(
            select(func.count(Licitacao.id)).where(
                Licitacao.status.ilike("aberta")
            )
        )
        or 0
    )
    total_com_valor = int(
        db.scalar(
            select(func.count(Licitacao.id)).where(
                *filtros, Licitacao.valor_estimado.is_not(None)
            )
        )
        or 0
    )
    total_com_prazo = int(
        db.scalar(
            select(func.count(Licitacao.id)).where(
                *filtros, Licitacao.data_encerramento.is_not(None)
            )
        )
        or 0
    )
    valor_total = db.scalar(
        select(func.coalesce(func.sum(Licitacao.valor_estimado), 0)).where(*filtros)
    ) or Decimal("0")
    valor_medio = db.scalar(
        select(func.coalesce(func.avg(Licitacao.valor_estimado), 0)).where(*filtros)
    ) or Decimal("0")
    valor_mediano = db.scalar(
        select(
            func.percentile_cont(0.5).within_group(Licitacao.valor_estimado)
        ).where(*filtros, Licitacao.valor_estimado.is_not(None))
    ) or Decimal("0")
    hoje = hoje_local()
    publicadas_30_dias = int(
        db.scalar(
            select(func.count(Licitacao.id)).where(
                *filtros,
                Licitacao.data_publicacao >= hoje - timedelta(days=29),
                Licitacao.data_publicacao <= hoje,
            )
        )
        or 0
    )
    publicadas_30_dias_anteriores = int(
        db.scalar(
            select(func.count(Licitacao.id)).where(
                *filtros,
                Licitacao.data_publicacao >= hoje - timedelta(days=59),
                Licitacao.data_publicacao <= hoje - timedelta(days=30),
            )
        )
        or 0
    )
    variacao_publicacoes = None
    if publicadas_30_dias_anteriores:
        variacao_publicacoes = (
            Decimal(publicadas_30_dias - publicadas_30_dias_anteriores)
            * Decimal("100")
            / Decimal(publicadas_30_dias_anteriores)
        ).quantize(Decimal("0.1"))
    encerram_7_dias = int(
        db.scalar(
            select(func.count(Licitacao.id)).where(
                Licitacao.status.ilike("aberta"),
                Licitacao.data_encerramento >= hoje,
                Licitacao.data_encerramento <= hoje + timedelta(days=7),
            )
        )
        or 0
    )
    encerram_30_dias = int(
        db.scalar(
            select(func.count(Licitacao.id)).where(
                Licitacao.status.ilike("aberta"),
                Licitacao.data_encerramento >= hoje,
                Licitacao.data_encerramento <= hoje + timedelta(days=30),
            )
        )
        or 0
    )
    periodo_base = db.execute(
        select(
            func.min(Licitacao.data_publicacao),
            func.max(Licitacao.data_publicacao),
            func.max(Licitacao.atualizado_em),
        ).where(*filtros)
    ).one()

    def agrupar(campo: Any, limite: int) -> list[dict[str, Any]]:
        linhas = db.execute(
            select(
                campo,
                func.count(Licitacao.id),
                func.coalesce(func.sum(Licitacao.valor_estimado), 0),
            )
            .where(*filtros, campo.is_not(None), campo != "")
            .group_by(campo)
            .order_by(func.count(Licitacao.id).desc())
            .limit(limite)
        ).all()
        return [
            {
                "nome": str(nome),
                "quantidade": int(quantidade),
                "valor_estimado": valor or Decimal("0"),
            }
            for nome, quantidade, valor in linhas
        ]

    inicio_historico = date(hoje.year - 1, hoje.month, 1)
    publicacoes = db.execute(
        select(Licitacao.data_publicacao, Licitacao.valor_estimado).where(
            *filtros,
            Licitacao.data_publicacao >= inicio_historico,
        )
    ).all()
    meses: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"quantidade": 0, "valor_estimado": Decimal("0")}
    )
    for data_publicacao, valor in publicacoes:
        periodo = data_publicacao.strftime("%Y-%m")
        meses[periodo]["quantidade"] += 1
        meses[periodo]["valor_estimado"] += valor or Decimal("0")

    return {
        "total": total,
        "total_abertas": total_abertas,
        "total_com_valor": total_com_valor,
        "valor_total_estimado": valor_total,
        "valor_medio_estimado": valor_medio,
        "valor_mediano_estimado": valor_mediano,
        "publicadas_ultimos_30_dias": publicadas_30_dias,
        "publicadas_30_dias_anteriores": publicadas_30_dias_anteriores,
        "variacao_publicacoes_30_dias": variacao_publicacoes,
        "encerram_em_7_dias": encerram_7_dias,
        "encerram_em_30_dias": encerram_30_dias,
        "percentual_com_valor": (
            Decimal(total_com_valor) * Decimal("100") / Decimal(total)
            if total
            else Decimal("0")
        ),
        "percentual_com_prazo": (
            Decimal(total_com_prazo) * Decimal("100") / Decimal(total)
            if total
            else Decimal("0")
        ),
        "data_inicial_base": periodo_base[0],
        "data_final_base": periodo_base[1],
        "ultima_atualizacao": periodo_base[2],
        "por_uf": agrupar(Licitacao.uf, 10),
        "por_modalidade": agrupar(Licitacao.modalidade, 8),
        "principais_orgaos": agrupar(Licitacao.orgao, 10),
        "por_fonte": agrupar(Licitacao.fonte, 5),
        "por_status": agrupar(Licitacao.status, 8),
        "evolucao_mensal": [
            {"periodo": periodo, **valores}
            for periodo, valores in sorted(meses.items())[-12:]
        ],
    }


def atualizar_status_encerradas(db: Session, referencia: date | None = None) -> int:
    hoje = referencia or hoje_local()
    resultado = db.execute(
        update(Licitacao)
        .where(
            Licitacao.status == "aberta",
            Licitacao.data_encerramento.is_not(None),
            Licitacao.data_encerramento < hoje,
        )
        .values(status="encerrada")
    )
    db.commit()
    return int(resultado.rowcount or 0)


def salvar_licitacoes_pncp(
    db: Session, dados_brutos: list[dict[str, Any]]
) -> dict[str, int]:
    return salvar_licitacoes_normalizadas(
        db, [normalizar_pncp(bruto) for bruto in dados_brutos]
    )


def salvar_licitacoes_comprasgov(
    db: Session,
    dados_brutos: list[dict[str, Any]],
    *,
    somente_abertas: bool = False,
) -> dict[str, int]:
    normalizados = [normalizar_comprasgov(bruto) for bruto in dados_brutos]
    if somente_abertas:
        normalizados = [
            item for item in normalizados if item.get("status") == "aberta"
        ]
    return salvar_licitacoes_normalizadas(
        db, normalizados
    )


def salvar_licitacoes_normalizadas(
    db: Session, normalizados: list[dict[str, Any]]
) -> dict[str, int]:
    unicos = {
        (normalizado["fonte"], normalizado["fonte_id"]): normalizado
        for normalizado in normalizados
    }
    normalizados = list(unicos.values())
    ids_por_fonte: dict[str, list[str]] = {}
    chaves = [
        str(item["chave_origem"])
        for item in normalizados
        if item.get("chave_origem")
    ]
    for item in normalizados:
        ids_por_fonte.setdefault(item["fonte"], []).append(item["fonte_id"])

    existentes_por_id: dict[str, Licitacao] = {}

    for fonte, ids in ids_por_fonte.items():
        for inicio in range(0, len(ids), 1000):
            lote_ids = ids[inicio : inicio + 1000]
            existentes = db.scalars(
                select(Licitacao).where(
                    Licitacao.fonte == fonte,
                    Licitacao.fonte_id.in_(lote_ids),
                )
            ).all()
            existentes_por_id.update(
                {
                    f"{licitacao.fonte}:{licitacao.fonte_id}": licitacao
                    for licitacao in existentes
                }
            )

    existentes_por_chave: dict[str, Licitacao] = {}
    for inicio in range(0, len(chaves), 1000):
        lote_chaves = chaves[inicio : inicio + 1000]
        existentes = db.scalars(
            select(Licitacao).where(Licitacao.chave_origem.in_(lote_chaves))
        ).all()
        existentes_por_chave.update(
            {
                str(licitacao.chave_origem): licitacao
                for licitacao in existentes
                if licitacao.chave_origem
            }
        )

    if any(chave.startswith("comprasgov:") for chave in chaves):
        candidatos = db.scalars(
            select(Licitacao).where(
                Licitacao.chave_origem.is_(None),
                Licitacao.link_original.ilike("%comprasnet-web%compra=%"),
            )
        ).all()
        for licitacao in candidatos:
            chave = extrair_chave_comprasgov_link(licitacao.link_original)
            if chave:
                licitacao.chave_origem = chave
                existentes_por_chave[chave] = licitacao

    criadas = 0
    atualizadas = 0

    for normalizado in normalizados:
        chave_id = f"{normalizado['fonte']}:{normalizado['fonte_id']}"
        existente = existentes_por_id.get(chave_id)
        if existente is None and normalizado.get("chave_origem"):
            existente = existentes_por_chave.get(normalizado["chave_origem"])

        if existente:
            if existente.fonte == normalizado["fonte"]:
                for campo, valor in normalizado.items():
                    setattr(existente, campo, valor)
            else:
                originais = dict(existente.dados_originais or {})
                complementares = dict(originais.get("fontes_complementares") or {})
                complementares[normalizado["fonte"]] = normalizado["dados_originais"]
                originais["fontes_complementares"] = complementares
                existente.dados_originais = originais
                if not existente.chave_origem:
                    existente.chave_origem = normalizado.get("chave_origem")
            atualizadas += 1
        else:
            db.add(Licitacao(**normalizado))
            criadas += 1

    db.commit()
    return {"criadas": criadas, "atualizadas": atualizadas}
