import {
  ArrowRight,
  Bell,
  Heart,
  LayoutDashboard,
  MapPin,
  Search,
  Settings,
  Timer,
} from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import { LicitacaoCard } from "@/components/LicitacaoCard";
import { getLicitacoes, getIndicadores } from "@/lib/api";
import { getCurrentUser, sessionToken } from "@/lib/session";
import type { LicitacaoFilters } from "@/types/licitacao";

export const metadata = { title: "Dashboard" };

const emptyFilters: LicitacaoFilters = {
  palavra_chave: "",
  uf: "",
  municipio: "",
  orgao: "",
  modalidade: "",
  status: "",
  data_inicio: "",
  data_fim: "",
  encerramento_inicio: "",
  encerramento_fim: "",
  fonte: "",
  valor_minimo: "",
  valor_maximo: "",
};

function saudacao(nome: string): string {
  const hora = new Date().getUTCHours() - 3; // UTC-3
  const primeiroNome = nome.split(" ")[0];
  if (hora >= 5 && hora < 12) return `Bom dia, ${primeiroNome}!`;
  if (hora >= 12 && hora < 18) return `Boa tarde, ${primeiroNome}!`;
  return `Boa noite, ${primeiroNome}!`;
}

function dataISO(delta = 0): string {
  const d = new Date();
  d.setDate(d.getDate() + delta);
  return d.toISOString().split("T")[0];
}

export default async function DashboardPage() {
  const token = await sessionToken();
  if (!token) redirect("/login");
  const usuario = await getCurrentUser();
  if (!usuario) redirect("/login");
  if (!usuario.acesso_liberado) redirect("/comprar");

  const hoje = dataISO(0);
  const em7dias = dataISO(7);

  const temPreferencias =
    usuario.palavras_chave.length > 0 || usuario.ufs_interesse.length > 0;

  const [porPalavra, porRegiao, encerrando, indicadores] = await Promise.all([
    usuario.palavras_chave[0]
      ? getLicitacoes(
          { ...emptyFilters, palavra_chave: usuario.palavras_chave[0], status: "aberta" },
          { page: 1, pageSize: 6 },
          token,
        )
      : null,
    usuario.ufs_interesse[0]
      ? getLicitacoes(
          { ...emptyFilters, uf: usuario.ufs_interesse[0], status: "aberta" },
          { page: 1, pageSize: 6 },
          token,
        )
      : null,
    getLicitacoes(
      {
        ...emptyFilters,
        status: "aberta",
        encerramento_inicio: hoje,
        encerramento_fim: em7dias,
      },
      { page: 1, pageSize: 6 },
      token,
    ),
    getIndicadores("aberta", token),
  ]);

  const stats = [
    {
      label: "Licitações abertas",
      value: indicadores.data?.total_abertas.toLocaleString("pt-BR") ?? "—",
    },
    {
      label: "Encerram em 7 dias",
      value: indicadores.data?.encerram_em_7_dias.toLocaleString("pt-BR") ?? "—",
    },
    {
      label: "Publicadas nos últimos 30 dias",
      value:
        indicadores.data?.publicadas_ultimos_30_dias.toLocaleString("pt-BR") ??
        "—",
    },
  ];

  return (
    <main className="pb-20">
      {/* Header */}
      <section className="border-b border-slate-200 bg-white">
        <div className="container-page py-10 sm:py-14">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-navy-50 text-navy-700">
              <LayoutDashboard aria-hidden="true" size={20} />
            </span>
            <p className="text-sm font-bold uppercase tracking-[0.16em] text-navy-600">
              Seu radar
            </p>
          </div>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
            {saudacao(usuario.nome)}
          </h1>
          <p className="mt-2 text-slate-500">
            Oportunidades selecionadas com base no seu perfil.
          </p>

          {/* Stats */}
          <dl className="mt-8 grid gap-4 sm:grid-cols-3">
            {stats.map(({ label, value }) => (
              <div
                key={label}
                className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card"
              >
                <dt className="text-sm text-slate-500">{label}</dt>
                <dd className="mt-1 font-mono text-2xl font-bold text-navy-950">
                  {value}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <div className="container-page space-y-12 pt-10">
        {/* Atalhos */}
        <div className="flex flex-wrap gap-3">
          <Link
            href="/favoritos"
            className="focus-ring inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-navy-100 hover:text-navy-700"
          >
            <Heart aria-hidden="true" size={16} />
            Favoritos
          </Link>
          <Link
            href="/lembretes"
            className="focus-ring inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-navy-100 hover:text-navy-700"
          >
            <Bell aria-hidden="true" size={16} />
            Lembretes
          </Link>
          <Link
            href="/buscas"
            className="focus-ring inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-navy-100 hover:text-navy-700"
          >
            <Search aria-hidden="true" size={16} />
            Buscas salvas
          </Link>
          <Link
            href="/licitacoes"
            className="focus-ring inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-navy-100 hover:text-navy-700"
          >
            Ver todas as licitações
            <ArrowRight aria-hidden="true" size={16} />
          </Link>
        </div>

        {/* Seção por palavra-chave */}
        {porPalavra && porPalavra.data.length > 0 && (
          <section>
            <div className="mb-5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-navy-50 text-navy-700">
                  <Search aria-hidden="true" size={17} />
                </span>
                <div>
                  <h2 className="font-bold text-navy-950">
                    Resultado para &ldquo;{usuario.palavras_chave[0]}&rdquo;
                  </h2>
                  <p className="text-sm text-slate-500">
                    {porPalavra.total.toLocaleString("pt-BR")} oportunidades abertas
                  </p>
                </div>
              </div>
              <Link
                href={`/licitacoes?palavra_chave=${encodeURIComponent(usuario.palavras_chave[0])}&status=aberta`}
                className="focus-ring hidden items-center gap-1.5 text-sm font-semibold text-navy-700 hover:underline sm:inline-flex"
              >
                Ver todas
                <ArrowRight aria-hidden="true" size={15} />
              </Link>
            </div>
            <div className="grid gap-5 lg:grid-cols-2">
              {porPalavra.data.map((l) => (
                <LicitacaoCard key={l.id} licitacao={l} />
              ))}
            </div>
          </section>
        )}

        {/* Seção por região */}
        {porRegiao && porRegiao.data.length > 0 && (
          <section>
            <div className="mb-5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-navy-50 text-navy-700">
                  <MapPin aria-hidden="true" size={17} />
                </span>
                <div>
                  <h2 className="font-bold text-navy-950">
                    Em {usuario.ufs_interesse[0]}
                  </h2>
                  <p className="text-sm text-slate-500">
                    {porRegiao.total.toLocaleString("pt-BR")} oportunidades abertas
                  </p>
                </div>
              </div>
              <Link
                href={`/licitacoes?uf=${usuario.ufs_interesse[0]}&status=aberta`}
                className="focus-ring hidden items-center gap-1.5 text-sm font-semibold text-navy-700 hover:underline sm:inline-flex"
              >
                Ver todas
                <ArrowRight aria-hidden="true" size={15} />
              </Link>
            </div>
            <div className="grid gap-5 lg:grid-cols-2">
              {porRegiao.data.map((l) => (
                <LicitacaoCard key={l.id} licitacao={l} />
              ))}
            </div>
          </section>
        )}

        {/* Encerrando em breve */}
        {encerrando.data.length > 0 && (
          <section>
            <div className="mb-5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
                  <Timer aria-hidden="true" size={17} />
                </span>
                <div>
                  <h2 className="font-bold text-navy-950">
                    Encerrando esta semana
                  </h2>
                  <p className="text-sm text-slate-500">
                    {encerrando.total.toLocaleString("pt-BR")} licitações encerram nos próximos 7 dias
                  </p>
                </div>
              </div>
              <Link
                href={`/licitacoes?status=aberta&encerramento_inicio=${hoje}&encerramento_fim=${em7dias}`}
                className="focus-ring hidden items-center gap-1.5 text-sm font-semibold text-navy-700 hover:underline sm:inline-flex"
              >
                Ver todas
                <ArrowRight aria-hidden="true" size={15} />
              </Link>
            </div>
            <div className="grid gap-5 lg:grid-cols-2">
              {encerrando.data.map((l) => (
                <LicitacaoCard key={l.id} licitacao={l} />
              ))}
            </div>
          </section>
        )}

        {/* CTA de configuração quando sem preferências */}
        {!temPreferencias && (
          <section className="rounded-2xl border border-dashed border-navy-200 bg-navy-50/50 p-8 text-center">
            <span className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-navy-100 text-navy-700">
              <Settings aria-hidden="true" size={26} />
            </span>
            <h2 className="mt-4 text-xl font-bold text-navy-950">
              Personalize seu radar
            </h2>
            <p className="mt-2 max-w-md mx-auto leading-7 text-slate-600">
              Configure palavras-chave, estados de interesse e tipos de
              licitação para ver oportunidades relevantes direto aqui.
            </p>
            <Link
              href="/conta"
              className="focus-ring mt-5 inline-flex items-center gap-2 rounded-xl bg-navy-900 px-5 py-3 text-sm font-bold text-white transition hover:bg-navy-800"
            >
              <Settings aria-hidden="true" size={16} />
              Configurar preferências
            </Link>
          </section>
        )}
      </div>
    </main>
  );
}
