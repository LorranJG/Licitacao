import Link from "next/link";

import { RequestResetForm } from "@/components/RecoveryForm";

export const metadata = { title: "Recuperar senha" };

export default function EsqueciSenhaPage() {
  return (
    <main className="container-page py-16">
      <section className="mx-auto max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-card">
        <h1 className="text-3xl font-bold text-navy-950">Recuperar senha</h1>
        <p className="mt-2 leading-7 text-slate-600">
          Informe seu e-mail para receber um link válido por 30 minutos.
        </p>
        <RequestResetForm />
        <Link href="/login" className="mt-5 block text-center text-sm font-bold text-navy-700">
          Voltar ao login
        </Link>
      </section>
    </main>
  );
}
