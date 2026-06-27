import { Search, SlidersHorizontal, X } from "lucide-react";
import Link from "next/link";

type LicitacaoFiltersProps = {
  values: {
    palavra_chave: string;
    uf: string;
    modalidade: string;
    status: string;
    data_inicio: string;
    data_fim: string;
    encerramento_inicio: string;
    encerramento_fim: string;
    fonte: string;
    valor_minimo: string;
    valor_maximo: string;
  };
};

const ufs = [
  "AC",
  "AL",
  "AP",
  "AM",
  "BA",
  "CE",
  "DF",
  "ES",
  "GO",
  "MA",
  "MT",
  "MS",
  "MG",
  "PA",
  "PB",
  "PR",
  "PE",
  "PI",
  "RJ",
  "RN",
  "RS",
  "RO",
  "RR",
  "SC",
  "SP",
  "SE",
  "TO",
] as const;

export function LicitacaoFilters({ values }: LicitacaoFiltersProps) {
  const hasFilters = Object.values(values).some(Boolean);
  const fieldClass =
    "focus-ring h-11 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-700 placeholder:text-slate-400";

  return (
    <form
      action="/licitacoes"
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card"
    >
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <p className="flex items-center gap-2 font-bold text-navy-950">
            <SlidersHorizontal aria-hidden="true" size={18} />
            Filtrar oportunidades
          </p>
          <p className="mt-1 text-sm leading-6 text-slate-500">
            Preencha apenas o que for relevante. Os filtros usados serão
            combinados na busca.
          </p>
        </div>
        {hasFilters ? (
          <Link
            href="/licitacoes"
            className="focus-ring inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-bold text-slate-500 hover:bg-slate-100 hover:text-navy-700"
          >
            <X aria-hidden="true" size={14} />
            Limpar
          </Link>
        ) : null}
      </div>
      <div className="grid gap-x-3 gap-y-4 md:grid-cols-2 xl:grid-cols-4">
        <label className="space-y-1.5">
          <span className="block text-sm font-bold text-navy-950">
            Palavra-chave
          </span>
          <input
            type="search"
            name="palavra_chave"
            defaultValue={values.palavra_chave}
            placeholder="Ex.: software, engenharia..."
            className={fieldClass}
          />
        </label>
        <label className="space-y-1.5">
          <span className="block text-sm font-bold text-navy-950">UF</span>
          <select name="uf" defaultValue={values.uf} className={fieldClass}>
            <option value="">Todas as UFs</option>
            {ufs.map((uf) => (
              <option key={uf} value={uf}>
                {uf}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-1.5">
          <span className="block text-sm font-bold text-navy-950">
            Modalidade
          </span>
          <input
            name="modalidade"
            defaultValue={values.modalidade}
            placeholder="Ex.: pregão, concorrência..."
            className={fieldClass}
          />
        </label>
        <label className="space-y-1.5">
          <span className="block text-sm font-bold text-navy-950">Status</span>
          <select
            name="status"
            defaultValue={values.status}
            className={fieldClass}
          >
            <option value="todos">Todos os status</option>
            <option value="aberta">Aberta</option>
            <option value="encerrada">Encerrada</option>
            <option value="suspensa">Suspensa</option>
            <option value="cancelada">Cancelada</option>
            <option value="divulgada">Divulgada</option>
            <option value="divulgada no pncp">Divulgada no PNCP</option>
          </select>
        </label>
        <label className="space-y-1.5">
          <span className="block text-sm font-bold text-navy-950">Fonte</span>
          <select
            name="fonte"
            defaultValue={values.fonte}
            className={fieldClass}
          >
            <option value="">Todas as fontes</option>
            <option value="PNCP">PNCP</option>
            <option value="Compras.gov.br">Compras.gov.br</option>
          </select>
        </label>
        <label className="space-y-1.5">
          <span className="block text-sm font-bold text-navy-950">
            Divulgacao de
          </span>
          <input
            type="date"
            name="data_inicio"
            defaultValue={values.data_inicio}
            className={fieldClass}
          />
        </label>
        <label className="space-y-1.5">
          <span className="block text-sm font-bold text-navy-950">
            Divulgacao ate
          </span>
          <input
            type="date"
            name="data_fim"
            defaultValue={values.data_fim}
            className={fieldClass}
          />
        </label>
        <label className="space-y-1.5">
          <span className="block text-sm font-bold text-navy-950">
            Encerramento de
          </span>
          <input
            type="date"
            name="encerramento_inicio"
            defaultValue={values.encerramento_inicio}
            className={fieldClass}
          />
        </label>
        <label className="space-y-1.5">
          <span className="block text-sm font-bold text-navy-950">
            Encerramento ate
          </span>
          <input
            type="date"
            name="encerramento_fim"
            defaultValue={values.encerramento_fim}
            className={fieldClass}
          />
        </label>
        <label className="space-y-1.5">
          <span className="block text-sm font-bold text-navy-950">
            Valor mínimo
          </span>
          <div className="relative">
            <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-sm font-semibold text-slate-400">
              R$
            </span>
            <input
              type="number"
              name="valor_minimo"
              min="0"
              step="0.01"
              inputMode="decimal"
              defaultValue={values.valor_minimo}
              placeholder="Valor mínimo"
              className={`${fieldClass} pl-10`}
            />
          </div>
        </label>
        <label className="space-y-1.5">
          <span className="block text-sm font-bold text-navy-950">
            Valor máximo
          </span>
          <div className="relative">
            <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-sm font-semibold text-slate-400">
              R$
            </span>
            <input
              type="number"
              name="valor_maximo"
              min="0"
              step="0.01"
              inputMode="decimal"
              defaultValue={values.valor_maximo}
              placeholder="Sem limite"
              className={`${fieldClass} pl-10`}
            />
          </div>
        </label>
        <div className="flex items-end">
          <button
            type="submit"
            className="focus-ring inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-navy-900 px-5 text-sm font-bold text-white transition hover:bg-navy-800"
          >
            <Search aria-hidden="true" size={17} />
            Aplicar filtros
          </button>
        </div>
      </div>
    </form>
  );
}
