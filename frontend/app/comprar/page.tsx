import { CheckCircle2, LockKeyhole, Radar, Search, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import { PurchaseButton } from "@/components/PurchaseButton";
import { getCurrentUser } from "@/lib/session";

export const metadata = { title: "Comprar acesso" };

type ComprarPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function ComprarPage({ searchParams }: ComprarPageProps) {
  const [usuario, params] = await Promise.all([getCurrentUser(), searchParams]);
  if (usuario?.acesso_liberado) redirect("/licitacoes");
  const cancelado = params.cancelado !== undefined;

  return (
    <main className="pb-20">
      <section className="border-b border-slate-200 bg-white">
        <div className="container-page grid gap-10 py-12 sm:py-16 lg:grid-cols-[1fr_380px] lg:items-center">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.16em] text-navy-600">
              Acesso ao Radar
            </p>
            <h1 className="mt-3 max-w-3xl text-4xl font-bold tracking-tight text-navy-950 sm:text-5xl">
              Monitore licitações públicas em um só lugar.
            </h1>
            <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-600">
              Sua conta pode ser criada gratuitamente. O acesso ao produto fica
              liberado somente depois da confirmação do pagamento.
            </p>
            {cancelado ? (
              <p className="mt-5 max-w-xl rounded-xl bg-amber-50 p-4 text-sm font-semibold text-amber-800">
                A compra foi cancelada. Você pode iniciar novamente quando quiser.
              </p>
            ) : null}
          </div>

          <aside className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
            <div className="flex items-center gap-3">
              <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-navy-50 text-navy-700">
                <Radar size={22} />
              </span>
              <div>
                <h2 className="text-xl font-bold text-navy-950">
                  Radar Licitações
                </h2>
                <p className="text-sm text-slate-500">Acesso completo</p>
              </div>
            </div>

            <div className="mt-6 rounded-xl bg-navy-50 px-4 py-3">
              <p className="text-sm text-slate-500">Valor mensal</p>
              <p className="mt-0.5 text-3xl font-extrabold text-navy-950">
                R$ 49<span className="text-xl">,90</span>
                <span className="ml-1 text-base font-semibold text-slate-400">/mês</span>
              </p>
            </div>

            <ul className="mt-5 space-y-3 text-sm leading-6 text-slate-700">
              {[
                "Consulta completa da base de licitações",
                "Filtros, indicadores e detalhes das oportunidades",
                "Favoritos, lembretes e buscas salvas com alertas",
                "Acesso ao portal oficial de cada publicação",
              ].map((item) => (
                <li key={item} className="flex gap-2">
                  <CheckCircle2 className="mt-0.5 shrink-0 text-emerald-600" size={17} />
                  <span>{item}</span>
                </li>
              ))}
            </ul>

            <div className="mt-7">
              {usuario ? (
                <PurchaseButton />
              ) : (
                <div className="grid gap-3">
                  <Link
                    href="/cadastro"
                    className="focus-ring inline-flex h-12 items-center justify-center rounded-xl bg-navy-900 px-6 font-bold text-white transition hover:bg-navy-800"
                  >
                    Criar conta para comprar
                  </Link>
                  <Link
                    href="/login"
                    className="focus-ring inline-flex h-12 items-center justify-center rounded-xl border border-slate-200 bg-white px-6 font-bold text-navy-800 transition hover:bg-slate-50"
                  >
                    Área do cliente
                  </Link>
                </div>
              )}
            </div>

            <p className="mt-4 text-center text-xs text-slate-400">
              Pagamento processado pelo{" "}
              <span className="font-semibold text-slate-500">Mercado Pago</span>.{" "}
              <Link href="/reembolso" className="underline hover:text-navy-700">
                Política de reembolso
              </Link>
            </p>
          </aside>
        </div>
      </section>

      <section className="container-page grid gap-5 pt-8 md:grid-cols-3">
        {[
          {
            icon: LockKeyhole,
            title: "Acesso após pagamento",
            text: "Cadastro e login continuam disponíveis, mas o produto só abre quando o Mercado Pago confirmar a compra.",
          },
          {
            icon: ShieldCheck,
            title: "Confirmação segura",
            text: "A liberação acontece pelo webhook do Mercado Pago, não apenas pelo retorno do navegador.",
          },
          {
            icon: Search,
            title: "Uso completo",
            text: "Depois de liberado, você acessa licitações, indicadores, favoritos, lembretes e buscas salvas.",
          },
        ].map(({ icon: Icon, title, text }) => (
          <article key={title} className="rounded-2xl border border-slate-200 bg-white p-6">
            <Icon className="text-navy-600" size={22} />
            <h2 className="mt-4 text-lg font-bold text-navy-950">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">{text}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
