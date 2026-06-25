import { ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";

import type { LicitacaoFilters } from "@/types/licitacao";

type PaginationProps = {
  currentPage: number;
  totalPages: number;
  filters: LicitacaoFilters;
};

function pageHref(page: number, filters: LicitacaoFilters): string {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  if (page > 1) params.set("pagina", String(page));
  const query = params.toString();
  return query ? `/licitacoes?${query}` : "/licitacoes";
}

function visiblePages(currentPage: number, totalPages: number): number[] {
  const start = Math.max(1, Math.min(currentPage - 2, totalPages - 4));
  const end = Math.min(totalPages, start + 4);
  return Array.from({ length: end - start + 1 }, (_, index) => start + index);
}

export function Pagination({
  currentPage,
  totalPages,
  filters,
}: PaginationProps) {
  if (totalPages <= 1) return null;

  const pages = visiblePages(currentPage, totalPages);
  const linkBase =
    "focus-ring inline-flex h-10 min-w-10 items-center justify-center rounded-lg border px-3 text-sm font-bold transition";
  const enabled = `${linkBase} border-slate-200 bg-white text-slate-700 hover:border-navy-200 hover:text-navy-800`;
  const disabled = `${linkBase} cursor-not-allowed border-slate-100 bg-slate-100 text-slate-400`;

  return (
    <nav
      aria-label="Paginação das licitações"
      className="mt-10 flex flex-col items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-card sm:flex-row"
    >
      <p className="font-mono text-sm text-slate-500">
        Página {currentPage} de {totalPages}
      </p>

      <div className="flex flex-wrap items-center justify-center gap-2">
        {currentPage > 1 ? (
          <Link
            href={pageHref(currentPage - 1, filters)}
            className={enabled}
            aria-label="Página anterior"
          >
            <ChevronLeft aria-hidden="true" size={17} />
            <span className="hidden sm:inline">Anterior</span>
          </Link>
        ) : (
          <span className={disabled} aria-disabled="true">
            <ChevronLeft aria-hidden="true" size={17} />
            <span className="hidden sm:inline">Anterior</span>
          </span>
        )}

        {pages[0] > 1 ? <span className="px-1 text-slate-400">…</span> : null}
        {pages.map((page) => (
          <Link
            key={page}
            href={pageHref(page, filters)}
            aria-current={page === currentPage ? "page" : undefined}
            className={
              page === currentPage
                ? `${linkBase} border-navy-900 bg-navy-900 text-white`
                : enabled
            }
          >
            {page}
          </Link>
        ))}
        {pages.at(-1)! < totalPages ? (
          <span className="px-1 text-slate-400">…</span>
        ) : null}

        {currentPage < totalPages ? (
          <Link
            href={pageHref(currentPage + 1, filters)}
            className={enabled}
            aria-label="Próxima página"
          >
            <span className="hidden sm:inline">Próxima</span>
            <ChevronRight aria-hidden="true" size={17} />
          </Link>
        ) : (
          <span className={disabled} aria-disabled="true">
            <span className="hidden sm:inline">Próxima</span>
            <ChevronRight aria-hidden="true" size={17} />
          </span>
        )}
      </div>
    </nav>
  );
}
