import { ResetPasswordForm } from "@/components/RecoveryForm";

export const metadata = { title: "Redefinir senha" };

export default async function RedefinirSenhaPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token = "" } = await searchParams;
  return (
    <main className="container-page py-16">
      <section className="mx-auto max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-card">
        <h1 className="text-3xl font-bold text-navy-950">Criar nova senha</h1>
        <p className="mt-2 text-slate-600">Use pelo menos oito caracteres.</p>
        <ResetPasswordForm token={token} />
      </section>
    </main>
  );
}
