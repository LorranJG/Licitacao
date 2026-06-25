"use client";

import { BellPlus, LoaderCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { FormEvent, useMemo, useState } from "react";

type ReminderFormProps = {
  licitacaoId: number;
  deadline: string | null;
  telegramConnected: boolean;
};

function initialDate(deadline: string | null): string {
  const target = deadline
    ? new Date(new Date(deadline).getTime() - 24 * 60 * 60 * 1000)
    : new Date(Date.now() + 24 * 60 * 60 * 1000);
  if (target.getTime() <= Date.now()) {
    target.setTime(Date.now() + 60 * 60 * 1000);
  }
  const offset = target.getTimezoneOffset() * 60000;
  return new Date(target.getTime() - offset).toISOString().slice(0, 16);
}

export function ReminderForm({
  licitacaoId,
  deadline,
  telegramConnected,
}: ReminderFormProps) {
  const router = useRouter();
  const defaultDate = useMemo(() => initialDate(deadline), [deadline]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    setError(null);
    const data = new FormData(event.currentTarget);
    const response = await fetch("/api/conta/lembretes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        licitacao_id: licitacaoId,
        lembrar_em: new Date(String(data.get("lembrar_em"))).toISOString(),
        mensagem: String(data.get("mensagem") || "") || null,
      }),
    });
    const body = response.status === 204 ? null : await response.json();
    if (response.status === 401) {
      router.push(`/login?retorno=/licitacoes/${licitacaoId}`);
      return;
    }
    if (!response.ok) {
      setError(body?.detail || "Não foi possível criar o lembrete.");
    } else {
      setMessage("Lembrete criado. Você receberá a mensagem no Telegram.");
      router.refresh();
    }
    setLoading(false);
  }

  if (!telegramConnected) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-5">
        <h3 className="font-bold text-navy-950">Receber um lembrete</h3>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Entre na sua conta e conecte o Telegram para programar notificações.
        </p>
        <a
          href="/conta"
          className="mt-4 inline-flex font-bold text-navy-700"
        >
          Configurar Telegram
        </a>
      </div>
    );
  }

  return (
    <form
      onSubmit={submit}
      className="rounded-2xl border border-slate-200 bg-white p-5"
    >
      <h3 className="flex items-center gap-2 font-bold text-navy-950">
        <BellPlus size={18} />
        Criar lembrete no Telegram
      </h3>
      <label className="mt-4 block">
        <span className="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500">
          Quando avisar
        </span>
        <input
          type="datetime-local"
          name="lembrar_em"
          required
          defaultValue={defaultDate}
          className="focus-ring h-11 w-full rounded-xl border border-slate-200 px-3 text-sm"
        />
      </label>
      <label className="mt-3 block">
        <span className="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500">
          Anotação opcional
        </span>
        <textarea
          name="mensagem"
          maxLength={500}
          rows={3}
          placeholder="Ex.: revisar certidões antes de enviar a proposta"
          className="focus-ring w-full rounded-xl border border-slate-200 p-3 text-sm"
        />
      </label>
      {message ? (
        <p className="mt-3 text-sm text-emerald-700">{message}</p>
      ) : null}
      {error ? <p className="mt-3 text-sm text-red-700">{error}</p> : null}
      <button
        disabled={loading}
        className="focus-ring mt-4 inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-navy-900 px-4 text-sm font-bold text-white disabled:opacity-60"
      >
        {loading ? <LoaderCircle className="animate-spin" size={17} /> : null}
        Salvar lembrete
      </button>
    </form>
  );
}
