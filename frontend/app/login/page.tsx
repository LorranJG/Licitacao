import { redirect } from "next/navigation";

import { AuthForm } from "@/components/AuthForm";
import { getCurrentUser } from "@/lib/session";

export const metadata = { title: "Entrar" };

type LoginPageProps = {
  searchParams: Promise<{ erro?: string; erro_detalhe?: string }>;
};

const googleErrors: Record<string, string> = {
  google_nao_configurado:
    "O login com Google ainda não foi configurado neste ambiente.",
  google_estado_invalido:
    "A tentativa de login expirou. Tente novamente.",
  google_token_falhou:
    "O Google não conseguiu concluir a autenticação.",
  google_token_ausente:
    "O Google não retornou uma identificação válida.",
  google_login_falhou:
    "Não foi possível vincular a conta Google ao Radar.",
};

export default async function LoginPage({ searchParams }: LoginPageProps) {
  if (await getCurrentUser()) redirect("/conta");
  const { erro, erro_detalhe } = await searchParams;
  const oauthError = erro
    ? erro === "google_login_falhou" && erro_detalhe
      ? erro_detalhe
      : googleErrors[erro] || "Falha no login com Google."
    : null;
  return (
    <main className="container-page py-14 sm:py-20">
      <section className="mx-auto max-w-md rounded-3xl border border-slate-200 bg-white p-7 shadow-card sm:p-9">
        <p className="text-sm font-bold uppercase tracking-[0.14em] text-navy-600">
          Sua área
        </p>
        <h1 className="mt-2 text-3xl font-bold text-navy-950">
          Entre no Radar
        </h1>
        <p className="mt-2 leading-7 text-slate-600">
          Acesse seus favoritos, lembretes e notificações do Telegram.
        </p>
        <AuthForm
          mode="login"
          oauthError={oauthError}
        />
      </section>
    </main>
  );
}
