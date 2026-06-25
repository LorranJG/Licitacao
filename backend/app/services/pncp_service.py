import logging
import asyncio
from datetime import date, timedelta
from typing import Any

import httpx

from app.config import get_settings
from app.services.http_client import async_client
from app.utils.datas import hoje_local

logger = logging.getLogger(__name__)


class PNCPServiceError(RuntimeError):
    pass


class PNCPService:
    """Cliente da API pública de consultas do PNCP.

    A API exige uma modalidade por chamada no endpoint de publicação. Por isso,
    quando nenhuma modalidade é informada, o serviço percorre os códigos
    configurados em PNCP_MODALIDADES.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.pncp_base_url.rstrip("/")
        self.modalidades = settings.pncp_modalidades
        self.max_pages = settings.pncp_max_pages
        self.open_max_pages = settings.pncp_open_max_pages
        self.request_delay = settings.pncp_request_delay_seconds

    async def coletar_contratacoes(
        self,
        *,
        data_inicial: date | None = None,
        data_final: date | None = None,
        modalidade_codigo: int | None = None,
    ) -> tuple[list[dict[str, Any]], str]:
        fim = data_final or hoje_local()
        inicio = data_inicial or (fim - timedelta(days=1))
        if inicio > fim:
            raise PNCPServiceError("A data inicial não pode ser posterior à final.")

        return await self._coletar_por_endpoint(
            endpoint_nome="publicacao",
            data_inicial=inicio,
            data_final=fim,
            modalidade_codigo=modalidade_codigo,
        )

    async def coletar_atualizacoes(
        self,
        *,
        data_inicial: date | None = None,
        data_final: date | None = None,
        modalidade_codigo: int | None = None,
    ) -> tuple[list[dict[str, Any]], str]:
        fim = data_final or hoje_local()
        inicio = data_inicial or fim
        if inicio > fim:
            raise PNCPServiceError("A data inicial não pode ser posterior à final.")

        return await self._coletar_por_endpoint(
            endpoint_nome="atualizacao",
            data_inicial=inicio,
            data_final=fim,
            modalidade_codigo=modalidade_codigo,
        )

    async def coletar_abertas(
        self,
        *,
        data_final: date,
        modalidade_codigo: int | None = None,
    ) -> tuple[list[dict[str, Any]], str]:
        modalidades = [modalidade_codigo] if modalidade_codigo else self.modalidades
        todas: list[dict[str, Any]] = []
        falhas: list[str] = []

        timeout = httpx.Timeout(30.0, connect=10.0)
        headers = {"Accept": "application/json", "User-Agent": "RadarLicitacoes/0.2"}
        async with async_client(timeout=timeout, headers=headers) as client:
            for modalidade in modalidades:
                try:
                    todas.extend(
                        await self._coletar_modalidade_aberta(
                            client,
                            data_final=data_final,
                            modalidade=modalidade,
                        )
                    )
                except PNCPServiceError as exc:
                    falhas.append(f"modalidade {modalidade}: {exc}")
                    logger.warning("Falha parcial no PNCP: %s", falhas[-1])

        if not todas and falhas and len(falhas) == len(modalidades):
            raise PNCPServiceError(
                "Não foi possível consultar propostas abertas. "
                + "; ".join(falhas[:3])
            )
        return todas, f"abertas até {data_final.isoformat()}"

    async def _coletar_por_endpoint(
        self,
        *,
        endpoint_nome: str,
        data_inicial: date,
        data_final: date,
        modalidade_codigo: int | None,
    ) -> tuple[list[dict[str, Any]], str]:
        modalidades = [modalidade_codigo] if modalidade_codigo else self.modalidades
        todas: list[dict[str, Any]] = []
        chamadas_bem_sucedidas = 0
        falhas: list[str] = []

        timeout = httpx.Timeout(30.0, connect=10.0)
        headers = {"Accept": "application/json", "User-Agent": "RadarLicitacoes/0.1"}

        async with async_client(timeout=timeout, headers=headers) as client:
            for modalidade in modalidades:
                try:
                    itens = await self._coletar_modalidade(
                        client,
                        inicio=data_inicial,
                        fim=data_final,
                        modalidade=modalidade,
                        endpoint_nome=endpoint_nome,
                    )
                    todas.extend(itens)
                    chamadas_bem_sucedidas += 1
                except PNCPServiceError as exc:
                    falhas.append(f"modalidade {modalidade}: {exc}")
                    logger.warning("Falha parcial no PNCP: %s", falhas[-1])

        if chamadas_bem_sucedidas == 0 and falhas:
            raise PNCPServiceError(
                "Não foi possível consultar o PNCP. " + "; ".join(falhas[:3])
            )

        periodo = f"{data_inicial.isoformat()} a {data_final.isoformat()}"
        return todas, periodo

    async def _coletar_modalidade(
        self,
        client: httpx.AsyncClient,
        *,
        inicio: date,
        fim: date,
        modalidade: int,
        endpoint_nome: str,
    ) -> list[dict[str, Any]]:
        endpoint = f"{self.base_url}/v1/contratacoes/{endpoint_nome}"
        pagina = 1
        resultados: list[dict[str, Any]] = []

        while pagina <= self.max_pages:
            params = {
                "dataInicial": inicio.strftime("%Y%m%d"),
                "dataFinal": fim.strftime("%Y%m%d"),
                "codigoModalidadeContratacao": modalidade,
                "pagina": pagina,
                "tamanhoPagina": 50,
            }
            payload = await self._obter_pagina(client, endpoint, params)
            if payload is None:
                break

            dados = payload.get("data", [])
            if not isinstance(dados, list):
                raise PNCPServiceError("resposta inesperada da API.")
            resultados.extend(dados)

            total_paginas = int(payload.get("totalPaginas") or 1)
            if pagina >= total_paginas or not dados:
                break
            pagina += 1

        return resultados

    async def _coletar_modalidade_aberta(
        self,
        client: httpx.AsyncClient,
        *,
        data_final: date,
        modalidade: int,
    ) -> list[dict[str, Any]]:
        endpoint = f"{self.base_url}/v1/contratacoes/proposta"
        pagina = 1
        resultados: list[dict[str, Any]] = []

        while pagina <= self.open_max_pages:
            params = {
                "dataFinal": data_final.strftime("%Y%m%d"),
                "codigoModalidadeContratacao": modalidade,
                "pagina": pagina,
                "tamanhoPagina": 50,
            }
            payload = await self._obter_pagina(client, endpoint, params)
            if payload is None:
                break
            dados = payload.get("data", [])
            if not isinstance(dados, list):
                raise PNCPServiceError("resposta inesperada da API.")
            resultados.extend(dados)

            total_paginas = int(payload.get("totalPaginas") or 1)
            if pagina >= total_paginas or not dados:
                break
            pagina += 1

        return resultados

    async def _obter_pagina(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        params: dict[str, Any],
    ) -> dict[str, Any] | None:
        ultimo_erro: Exception | None = None
        for tentativa in range(1, 4):
            try:
                response = await client.get(endpoint, params=params)
                if response.status_code == 429:
                    ultimo_erro = RuntimeError("limite de requisições do PNCP")
                    retry_after = response.headers.get("Retry-After")
                    espera = (
                        float(retry_after)
                        if retry_after and retry_after.isdigit()
                        else 10.0 * tentativa
                    )
                    logger.warning(
                        "PNCP limitou requisições; nova tentativa em %.1fs.", espera
                    )
                    await asyncio.sleep(espera)
                    continue
                if response.status_code == 204:
                    await asyncio.sleep(self.request_delay)
                    return None
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

        raise PNCPServiceError(f"erro de comunicação: {ultimo_erro}")
