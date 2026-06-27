import type {
  Indicadores,
  Licitacao,
  LicitacaoDetalhe,
  LicitacaoFilters,
  LicitacaoPagination,
  StatusDados,
} from "@/types/licitacao";

type ApiResult = {
  data: Licitacao[];
  total: number;
  error: string | null;
};

type DetailResult = {
  data: LicitacaoDetalhe | null;
  error: string | null;
  notFound: boolean;
};

type IndicatorsResult = {
  data: Indicadores | null;
  error: string | null;
};

function apiBaseUrl(): string {
  return (
    process.env.API_INTERNAL_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

export async function getLicitacoes(
  filters: LicitacaoFilters,
  pagination: LicitacaoPagination,
  token?: string | null,
): Promise<ApiResult> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value && !(key === "status" && value === "todos")) {
      params.set(key, value);
    }
  });
  params.set("limite", String(pagination.pageSize));
  params.set("offset", String((pagination.page - 1) * pagination.pageSize));

  try {
    const response = await fetch(
      `${apiBaseUrl()}/licitacoes?${params.toString()}`,
      {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        cache: "no-store",
        signal: AbortSignal.timeout(8000),
      },
    );
    if (!response.ok) {
      throw new Error(`A API retornou o status ${response.status}.`);
    }
    const total = Number(response.headers.get("X-Total-Count") ?? 0);
    return {
      data: (await response.json()) as Licitacao[],
      total: Number.isFinite(total) ? total : 0,
      error: null,
    };
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Falha desconhecida na consulta.";
    return { data: [], total: 0, error: message };
  }
}

export async function getLicitacao(
  id: number,
  token?: string | null,
): Promise<DetailResult> {
  try {
    const response = await fetch(`${apiBaseUrl()}/licitacoes/${id}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      cache: "no-store",
      signal: AbortSignal.timeout(8000),
    });
    if (response.status === 404) {
      return { data: null, error: null, notFound: true };
    }
    if (!response.ok) {
      throw new Error(`A API retornou o status ${response.status}.`);
    }
    return {
      data: (await response.json()) as LicitacaoDetalhe,
      error: null,
      notFound: false,
    };
  } catch (error) {
    return {
      data: null,
      error:
        error instanceof Error
          ? error.message
          : "Falha desconhecida na consulta.",
      notFound: false,
    };
  }
}

export async function getIndicadores(
  status = "aberta",
  token?: string | null,
): Promise<IndicatorsResult> {
  try {
    const params = new URLSearchParams({ status });
    const response = await fetch(
      `${apiBaseUrl()}/licitacoes/indicadores/resumo?${params.toString()}`,
      {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        next: { revalidate: 300 },
        signal: AbortSignal.timeout(12000),
      },
    );
    if (!response.ok) {
      throw new Error(`A API retornou o status ${response.status}.`);
    }
    return {
      data: (await response.json()) as Indicadores,
      error: null,
    };
  } catch (error) {
    return {
      data: null,
      error:
        error instanceof Error
          ? error.message
          : "Falha desconhecida na consulta.",
    };
  }
}

export async function getStatusDados(): Promise<StatusDados | null> {
  try {
    const response = await fetch(`${apiBaseUrl()}/status-dados`, {
      cache: "no-store",
      signal: AbortSignal.timeout(8000),
    });
    return response.ok ? ((await response.json()) as StatusDados) : null;
  } catch {
    return null;
  }
}
