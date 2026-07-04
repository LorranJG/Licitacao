import { CheckCircle2, Clock } from "lucide-react";
import Link from "next/link";

import { getCurrentUser } from "@/lib/session";

export const metadata = { title: "Compra recebida" };

export default async function CompraSucessoPage() {
  const usuario = await getCurrentUser();

  return (
    <main className="container-page flex min-h-[70vh] items-center justify-center py-16">
      <section className="max-w-2xl rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-card">
        <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-700">
          {usuario?.acesso_liberado ? <CheckCircle2 size={28} /> : <Clock size={28} />}
        </span>
        <h1 className="mt-5 text-3xl font-bold text-navy-950">
          {usuario?.acesso_liberado
            ? "Acesso liberado"
            : "Pagamento recebido"}
        </h1>
        <p className="mt-3 leading-7 text-slate-600">
          {usuario?.acesso_liberado
            ? "Sua compra foi confirmada e o Radar ja esta disponivel."
            : "Estamos aguardando a confirmação do Mercado Pago. Pagamentos por cartão são instantâneos. Boleto pode levar até 3 dias úteis."}
        </p>
        <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
          <Link
            href={usuario?.acesso_liberado ? "/licitacoes" : "/comprar"}
            className="focus-ring inline-flex h-12 items-center justify-center rounded-xl bg-navy-900 px-6 font-bold text-white transition hover:bg-navy-800"
          >
            {usuario?.acesso_liberado ? "Acessar licitacoes" : "Ver status"}
          </Link>
          <Link
            href="/conta"
            className="focus-ring inline-flex h-12 items-center justify-center rounded-xl border border-slate-200 px-6 font-bold text-navy-800 transition hover:bg-slate-50"
          >
            Minha conta
          </Link>
        </div>
      </section>
    </main>
  );
}
