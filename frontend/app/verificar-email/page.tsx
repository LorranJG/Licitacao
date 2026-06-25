import { VerifyEmailForm } from "@/components/RecoveryForm";

export const metadata = { title: "Confirmar e-mail" };

export default async function VerificarEmailPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token = "" } = await searchParams;
  return (
    <main className="container-page py-16">
      <section className="mx-auto max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-card">
        <h1 className="text-3xl font-bold text-navy-950">Confirmar e-mail</h1>
        <p className="mt-2 leading-7 text-slate-600">
          Confirme que este endereço pertence a você.
        </p>
        <VerifyEmailForm token={token} />
      </section>
    </main>
  );
}
