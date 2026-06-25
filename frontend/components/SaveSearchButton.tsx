"use client";

import { BellPlus, LoaderCircle } from "lucide-react";
import { useState } from "react";

import type { LicitacaoFilters } from "@/types/licitacao";

export function SaveSearchButton({
  filters,
  authenticated,
}: {
  filters: LicitacaoFilters;
  authenticated: boolean;
}) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const hasFilters = Object.entries(filters).some(
    ([key, value]) => key !== "status" ? Boolean(value) : value !== "aberta",
  );

  async function save() {
    if (!authenticated) {
      window.location.href = "/login";
      return;
    }
    const suggested =
      filters.palavra_chave ||
      [filters.modalidade, filters.uf].filter(Boolean).join(" em ") ||
      "Minha busca";
    const name = window.prompt("Nome para esta busca:", suggested);
    if (!name) return;
    setLoading(true);
    setMessage(null);
    const response = await fetch("/api/conta/buscas-salvas", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nome: name,
        filtros: filters,
        alertas_ativos: true,
      }),
    });
    const body = await response.json();
    setMessage(
      response.ok
        ? "Busca salva. Você será avisado sobre novas oportunidades."
        : body.detail || "Não foi possível salvar a busca.",
    );
    setLoading(false);
  }

  if (!hasFilters) return null;
  return (
    <div className="mt-4 flex flex-col items-start gap-2 sm:flex-row sm:items-center">
      <button
        type="button"
        onClick={save}
        disabled={loading}
        className="focus-ring inline-flex items-center gap-2 rounded-xl border border-navy-200 bg-white px-4 py-2.5 text-sm font-bold text-navy-800 hover:bg-navy-50 disabled:opacity-60"
      >
        {loading ? (
          <LoaderCircle className="animate-spin" size={17} />
        ) : (
          <BellPlus size={17} />
        )}
        Salvar busca e receber alertas
      </button>
      {message ? <p className="text-sm text-slate-600">{message}</p> : null}
    </div>
  );
}
