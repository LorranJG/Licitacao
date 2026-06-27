"use client";

import { LoaderCircle, LogIn, UserPlus } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

type AuthFormProps = {
  mode: "login" | "registrar";
  oauthError?: string | null;
};

export function AuthForm({ mode, oauthError = null }: AuthFormProps) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const isRegister = mode === "registrar";

  function startGoogleLogin() {
    window.location.assign("/api/session/google/start");
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    const formData = new FormData(event.currentTarget);
    const payload = {
      ...(isRegister ? { nome: String(formData.get("nome") || "") } : {}),
      email: String(formData.get("email") || ""),
      senha: String(formData.get("senha") || ""),
    };
    try {
      const response = await fetch(`/api/session/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.detail || "Não foi possível continuar.");
      }
      router.push(body.usuario?.acesso_liberado ? "/licitacoes" : "/comprar");
      router.refresh();
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Não foi possível continuar.",
      );
    } finally {
      setLoading(false);
    }
  }

  const fieldClass =
    "focus-ring h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-slate-800";

  return (
    <div className="mt-7">
      <button
        type="button"
        onClick={startGoogleLogin}
        className="focus-ring inline-flex h-12 w-full items-center justify-center gap-3 rounded-xl border border-slate-200 bg-white px-5 font-bold text-slate-700 transition hover:bg-slate-50"
      >
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          className="h-5 w-5"
        >
          <path
            fill="#4285F4"
            d="M21.6 12.23c0-.71-.06-1.4-.18-2.07H12v3.92h5.38a4.6 4.6 0 0 1-2 3.02v2.55h3.24c1.9-1.75 2.98-4.33 2.98-7.42Z"
          />
          <path
            fill="#34A853"
            d="M12 22c2.7 0 4.98-.9 6.64-2.43l-3.24-2.55c-.9.6-2.05.96-3.4.96-2.61 0-4.82-1.76-5.61-4.13H3.04v2.63A10 10 0 0 0 12 22Z"
          />
          <path
            fill="#FBBC05"
            d="M6.39 13.85A6.02 6.02 0 0 1 6.07 12c0-.64.11-1.27.32-1.85V7.52H3.04A10 10 0 0 0 2 12c0 1.61.38 3.14 1.04 4.48l3.35-2.63Z"
          />
          <path
            fill="#EA4335"
            d="M12 6.02c1.47 0 2.78.5 3.82 1.49l2.88-2.88A9.66 9.66 0 0 0 12 2a10 10 0 0 0-8.96 5.52l3.35 2.63C7.18 7.78 9.39 6.02 12 6.02Z"
          />
        </svg>
        Continuar com Google
      </button>
      {oauthError ? (
        <p
          role="alert"
          className="mt-3 rounded-xl bg-amber-50 p-3 text-sm text-amber-800"
        >
          {oauthError}
        </p>
      ) : null}

      <div className="my-5 flex items-center gap-3">
        <span className="h-px flex-1 bg-slate-200" />
        <span className="text-xs font-bold uppercase tracking-wide text-slate-400">
          ou
        </span>
        <span className="h-px flex-1 bg-slate-200" />
      </div>

      <form onSubmit={submit} className="space-y-5">
      {isRegister ? (
        <label className="block">
          <span className="mb-2 block text-sm font-bold text-navy-950">
            Seu nome
          </span>
          <input
            name="nome"
            required
            minLength={2}
            autoComplete="name"
            className={fieldClass}
          />
        </label>
      ) : null}
      <label className="block">
        <span className="mb-2 block text-sm font-bold text-navy-950">
          E-mail
        </span>
        <input
          type="email"
          name="email"
          required
          autoComplete="email"
          className={fieldClass}
        />
      </label>
      <label className="block">
        <span className="mb-2 block text-sm font-bold text-navy-950">
          Senha
        </span>
        <input
          type="password"
          name="senha"
          required
          minLength={isRegister ? 8 : 1}
          autoComplete={isRegister ? "new-password" : "current-password"}
          className={fieldClass}
        />
        {isRegister ? (
          <span className="mt-1 block text-xs text-slate-500">
            Use pelo menos 8 caracteres.
          </span>
        ) : null}
      </label>
      {!isRegister ? (
        <div className="-mt-3 text-right">
          <Link
            href="/esqueci-senha"
            className="focus-ring rounded text-sm font-bold text-navy-700 hover:underline"
          >
            Esqueci minha senha
          </Link>
        </div>
      ) : null}
      {error ? (
        <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      ) : null}
      <button
        type="submit"
        disabled={loading}
        className="focus-ring inline-flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-navy-900 px-5 font-bold text-white transition hover:bg-navy-800 disabled:opacity-60"
      >
        {loading ? (
          <LoaderCircle className="animate-spin" size={18} />
        ) : isRegister ? (
          <UserPlus size={18} />
        ) : (
          <LogIn size={18} />
        )}
        {isRegister ? "Criar conta" : "Acessar área do cliente"}
      </button>
      <p className="text-center text-sm text-slate-600">
        {isRegister ? "Já possui uma conta?" : "Ainda não possui uma conta?"}{" "}
        <Link
          href={isRegister ? "/login" : "/cadastro"}
          className="font-bold text-navy-700"
        >
          {isRegister ? "Área do cliente" : "Cadastre-se"}
        </Link>
      </p>
      </form>
    </div>
  );
}
