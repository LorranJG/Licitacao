"use client";

import { LoaderCircle } from "lucide-react";
import { FormEvent, useState } from "react";

export function RequestResetForm() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  return (
    <form
      className="mt-6 space-y-4"
      onSubmit={async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setLoading(true);
        const data = new FormData(event.currentTarget);
        const response = await fetch("/api/session/solicitar-redefinicao", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: String(data.get("email") || "") }),
        });
        const body = await response.json();
        setMessage(body.message || body.detail);
        setLoading(false);
      }}
    >
      <input
        type="email"
        name="email"
        required
        aria-label="E-mail da conta"
        placeholder="seu@email.com"
        className="focus-ring h-12 w-full rounded-xl border border-slate-200 px-4"
      />
      <button
        disabled={loading}
        className="focus-ring flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-navy-900 font-bold text-white disabled:opacity-60"
      >
        {loading ? <LoaderCircle className="animate-spin" size={17} /> : null}
        Enviar instruções
      </button>
      {message ? <p className="text-sm leading-6 text-slate-600">{message}</p> : null}
    </form>
  );
}

export function ResetPasswordForm({ token }: { token: string }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  return (
    <form
      className="mt-6 space-y-4"
      onSubmit={async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        const password = String(form.get("senha") || "");
        if (password !== String(form.get("confirmacao") || "")) {
          setMessage("As senhas não conferem.");
          return;
        }
        setLoading(true);
        const response = await fetch("/api/session/redefinir-senha", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token, nova_senha: password }),
        });
        const body = await response.json();
        setMessage(body.message || body.detail);
        setLoading(false);
      }}
    >
      <input type="password" name="senha" minLength={8} required aria-label="Nova senha" placeholder="Nova senha" className="focus-ring h-12 w-full rounded-xl border border-slate-200 px-4" />
      <input type="password" name="confirmacao" minLength={8} required aria-label="Confirmação da nova senha" placeholder="Confirme a nova senha" className="focus-ring h-12 w-full rounded-xl border border-slate-200 px-4" />
      <button
        disabled={loading || !token}
        className="focus-ring flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-navy-900 font-bold text-white disabled:opacity-60"
      >
        {loading ? <LoaderCircle className="animate-spin" size={17} /> : null}
        Criar nova senha
      </button>
      {message ? <p className="text-sm leading-6 text-slate-600">{message}</p> : null}
    </form>
  );
}

export function VerifyEmailForm({ token }: { token: string }) {
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  return (
    <div className="mt-6">
      <button
        type="button"
        disabled={loading || !token}
        onClick={async () => {
          setLoading(true);
          const response = await fetch("/api/session/confirmar-email", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token }),
          });
          const body = await response.json();
          setMessage(body.message || body.detail);
          setLoading(false);
        }}
        className="focus-ring flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-navy-900 font-bold text-white disabled:opacity-60"
      >
        {loading ? <LoaderCircle className="animate-spin" size={17} /> : null}
        Confirmar meu e-mail
      </button>
      {message ? <p className="mt-4 text-sm text-slate-600">{message}</p> : null}
    </div>
  );
}
