import { FileHeart, Heart } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import { LicitacaoCard } from "@/components/LicitacaoCard";
import { getAccountData, getCurrentUser } from "@/lib/session";

export const metadata = { title: "Favoritos" };

export default async function FavoritosPage() {
  if (!(await getCurrentUser())) redirect("/login");
  const { favoritos } = await getAccountData();

  return (
    <main className="pb-20">
      <section className="border-b border-slate-200 bg-white">
        <div className="container-page py-10 sm:py-14">
          <p className="flex items-center gap-2 text-sm font-bold uppercase tracking-[0.14em] text-navy-600">
            <Heart aria-hidden="true" size={17} />
            Oportunidades salvas
          </p>
          <div className="mt-3 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <h1 className="text-4xl font-bold text-navy-950">
                Meus favoritos
              </h1>
              <p className="mt-2 max-w-2xl leading-7 text-slate-600">
                Acompanhe com facilidade as licitações que despertaram seu
                interesse.
              </p>
            </div>
            <p className="font-mono text-sm font-semibold text-slate-500">
              {favoritos.length} oportunidade
              {favoritos.length === 1 ? "" : "s"}
            </p>
          </div>
        </div>
      </section>

      <div className="container-page pt-8">
        {favoritos.length ? (
          <div className="grid gap-5 lg:grid-cols-2">
            {favoritos.map((favorito) => (
              <LicitacaoCard
                key={favorito.id}
                licitacao={favorito.licitacao}
              />
            ))}
          </div>
        ) : (
          <div className="flex min-h-80 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
            <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-50 text-rose-600">
              <FileHeart aria-hidden="true" size={27} />
            </span>
            <h2 className="mt-5 text-xl font-bold text-navy-950">
              Nenhuma licitação favorita
            </h2>
            <p className="mt-2 max-w-md leading-7 text-slate-600">
              Salve oportunidades na página de licitações para encontrá-las
              rapidamente aqui.
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
