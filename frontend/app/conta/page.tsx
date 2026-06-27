import { LockKeyhole, Send } from "lucide-react";
import { redirect } from "next/navigation";

import { AccountSettingsForm } from "@/components/AccountSettingsForm";
import { TelegramAction } from "@/components/AccountActions";
import {
  DeleteAccountButton,
  ResendVerificationButton,
} from "@/components/AccountDangerActions";
import { PurchaseButton } from "@/components/PurchaseButton";
import { getCurrentUser } from "@/lib/session";

export const metadata = { title: "Minha conta" };

export default async function ContaPage() {
  const usuario = await getCurrentUser();
  if (!usuario) redirect("/login");

  return (
    <main className="pb-20">
      <section className="border-b border-slate-200 bg-white">
        <div className="container-page py-10 sm:py-14">
          <p className="text-sm font-bold uppercase tracking-[0.14em] text-navy-600">
            Área pessoal
          </p>
          <h1 className="mt-2 text-4xl font-bold text-navy-950">
            Olá, {usuario.nome}
          </h1>
          <p className="mt-2 text-slate-600">{usuario.email}</p>
        </div>
      </section>

      <div className="container-page space-y-8 pt-8">
        {!usuario.email_verificado ? (
          <section className="rounded-2xl border border-amber-200 bg-amber-50 p-6">
            <h2 className="font-bold text-amber-950">Confirme seu e-mail</h2>
            <p className="mt-2 text-sm leading-6 text-amber-900">
              A confirmação ajuda a proteger sua conta e será necessária para
              receber alertas e recuperar a senha por e-mail.
            </p>
            <div className="mt-4">
              <ResendVerificationButton />
            </div>
          </section>
        ) : null}
        {!usuario.acesso_liberado ? (
          <section className="rounded-2xl border border-amber-200 bg-amber-50 p-6 sm:p-8">
            <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
              <div>
                <h2 className="flex items-center gap-2 text-xl font-bold text-amber-950">
                  <LockKeyhole size={21} />
                  Acesso pendente
                </h2>
                <p className="mt-2 max-w-2xl leading-7 text-amber-900">
                  Sua conta foi criada, mas o acesso ao Radar so sera liberado
                  depois da compra confirmada.
                </p>
              </div>
              <PurchaseButton />
            </div>
          </section>
        ) : null}
        {usuario.acesso_liberado ? (
        <section className="rounded-2xl border border-sky-200 bg-sky-50 p-6 sm:p-8">
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
            <div>
              <h2 className="flex items-center gap-2 text-xl font-bold text-navy-950">
                <Send className="text-sky-600" size={21} />
                Notificações no Telegram
              </h2>
              <p className="mt-2 max-w-2xl leading-7 text-slate-700">
                {usuario.telegram_conectado
                  ? `Conectado${usuario.telegram_username ? ` como @${usuario.telegram_username}` : ""}. Seus lembretes serão enviados pelo bot.`
                  : "Conecte sua conta para receber lembretes de prazos e oportunidades salvas."}
              </p>
            </div>
            <TelegramAction connected={usuario.telegram_conectado} />
          </div>
        </section>
        ) : null}
        <AccountSettingsForm usuario={usuario} />
        <section className="rounded-2xl border border-red-200 bg-red-50 p-6 sm:p-8">
          <h2 className="text-xl font-bold text-red-950">Privacidade e dados</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-red-900">
            Ao excluir a conta, seus favoritos, lembretes, buscas salvas e dados
            pessoais serão removidos permanentemente.
          </p>
          <div className="mt-5">
            <DeleteAccountButton />
          </div>
        </section>
      </div>
    </main>
  );
}
