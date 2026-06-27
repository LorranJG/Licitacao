import { FileSearch2 } from "lucide-react";
import { redirect } from "next/navigation";

import { AutoRefresh } from "@/components/AutoRefresh";
import { LicitacaoCard } from "@/components/LicitacaoCard";
import { LicitacaoFilters } from "@/components/LicitacaoFilters";
import { Pagination } from "@/components/Pagination";
import { SaveSearchButton } from "@/components/SaveSearchButton";
import { getLicitacoes, getStatusDados } from "@/lib/api";
import { getCurrentUser, sessionToken } from "@/lib/session";

export const metadata = {
  title: "Licitações",
};

type LicitacoesPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

function first(value: string | string[] | undefined): string {
  return Array.isArray(value) ? value[0] ?? "" : value ?? "";
}

function positiveInteger(value: string, fallback: number): number {
  const parsed = Number.parseInt(value, 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback;
}

export default async function LicitacoesPage({
  searchParams,
}: LicitacoesPageProps) {
  const rawParams = await searchParams;
  const filters = {
    palavra_chave: first(rawParams.palavra_chave),
    uf: first(rawParams.uf),
    modalidade: first(rawParams.modalidade),
    status:
      rawParams.status === undefined ? "aberta" : first(rawParams.status),
    data_inicio: first(rawParams.data_inicio),
    data_fim: first(rawParams.data_fim),
    encerramento_inicio: first(rawParams.encerramento_inicio),
    encerramento_fim: first(rawParams.encerramento_fim),
    fonte: first(rawParams.fonte),
    valor_minimo: first(rawParams.valor_minimo),
    valor_maximo: first(rawParams.valor_maximo),
  };
  const page = positiveInteger(first(rawParams.pagina), 1);
  const pageSize = 20;
  const token = await sessionToken();
  if (!token) redirect("/login");
  const usuario = await getCurrentUser();
  if (!usuario) redirect("/login");
  if (!usuario.acesso_liberado) redirect("/comprar");
  const [result, statusDados] = await Promise.all([
    getLicitacoes(filters, { page, pageSize }, token),
    getStatusDados(),
  ]);
  const totalPages = Math.max(1, Math.ceil(result.total / pageSize));
  const firstResult = result.total === 0 ? 0 : (page - 1) * pageSize + 1;
  const lastResult = Math.min(page * pageSize, result.total);

  return (
    <main className="pb-20">
      <section className="border-b border-slate-200 bg-white">
        <div className="container-page py-12 sm:py-16">
          <p className="text-sm font-bold uppercase tracking-[0.16em] text-navy-600">
            Radar de oportunidades
          </p>
          <div className="mt-3 flex flex-col justify-between gap-5 md:flex-row md:items-end">
            <div>
              <h1 className="text-4xl font-bold tracking-tight text-navy-950 sm:text-5xl">
                Licitações públicas
              </h1>
              <p className="mt-3 max-w-2xl text-lg leading-8 text-slate-600">
                Consulte oportunidades compiladas de fontes públicas e acesse
                o portal oficial para participar.
              </p>
            </div>
            <div className="space-y-2 text-left md:text-right">
              <p className="font-mono text-sm font-semibold text-slate-500">
                {result.total} resultado{result.total === 1 ? "" : "s"}
              </p>
              <AutoRefresh />
            </div>
          </div>
        </div>
      </section>

      <div className="container-page pt-8">
        <LicitacaoFilters values={filters} />
        <SaveSearchButton filters={filters} authenticated={Boolean(usuario)} />

        {statusDados ? (
          <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-2 rounded-xl bg-slate-100 px-4 py-3 text-xs text-slate-600">
            <span>
              Base: {statusDados.total_licitacoes.toLocaleString("pt-BR")} oportunidades
            </span>
            {statusDados.fontes.map((fonte) => (
              <span key={fonte.fonte}>
                {fonte.fonte}:{" "}
                <strong className={fonte.status === "ok" ? "text-emerald-700" : "text-amber-700"}>
                  {fonte.status === "ok" ? "atualizada" : fonte.status}
                </strong>
                {fonte.ultima_execucao_em
                  ? ` em ${new Intl.DateTimeFormat("pt-BR", {
                      dateStyle: "short",
                      timeStyle: "short",
                      timeZone: "America/Sao_Paulo",
                    }).format(new Date(fonte.ultima_execucao_em))}`
                  : ""}
              </span>
            ))}
          </div>
        ) : null}

        {result.error ? (
          <div
            role="alert"
            className="mt-8 rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-950"
          >
            <p className="font-bold">A API não respondeu desta vez.</p>
            <p className="mt-1 text-sm leading-6">
              {result.error} Verifique se o backend está ativo na porta 8000.
            </p>
          </div>
        ) : null}

        {result.data.length > 0 ? (
          <>
            <p className="mt-8 text-sm text-slate-500">
              Exibindo {firstResult}–{lastResult} de {result.total} licitações
            </p>
            <div className="mt-4 grid gap-5 lg:grid-cols-2">
              {result.data.map((licitacao) => (
                <LicitacaoCard key={licitacao.id} licitacao={licitacao} />
              ))}
            </div>
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              filters={filters}
            />
          </>
        ) : (
          <div className="mt-8 flex min-h-80 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
            <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-navy-50 text-navy-700">
              <FileSearch2 aria-hidden="true" size={26} />
            </span>
            <h2 className="mt-5 text-xl font-bold text-navy-950">
              Nenhuma licitação encontrada
            </h2>
            <p className="mt-2 max-w-md leading-7 text-slate-600">
              Ajuste os filtros ou execute uma coleta do PNCP para preencher a
              base com novas oportunidades.
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
