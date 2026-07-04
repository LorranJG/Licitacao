import Link from "next/link";

export const metadata = { title: "Política de Reembolso" };

export default function ReembolsoPage() {
  return (
    <main className="container-page max-w-3xl py-12 sm:py-16">
      <h1 className="text-3xl font-bold tracking-tight text-navy-950">
        Política de Reembolso
      </h1>
      <p className="mt-2 text-sm text-slate-400">
        Última atualização: julho de 2026
      </p>

      <div className="mt-8 space-y-8 text-slate-700">
        <section>
          <h2 className="text-lg font-bold text-navy-950">1. Direito de arrependimento</h2>
          <p className="mt-3 leading-7">
            De acordo com o Código de Defesa do Consumidor (Art. 49 da Lei nº 8.078/1990),
            você tem o direito de cancelar a assinatura em até{" "}
            <strong>7 dias corridos</strong> a partir da data da compra, sem
            necessidade de justificativa, com reembolso integral do valor pago.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-navy-950">2. Como solicitar o reembolso</h2>
          <p className="mt-3 leading-7">
            Para solicitar o cancelamento e reembolso dentro do prazo legal, entre em
            contato pelo e-mail informado nos{" "}
            <Link href="/termos" className="font-semibold text-navy-700 underline hover:text-navy-900">
              Termos de Uso
            </Link>{" "}
            com os seguintes dados:
          </p>
          <ul className="mt-3 list-disc space-y-1 pl-6 text-sm leading-7">
            <li>Nome completo cadastrado na conta</li>
            <li>E-mail da conta</li>
            <li>Data da compra</li>
            <li>Comprovante ou número do pagamento (Mercado Pago)</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-bold text-navy-950">3. Prazo de devolução</h2>
          <p className="mt-3 leading-7">
            Após a confirmação da solicitação, o reembolso é processado em até{" "}
            <strong>10 dias úteis</strong>, conforme o prazo operacional do Mercado Pago.
            O valor retorna ao mesmo método de pagamento utilizado na compra.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-navy-950">4. Cancelamento após o prazo</h2>
          <p className="mt-3 leading-7">
            Solicitações de reembolso após os 7 dias corridos não são garantidas por
            lei, mas podem ser analisadas individualmente a critério da equipe do
            Radar Licitações. O acesso permanece ativo até o encerramento da assinatura
            vigente.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-navy-950">5. Suspensão do acesso</h2>
          <p className="mt-3 leading-7">
            Ao confirmar o reembolso, o acesso ao produto é suspenso imediatamente,
            independentemente do período restante da assinatura.
          </p>
        </section>
      </div>

      <div className="mt-10 flex gap-4">
        <Link
          href="/comprar"
          className="focus-ring inline-flex h-11 items-center rounded-xl bg-navy-900 px-5 text-sm font-bold text-white transition hover:bg-navy-800"
        >
          Voltar para compra
        </Link>
        <Link
          href="/termos"
          className="focus-ring inline-flex h-11 items-center rounded-xl border border-slate-200 px-5 text-sm font-bold text-navy-800 transition hover:bg-slate-50"
        >
          Termos de uso
        </Link>
      </div>
    </main>
  );
}
