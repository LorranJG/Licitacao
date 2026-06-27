import { redirect } from "next/navigation";

import { AuthForm } from "@/components/AuthForm";
import { getCurrentUser } from "@/lib/session";

export const metadata = { title: "Criar conta" };

export default async function CadastroPage() {
  const usuario = await getCurrentUser();
  if (usuario?.acesso_liberado) redirect("/licitacoes");
  if (usuario) redirect("/comprar");
  return (
    <main className="container-page py-14 sm:py-20">
      <section className="mx-auto max-w-md rounded-3xl border border-slate-200 bg-white p-7 shadow-card sm:p-9">
        <p className="text-sm font-bold uppercase tracking-[0.14em] text-navy-600">
          Comece gratuitamente
        </p>
        <h1 className="mt-2 text-3xl font-bold text-navy-950">
          Crie sua conta
        </h1>
        <p className="mt-2 leading-7 text-slate-600">
          Salve oportunidades e receba lembretes no Telegram.
        </p>
        <AuthForm mode="registrar" />
      </section>
    </main>
  );
}
