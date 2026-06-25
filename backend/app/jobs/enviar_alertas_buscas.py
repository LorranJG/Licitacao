import asyncio
import html
import logging
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import SessionLocal
from app.models import AlertaBusca, BuscaSalva
from app.services.email_service import enviar_email
from app.services.licitacao_service import listar_licitacoes
from app.services.telegram_service import enviar_mensagem

logger = logging.getLogger("radar.alertas_buscas")
settings = get_settings()


async def processar_busca(busca_id: int) -> int:
    with SessionLocal() as db:
        busca = db.scalar(
            select(BuscaSalva)
            .options(selectinload(BuscaSalva.usuario))
            .where(BuscaSalva.id == busca_id)
        )
        if busca is None or not busca.alertas_ativos or not busca.usuario.ativo:
            return 0
        desde = busca.ultima_verificacao_em or busca.criado_em
        filtros = {
            chave: valor
            for chave, valor in (busca.filtros or {}).items()
            if valor not in (None, "", "todos")
        }
        for chave in ("valor_minimo", "valor_maximo"):
            if filtros.get(chave):
                filtros[chave] = Decimal(str(filtros[chave]))
        novas = listar_licitacoes(
            db,
            **filtros,
            criado_apos=desde,
            limite=10,
        )
        busca.ultima_verificacao_em = datetime.now(timezone.utc)
        ineditas = []
        for licitacao in novas:
            existe = db.scalar(
                select(AlertaBusca.id).where(
                    AlertaBusca.busca_id == busca.id,
                    AlertaBusca.licitacao_id == licitacao.id,
                )
            )
            if not existe:
                ineditas.append(licitacao)
        if not ineditas:
            db.commit()
            return 0

        linhas = [
            f"<b>{html.escape(busca.nome)}</b>",
            f"{len(ineditas)} nova(s) oportunidade(s):",
        ]
        botoes = []
        for licitacao in ineditas:
            linhas.append(f"\n• {html.escape(licitacao.titulo[:130])}")
            botoes.append(
                [
                    {
                        "text": f"Ver #{licitacao.id}",
                        "url": f"{settings.app_public_url}/licitacoes/{licitacao.id}",
                    }
                ]
            )
        texto = "\n".join(linhas)
        enviado = False
        erro = None
        try:
            if busca.usuario.telegram_chat_id:
                await enviar_mensagem(
                    busca.usuario.telegram_chat_id, texto, botoes=botoes
                )
                enviado = True
            if settings.resend_api_key and busca.usuario.email_verificado_em:
                links = "".join(
                    f"<li><a href='{settings.app_public_url}/licitacoes/{item.id}'>"
                    f"{html.escape(item.titulo)}</a></li>"
                    for item in ineditas
                )
                enviar_email(
                    destinatario=busca.usuario.email,
                    assunto=f"Novas oportunidades: {busca.nome}",
                    html=f"<p>Encontramos novas oportunidades.</p><ul>{links}</ul>",
                )
                enviado = True
        except Exception as exc:
            erro = str(exc)[:1000]
            logger.exception("Falha ao enviar alerta da busca %s.", busca.id)

        agora = datetime.now(timezone.utc) if enviado else None
        for licitacao in ineditas:
            db.add(
                AlertaBusca(
                    busca_id=busca.id,
                    licitacao_id=licitacao.id,
                    enviado_em=agora,
                    erro_envio=erro or (None if enviado else "Nenhum canal configurado."),
                )
            )
        db.commit()
        return len(ineditas)


async def executar_ciclo() -> int:
    with SessionLocal() as db:
        ids = list(
            db.scalars(
                select(BuscaSalva.id).where(BuscaSalva.alertas_ativos.is_(True))
            ).all()
        )
    total = 0
    for busca_id in ids:
        total += await processar_busca(busca_id)
    return total


async def worker() -> None:
    logging.basicConfig(level=logging.INFO)
    while True:
        try:
            total = await executar_ciclo()
            if total:
                logger.info("%s correspondências processadas.", total)
        except Exception:
            logger.exception("Falha no ciclo de buscas salvas.")
        await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(worker())
