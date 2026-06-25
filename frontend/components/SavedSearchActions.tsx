"use client";

import { LoaderCircle, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function SavedSearchActions({
  id,
  name,
  active,
}: {
  id: number;
  name: string;
  active: boolean;
}) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function update(nextActive: boolean) {
    setLoading(true);
    await fetch(`/api/conta/buscas-salvas/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome: name, alertas_ativos: nextActive }),
    });
    router.refresh();
    setLoading(false);
  }

  async function remove() {
    if (!window.confirm("Excluir esta busca salva?")) return;
    setLoading(true);
    await fetch(`/api/conta/buscas-salvas/${id}`, { method: "DELETE" });
    router.refresh();
  }

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        disabled={loading}
        onClick={() => update(!active)}
        className="text-xs font-bold text-navy-700"
      >
        {loading ? "Salvando..." : active ? "Pausar alertas" : "Ativar alertas"}
      </button>
      <button
        type="button"
        disabled={loading}
        onClick={remove}
        aria-label="Excluir busca"
        className="text-red-600"
      >
        {loading ? <LoaderCircle className="animate-spin" size={15} /> : <Trash2 size={15} />}
      </button>
    </div>
  );
}
