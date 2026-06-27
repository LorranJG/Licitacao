"use client";

import { LoaderCircle, ShoppingCart } from "lucide-react";
import { useState } from "react";

export function PurchaseButton() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function startCheckout() {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/conta/pagamentos/checkout", {
        method: "POST",
      });
      const body = (await response.json()) as { url?: string; detail?: string };
      if (!response.ok || !body.url) {
        throw new Error(body.detail || "Nao foi possivel iniciar a compra.");
      }
      window.location.assign(body.url);
    } catch (checkoutError) {
      setError(
        checkoutError instanceof Error
          ? checkoutError.message
          : "Nao foi possivel iniciar a compra.",
      );
      setLoading(false);
    }
  }

  return (
    <div>
      <button
        type="button"
        onClick={startCheckout}
        disabled={loading}
        className="focus-ring inline-flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-navy-900 px-6 font-bold text-white transition hover:bg-navy-800 disabled:opacity-60 sm:w-auto"
      >
        {loading ? (
          <LoaderCircle className="animate-spin" size={18} />
        ) : (
          <ShoppingCart size={18} />
        )}
        Comprar acesso
      </button>
      {error ? (
        <p role="alert" className="mt-3 rounded-xl bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      ) : null}
    </div>
  );
}
