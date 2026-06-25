import { BellRing, Search } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import { SavedSearchActions } from "@/components/SavedSearchActions";
import { getAccountData, getCurrentUser } from "@/lib/session";

export const metadata = { title: "Buscas salvas" };

export default async function BuscasPage() {
  if (!(await getCurrentUser())) redirect("/login");
  const { buscas } = await getAccountData();
  return (
    <main className="container-page py-12 sm:py-16">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-bold uppercase tracking-wider text-navy-600">
            Monitoramento
          </p>
          <h1 className="mt-2 text-4xl font-bold text-navy-950">Buscas salvas</h1>
          <p className="mt-2 text-slate-600">
            Receba avisos quando novas oportunidades combinarem com seus filtros.
          </p>
        </div>
        <Link href="/licitacoes" className="focus-ring inline-flex items-center gap-2 rounded-xl bg-navy-900 px-5 py-3 text-sm font-bold text-white">
          <Search size={17} />
          Criar nova busca
        </Link>
      </div>
      {buscas.length ? (
        <div className="mt-8 grid gap-5 lg:grid-cols-2">
          {buscas.map((busca) => {
            const params = new URLSearchParams(busca.filtros);
            return (
              <article key={busca.id} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-bold text-navy-950">{busca.nome}</h2>
                    <p className="mt-1 text-sm text-slate-500">
                      {busca.total_correspondencias} correspondência
                      {busca.total_correspondencias === 1 ? "" : "s"} atualmente
                    </p>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-xs font-bold ${busca.alertas_ativos ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-600"}`}>
                    {busca.alertas_ativos ? "Alertas ativos" : "Pausada"}
                  </span>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {Object.entries(busca.filtros).map(([key, value]) => (
                    <span key={key} className="rounded-lg bg-navy-50 px-2.5 py-1 text-xs text-navy-700">
                      {key.replaceAll("_", " ")}: {value}
                    </span>
                  ))}
                </div>
                <div className="mt-5 flex items-center justify-between gap-4 border-t border-slate-100 pt-4">
                  <Link href={`/licitacoes?${params.toString()}`} className="text-sm font-bold text-navy-700">
                    Ver resultados
                  </Link>
                  <SavedSearchActions id={busca.id} name={busca.nome} active={busca.alertas_ativos} />
                </div>
              </article>
            );
          })}
        </div>
      ) : (
        <div className="mt-8 flex min-h-72 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
          <BellRing size={28} className="text-navy-600" />
          <h2 className="mt-4 text-xl font-bold text-navy-950">Nenhuma busca salva</h2>
          <p className="mt-2 max-w-md text-slate-600">
            Aplique filtros na listagem e clique em “Salvar busca e receber alertas”.
          </p>
        </div>
      )}
    </main>
  );
}
