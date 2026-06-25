import {
  Activity,
  BarChart3,
  CalendarClock,
  CircleDollarSign,
  Database,
  MapPinned,
  TrendingUp,
  WalletCards,
} from "lucide-react";
import Link from "next/link";

import { getIndicadores } from "@/lib/api";
import type { IndicadorItem } from "@/types/licitacao";

export const metadata = {
  title: "Indicadores",
};

type IndicadoresPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

function formatCurrency(value: string): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(Number(value));
}

function formatDate(value: string | null): string {
  if (!value) return "não informada";
  return new Intl.DateTimeFormat("pt-BR", {
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function formatDateTime(value: string | null): string {
  if (!value) return "não informada";
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
    timeZone: "America/Sao_Paulo",
  }).format(new Date(value));
}

function Ranking({
  title,
  items,
  filterKey,
  baseStatus = "aberta",
}: {
  title: string;
  items: IndicadorItem[];
  filterKey?: "uf" | "modalidade" | "fonte" | "status" | "palavra_chave";
  baseStatus?: string;
}) {
  const max = Math.max(...items.map((item) => item.quantidade), 1);
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-bold text-navy-950">{title}</h2>
      <div className="mt-5 space-y-4">
        {items.map((item, index) => {
          const content = (
            <>
            <div className="flex items-start justify-between gap-4 text-sm">
              <span className="line-clamp-2 font-semibold text-slate-700">
                {index + 1}. {item.nome}
              </span>
              <span className="shrink-0 text-right">
                <span className="block font-mono font-bold text-navy-700">
                  {item.quantidade.toLocaleString("pt-BR")}
                </span>
                <span className="block text-[10px] text-slate-400">
                  {formatCurrency(item.valor_estimado)}
                </span>
              </span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-navy-600"
                style={{ width: `${(item.quantidade / max) * 100}%` }}
              />
            </div>
            </>
          );
          if (!filterKey) return <div key={item.nome}>{content}</div>;
          const params = new URLSearchParams({
            [filterKey]: item.nome,
            status: filterKey === "status" ? item.nome : baseStatus,
          });
          return (
            <Link
              key={item.nome}
              href={`/licitacoes?${params.toString()}`}
              className="focus-ring block rounded-lg hover:bg-slate-50"
            >
              {content}
            </Link>
          );
        })}
      </div>
    </section>
  );
}

export default async function IndicadoresPage({
  searchParams,
}: IndicadoresPageProps) {
  const params = await searchParams;
  const rawStatus = Array.isArray(params.status) ? params.status[0] : params.status;
  const status = rawStatus === "todos" ? "todos" : "aberta";
  const result = await getIndicadores(status);
  const evolutionMax = Math.max(
    ...(result.data?.evolucao_mensal.map((month) => month.quantidade) ?? []),
    1,
  );

  return (
    <main className="pb-20">
      <section className="border-b border-slate-200 bg-white">
        <div className="container-page py-12 sm:py-16">
          <p className="text-sm font-bold uppercase tracking-[0.16em] text-navy-600">
            Inteligência de mercado público
          </p>
          <div className="mt-3 flex flex-col justify-between gap-5 md:flex-row md:items-end">
            <div>
              <h1 className="text-4xl font-bold tracking-tight text-navy-950 sm:text-5xl">
                Indicadores
              </h1>
              <p className="mt-3 max-w-2xl text-lg leading-8 text-slate-600">
                Acompanhe volume, valores, regiões, órgãos compradores e a
                evolução das oportunidades.
              </p>
            </div>
            <div className="flex rounded-xl border border-slate-200 bg-slate-50 p-1">
              <Link
                href="/indicadores"
                className={`rounded-lg px-4 py-2 text-sm font-bold ${
                  status === "aberta"
                    ? "bg-white text-navy-900 shadow-sm"
                    : "text-slate-500"
                }`}
              >
                Em aberto
              </Link>
              <Link
                href="/indicadores?status=todos"
                className={`rounded-lg px-4 py-2 text-sm font-bold ${
                  status === "todos"
                    ? "bg-white text-navy-900 shadow-sm"
                    : "text-slate-500"
                }`}
              >
                Histórico
              </Link>
            </div>
          </div>
        </div>
      </section>

      <div className="container-page pt-8">
        {!result.data ? (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 p-7 text-amber-950">
            <h2 className="font-bold">Não foi possível gerar os indicadores.</h2>
            <p className="mt-2 text-sm">{result.error}</p>
          </div>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {[
                {
                  icon: Activity,
                  label: "Oportunidades",
                  value: result.data.total.toLocaleString("pt-BR"),
                  help:
                    status === "aberta"
                      ? "atualmente abertas"
                      : "na base histórica",
                },
                {
                  icon: CircleDollarSign,
                  label: "Valor mediano",
                  value: formatCurrency(result.data.valor_mediano_estimado),
                  help: "metade das oportunidades está abaixo deste valor",
                },
                {
                  icon: BarChart3,
                  label: "Publicadas em 30 dias",
                  value:
                    result.data.publicadas_ultimos_30_dias.toLocaleString("pt-BR"),
                  help:
                    result.data.variacao_publicacoes_30_dias === null
                      ? "sem período anterior comparável"
                      : `${Number(result.data.variacao_publicacoes_30_dias) >= 0 ? "+" : ""}${Number(result.data.variacao_publicacoes_30_dias).toFixed(1)}% contra os 30 dias anteriores`,
                },
                {
                  icon: CalendarClock,
                  label: "Encerram em 7 dias",
                  value: result.data.encerram_em_7_dias.toLocaleString("pt-BR"),
                  help: "oportunidades abertas com prazo próximo",
                },
              ].map(({ icon: Icon, label, value, help }) => (
                <article
                  key={label}
                  className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card"
                >
                  <Icon aria-hidden="true" className="text-navy-600" size={22} />
                  <p className="mt-5 text-sm font-semibold text-slate-500">
                    {label}
                  </p>
                  <p className="mt-1 font-mono text-2xl font-bold text-navy-950">
                    {value}
                  </p>
                  <p className="mt-2 text-xs text-slate-400">{help}</p>
                </article>
              ))}
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-3">
              <article className="rounded-2xl border border-violet-200 bg-violet-50 p-5">
                <WalletCards className="text-violet-700" size={21} />
                <p className="mt-3 text-sm font-bold text-violet-950">
                  Soma dos valores publicados
                </p>
                <p className="mt-1 font-mono text-2xl font-bold text-violet-950">
                  {formatCurrency(result.data.valor_total_estimado)}
                </p>
                <p className="mt-2 text-xs text-violet-800">
                  Pode incluir concessões e valores extremos informados pelas
                  fontes; não equivale ao valor contratado.
                </p>
              </article>
              <article className="rounded-2xl border border-sky-200 bg-sky-50 p-5">
                <TrendingUp className="text-sky-700" size={21} />
                <p className="mt-3 text-sm font-bold text-sky-950">
                  Encerram nos próximos 30 dias
                </p>
                <p className="mt-1 font-mono text-2xl font-bold text-sky-950">
                  {result.data.encerram_em_30_dias.toLocaleString("pt-BR")}
                </p>
                <p className="mt-2 text-xs text-sky-800">
                  Inclui as oportunidades dos próximos 7 dias.
                </p>
              </article>
              <article className="rounded-2xl border border-slate-200 bg-white p-5">
                <Database className="text-navy-600" size={21} />
                <p className="mt-3 text-sm font-bold text-navy-950">
                  Cobertura dos dados
                </p>
                <p className="mt-1 text-sm text-slate-600">
                  Valor informado:{" "}
                  <strong>{Number(result.data.percentual_com_valor).toFixed(1)}%</strong>
                </p>
                <p className="mt-1 text-sm text-slate-600">
                  Prazo informado:{" "}
                  <strong>{Number(result.data.percentual_com_prazo).toFixed(1)}%</strong>
                </p>
              </article>
            </div>

            <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6">
              <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
                <div>
                  <h2 className="text-lg font-bold text-navy-950">
                    Evolução das publicações
                  </h2>
                  <p className="mt-1 text-xs text-slate-500">
                    Base selecionada: {formatDate(result.data.data_inicial_base)} a{" "}
                    {formatDate(result.data.data_final_base)}.
                  </p>
                  <p className="mt-1 text-xs text-slate-400">
                    Última atualização: {formatDateTime(result.data.ultima_atualizacao)}.
                  </p>
                </div>
                <p className="text-xs text-slate-400">
                  Valores extremos podem elevar o total financeiro; por isso a
                  mediana é usada como referência de porte.
                </p>
              </div>
              <div className="mt-6 flex h-56 items-end gap-2 overflow-x-auto pb-2">
                {result.data.evolucao_mensal.map((item) => {
                  return (
                    <div
                      key={item.periodo}
                      className="flex min-w-14 flex-1 flex-col items-center justify-end"
                    >
                      <span className="mb-2 font-mono text-xs font-bold text-navy-700">
                        {item.quantidade}
                      </span>
                      <div
                        className="w-full max-w-16 rounded-t-lg bg-navy-600"
                        style={{
                          height: `${Math.max(
                            (item.quantidade / evolutionMax) * 160,
                            6,
                          )}px`,
                        }}
                      />
                      <span className="mt-2 text-[11px] text-slate-400">
                        {item.periodo.slice(5)}/{item.periodo.slice(2, 4)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </section>

            <div className="mt-6 grid gap-6 lg:grid-cols-2">
              <Ranking
                title="Estados com mais oportunidades"
                items={result.data.por_uf}
                filterKey="uf"
                baseStatus={status}
              />
              <Ranking
                title="Modalidades mais frequentes"
                items={result.data.por_modalidade}
                filterKey="modalidade"
                baseStatus={status}
              />
              <Ranking
                title="Órgãos que mais publicam"
                items={result.data.principais_orgaos}
                filterKey="palavra_chave"
                baseStatus={status}
              />
              <Ranking
                title="Distribuição por fonte"
                items={result.data.por_fonte}
                filterKey="fonte"
                baseStatus={status}
              />
              {status === "todos" ? (
                <Ranking
                  title="Distribuição por situação"
                  items={result.data.por_status}
                  filterKey="status"
                />
              ) : null}
              <section className="rounded-2xl border border-slate-200 bg-white p-6">
                <h2 className="text-lg font-bold text-navy-950">
                  Como interpretar
                </h2>
                <dl className="mt-5 space-y-4 text-sm">
                  <div>
                    <dt className="font-bold text-slate-800">Valor mediano</dt>
                    <dd className="mt-1 leading-6 text-slate-500">
                      Representa melhor uma oportunidade típica do que a média,
                      que sofre influência de concessões e valores sentinela.
                    </dd>
                  </div>
                  <div>
                    <dt className="font-bold text-slate-800">Valor estimado total</dt>
                    <dd className="mt-1 leading-6 text-slate-500">
                      Soma apenas os valores publicados pelas fontes e não
                      representa necessariamente o valor contratado.
                    </dd>
                  </div>
                  <div>
                    <dt className="font-bold text-slate-800">Variação em 30 dias</dt>
                    <dd className="mt-1 leading-6 text-slate-500">
                      Compara a data de publicação dos últimos 30 dias com os 30
                      dias imediatamente anteriores.
                    </dd>
                  </div>
                </dl>
              </section>
              <section className="rounded-2xl bg-navy-950 p-7 text-white">
                <MapPinned
                  aria-hidden="true"
                  className="text-blue-300"
                  size={25}
                />
                <h2 className="mt-6 text-2xl font-bold">
                  Use os indicadores para escolher onde competir.
                </h2>
                <p className="mt-3 leading-7 text-slate-300">
                  Compare regiões, modalidades e órgãos para concentrar sua
                  prospecção nos mercados com maior aderência.
                </p>
                <Link
                  href="/licitacoes"
                  className="mt-7 inline-flex rounded-xl bg-white px-5 py-3 font-bold text-navy-950"
                >
                  Explorar oportunidades
                </Link>
              </section>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
