import asyncio
import logging
from datetime import date, timedelta
from typing import Any

import httpx

from app.config import get_settings
from app.services.http_client import async_client
from app.utils.datas import hoje_local

logger = logging.getLogger(__name__)


class ComprasGovServiceError(RuntimeError):
    pass


class ComprasGovService:
    """Cliente da API oficial de Dados Abertos do Compras.gov.br.

    São consultados os módulos legados com `pertence14133=false`, pois as
    contratações da Lei 14.133 já chegam pelo PNCP e seriam duplicadas.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.compras_gov_base_url.rstrip("/")
        self.max_pages = settings.compras_gov_max_pages
        self.request_delay = settings.compras_gov_request_delay_seconds
        self.uasg_limit = settings.compras_gov_uasg_enrichment_limit
        self._uasg_cache: dict[str, dict[str, Any]] = {}

    async def coletar(
        self,
        *,
        data_inicial: date | None = None,
        data_final: date | None = None,
    ) -> tuple[list[dict[str, Any]], str]:
        fim = data_final or hoje_local()
        inicio = data_inicial or (fim - timedelta(days=6))
        if inicio > fim:
            raise ComprasGovServiceError(
                "A data inicial não pode ser posterior à final."
            )

        timeout = httpx.Timeout(60.0, connect=15.0)
        headers = {"Accept": "application/json", "User-Agent": "RadarLicitacoes/0.2"}
        async with async_client(timeout=timeout, headers=headers) as client:
            licitacoes = await self._coletar_licitacoes(client, inicio, fim)
            compras_diretas = await self._coletar_compras_diretas(
                client, inicio, fim
            )
            dados = licitacoes + compras_diretas
            await self._enriquecer_uasgs(client, dados)

        return dados, f"{inicio.isoformat()} a {fim.isoformat()}"

    async def _coletar_licitacoes(
        self,
        client: httpx.AsyncClient,
        inicio: date,
        fim: date,
    ) -> list[dict[str, Any]]:
        params = {
            "data_publicacao_inicial": inicio.isoformat(),
            "data_publicacao_final": fim.isoformat(),
            "pertence14133": "false",
        }
        dados = await self._paginar(
            client,
            "/modulo-legado/1_consultarLicitacao",
            params,
        )
        for item in dados:
            item["_tipo_registro"] = "licitacao"
        return dados

    async def _coletar_compras_diretas(
        self,
        client: httpx.AsyncClient,
        inicio: date,
        fim: date,
    ) -> list[dict[str, Any]]:
        resultados: list[dict[str, Any]] = []
        dia = inicio
        while dia <= fim:
            params = {
                "dt_ano_aviso": dia.year,
                "dtPublicacao": dia.isoformat(),
                "pertence14133": "false",
            }
            dados = await self._paginar(
                client,
                "/modulo-legado/5_consultarComprasSemLicitacao",
                params,
            )
            for item in dados:
                item["_tipo_registro"] = "compra_direta"
            resultados.extend(dados)
            dia += timedelta(days=1)
        return resultados

    async def _paginar(
        self,
        client: httpx.AsyncClient,
        caminho: str,
        params_base: dict[str, Any],
    ) -> list[dict[str, Any]]:
        pagina = 1
        resultados: list[dict[str, Any]] = []

        while pagina <= self.max_pages:
            params = {**params_base, "pagina": pagina, "tamanhoPagina": 500}
            payload = await self._get_json(client, f"{self.base_url}{caminho}", params)
            dados = payload.get("resultado") or []
            if not isinstance(dados, list):
                raise ComprasGovServiceError("Resposta inesperada da API.")
            resultados.extend(item for item in dados if isinstance(item, dict))

            total_paginas = int(payload.get("totalPaginas") or 0)
            if pagina >= total_paginas or not dados:
                break
            pagina += 1

        return resultados

    async def _enriquecer_uasgs(
        self,
        client: httpx.AsyncClient,
        dados: list[dict[str, Any]],
    ) -> None:
        codigos = []
        for item in dados:
            codigo = item.get("uasg") or item.get("co_uasg")
            if codigo and str(codigo) not in codigos:
                codigos.append(str(codigo))

        for codigo in codigos[: self.uasg_limit]:
            item_uasg = await self._consultar_uasg(client, codigo)
            if item_uasg:
                for item in dados:
                    if str(item.get("uasg") or item.get("co_uasg") or "") == codigo:
                        item["_uasg"] = item_uasg

    async def _consultar_uasg(
        self,
        client: httpx.AsyncClient,
        codigo: str,
    ) -> dict[str, Any] | None:
        if codigo in self._uasg_cache:
            return self._uasg_cache[codigo]

        payload = await self._get_json(
            client,
            f"{self.base_url}/modulo-uasg/1_consultarUasg",
            {"pagina": 1, "codigoUasg": codigo, "statusUasg": "true"},
        )
        resultado = payload.get("resultado") or []
        uasg = resultado[0] if resultado else None
        if isinstance(uasg, dict):
            self._uasg_cache[codigo] = uasg
            return uasg
        return None

    async def _get_json(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        ultimo_erro: Exception | None = None
        for tentativa in range(1, 4):
            try:
                response = await client.get(url, params=params)
                if response.status_code == 429:
                    await asyncio.sleep(10 * tentativa)
                    continue
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError("resposta não é um objeto JSON")
                await asyncio.sleep(self.request_delay)
                return payload
            except (httpx.HTTPError, ValueError) as exc:
                ultimo_erro = exc
                if tentativa < 3:
                    await asyncio.sleep(2 ** (tentativa - 1))

        raise ComprasGovServiceError(f"Erro de comunicação: {ultimo_erro}")
