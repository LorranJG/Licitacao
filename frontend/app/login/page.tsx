import { redirect } from "next/navigation";

import { AuthForm } from "@/components/AuthForm";
import { getCurrentUser } from "@/lib/session";

export const metadata = { title: "Área do cliente" };

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
  const usuario = await getCurrentUser();
  if (usuario?.acesso_liberado) redirect("/licitacoes");
  if (usuario) redirect("/comprar");
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
          Área do cliente
        </p>
        <h1 className="mt-2 text-3xl font-bold text-navy-950">
          Acesse sua conta
        </h1>
        <p className="mt-2 leading-7 text-slate-600">
          Clientes com compra confirmada entram direto no Radar, sem passar
          novamente pelo checkout.
        </p>
        <AuthForm mode="login" oauthError={oauthError} />
      </section>
    </main>
  );
}
