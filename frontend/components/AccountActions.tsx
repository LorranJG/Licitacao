"use client";

import { LoaderCircle, LogOut, Send, Unplug } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export function LogoutButton() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  return (
    <button
      type="button"
      disabled={loading}
      onClick={async () => {
        setLoading(true);
        await fetch("/api/session/logout", { method: "POST" });
        router.push("/");
        router.refresh();
      }}
      className="focus-ring inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-bold text-slate-600 hover:bg-slate-100"
    >
      {loading ? <LoaderCircle className="animate-spin" size={16} /> : <LogOut size={16} />}
      Sair
    </button>
  );
}

export function TelegramAction({
  connected,
}: {
  connected: boolean;
}) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (connected) return;
    const refresh = () => router.refresh();
    window.addEventListener("focus", refresh);
    return () => window.removeEventListener("focus", refresh);
  }, [connected, router]);

  async function act() {
    setLoading(true);
    setError(null);
    const response = await fetch("/api/conta/telegram/link", {
      method: connected ? "DELETE" : "POST",
    });
    if (connected && response.ok) {
      router.refresh();
      setLoading(false);
      return;
    }
    const body = await response.json();
    if (!response.ok) {
      setError(body.detail || "Não foi possível conectar o Telegram.");
      setLoading(false);
      return;
    }
    window.open(body.url, "_blank", "noopener,noreferrer");
    setLoading(false);
  }

  return (
    <div>
      <button
        type="button"
        onClick={act}
        disabled={loading}
        className={[
          "focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-xl px-5 text-sm font-bold transition disabled:opacity-60",
          connected
            ? "border border-slate-200 bg-white text-slate-700"
            : "bg-sky-500 text-white hover:bg-sky-600",
        ].join(" ")}
      >
        {loading ? (
          <LoaderCircle className="animate-spin" size={17} />
        ) : connected ? (
          <Unplug size={17} />
        ) : (
          <Send size={17} />
        )}
        {connected ? "Desconectar Telegram" : "Conectar Telegram"}
      </button>
      {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}
    </div>
  );
}

export function DeleteReminderButton({ reminderId }: { reminderId: number }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  return (
    <button
      type="button"
      disabled={loading}
      onClick={async () => {
        setLoading(true);
        const response = await fetch(`/api/conta/lembretes/${reminderId}`, {
          method: "DELETE",
        });
        if (response.ok) router.refresh();
        setLoading(false);
      }}
      className="text-xs font-bold text-red-600 hover:text-red-700"
    >
      {loading ? "Removendo..." : "Remover"}
    </button>
  );
}
