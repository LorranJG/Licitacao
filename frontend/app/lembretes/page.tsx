import { Bell, BellOff } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import { DeleteReminderButton } from "@/components/AccountActions";
import { LicitacaoCard } from "@/components/LicitacaoCard";
import { getAccountData, getCurrentUser } from "@/lib/session";

export const metadata = { title: "Lembretes" };

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
    timeZone: "America/Sao_Paulo",
  }).format(new Date(value));
}

export default async function LembretesPage() {
  if (!(await getCurrentUser())) redirect("/login");
  const { lembretes } = await getAccountData();

  return (
    <main className="pb-20">
      <section className="border-b border-slate-200 bg-white">
        <div className="container-page py-10 sm:py-14">
          <p className="flex items-center gap-2 text-sm font-bold uppercase tracking-[0.14em] text-navy-600">
            <Bell aria-hidden="true" size={17} />
            Avisos programados
          </p>
          <div className="mt-3 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <h1 className="text-4xl font-bold text-navy-950">
                Meus lembretes
              </h1>
              <p className="mt-2 max-w-2xl leading-7 text-slate-600">
                Consulte as licitações que possuem notificações programadas no
                Telegram.
              </p>
            </div>
            <p className="font-mono text-sm font-semibold text-slate-500">
              {lembretes.length} lembrete{lembretes.length === 1 ? "" : "s"}
            </p>
          </div>
        </div>
      </section>

      <div className="container-page pt-8">
        {lembretes.length ? (
          <div className="grid gap-6 lg:grid-cols-2">
            {lembretes.map((lembrete) => (
              <div key={lembrete.id} className="flex flex-col gap-3">
                <div className="flex items-start justify-between gap-4 rounded-2xl border border-sky-200 bg-sky-50 px-5 py-4">
                  <div>
                    <p className="font-bold text-sky-900">
                      {lembrete.enviado_em
                        ? `Enviado em ${formatDateTime(lembrete.enviado_em)}`
                        : `Avisar em ${formatDateTime(lembrete.lembrar_em)}`}
                    </p>
                    {lembrete.mensagem ? (
                      <p className="mt-1 text-sm leading-6 text-slate-600">
                        {lembrete.mensagem}
                      </p>
                    ) : null}
                  </div>
                  <DeleteReminderButton reminderId={lembrete.id} />
                </div>
                <LicitacaoCard licitacao={lembrete.licitacao} />
              </div>
            ))}
          </div>
        ) : (
          <div className="flex min-h-80 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
            <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-sky-50 text-sky-600">
              <BellOff aria-hidden="true" size={27} />
            </span>
            <h2 className="mt-5 text-xl font-bold text-navy-950">
              Nenhum lembrete programado
            </h2>
            <p className="mt-2 max-w-md leading-7 text-slate-600">
              Abra uma licitação e escolha quando deseja receber um aviso no
              Telegram.
            </p>
            <Link
              href="/licitacoes"
              className="focus-ring mt-5 rounded-xl bg-navy-900 px-5 py-3 font-bold text-white"
            >
              Ver licitações
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}
