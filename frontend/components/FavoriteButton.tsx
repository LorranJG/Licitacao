"use client";

import { Heart, LoaderCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

type FavoriteButtonProps = {
  licitacaoId: number;
  compact?: boolean;
};

export function FavoriteButton({
  licitacaoId,
  compact = false,
}: FavoriteButtonProps) {
  const router = useRouter();
  const [favorite, setFavorite] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    fetch(`/api/conta/favoritos/${licitacaoId}/status`)
      .then(async (response) => {
        if (response.status === 401) return null;
        if (!response.ok) throw new Error();
        return (await response.json()) as { favorito: boolean };
      })
      .then((body) => {
        if (active && body) setFavorite(body.favorito);
      })
      .catch(() => undefined)
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [licitacaoId]);

  async function toggle() {
    setLoading(true);
    const response = await fetch(`/api/conta/favoritos/${licitacaoId}`, {
      method: favorite ? "DELETE" : "POST",
    });
    if (response.status === 401) {
      router.push(`/login?retorno=/licitacoes/${licitacaoId}`);
      return;
    }
    if (response.ok) {
      setFavorite(!favorite);
      router.refresh();
    }
    setLoading(false);
  }

  return (
    <button
      type="button"
      onClick={toggle}
      disabled={loading}
      aria-pressed={favorite}
      className={[
        "focus-ring inline-flex items-center justify-center gap-2 rounded-xl border font-bold transition disabled:opacity-60",
        compact ? "px-3 py-2 text-xs" : "px-5 py-3 text-sm",
        favorite
          ? "border-rose-200 bg-rose-50 text-rose-700"
          : "border-slate-200 bg-white text-navy-900 hover:bg-slate-50",
      ].join(" ")}
    >
      {loading ? (
        <LoaderCircle className="animate-spin" size={17} />
      ) : (
        <Heart fill={favorite ? "currentColor" : "none"} size={17} />
      )}
      {favorite ? "Salva" : "Favoritar"}
    </button>
  );
}
