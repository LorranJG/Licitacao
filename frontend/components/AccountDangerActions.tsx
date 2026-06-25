"use client";

import { LoaderCircle, MailCheck, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function ResendVerificationButton() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  return (
    <div>
      <button
        type="button"
        disabled={loading}
        onClick={async () => {
          setLoading(true);
          const response = await fetch("/api/conta/auth/reenviar-verificacao", {
            method: "POST",
          });
          const body = await response.json();
          setMessage(body.message || body.detail);
          setLoading(false);
        }}
        className="focus-ring inline-flex items-center gap-2 rounded-xl bg-amber-600 px-4 py-2.5 text-sm font-bold text-white disabled:opacity-60"
      >
        {loading ? <LoaderCircle className="animate-spin" size={16} /> : <MailCheck size={16} />}
        Enviar confirmação
      </button>
      {message ? <p className="mt-2 text-sm text-amber-900">{message}</p> : null}
    </div>
  );
}

export function DeleteAccountButton() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  return (
    <button
      type="button"
      disabled={loading}
      onClick={async () => {
        const confirmation = window.prompt(
          'Digite EXCLUIR para apagar sua conta, favoritos, buscas e lembretes.',
        );
        if (confirmation !== "EXCLUIR") return;
        setLoading(true);
        const response = await fetch("/api/conta/auth/me", { method: "DELETE" });
        if (response.ok) {
          await fetch("/api/session/logout", { method: "POST" });
          router.push("/");
          router.refresh();
          return;
        }
        setLoading(false);
      }}
      className="focus-ring inline-flex items-center gap-2 rounded-xl border border-red-200 bg-white px-4 py-2.5 text-sm font-bold text-red-700 hover:bg-red-50 disabled:opacity-60"
    >
      {loading ? <LoaderCircle className="animate-spin" size={16} /> : <Trash2 size={16} />}
      Excluir minha conta
    </button>
  );
}
