import {
  BellRing,
  Building2,
  ExternalLink,
  Search,
  SlidersHorizontal,
} from "lucide-react";
import Link from "next/link";

import { getStatusDados } from "@/lib/api";

const features = [
  {
    title: "Busca centralizada",
    description:
      "Oportunidades de diferentes órgãos reunidas em uma visão simples.",
    icon: Search,
  },
  {
    title: "Filtros inteligentes",
    description:
      "Encontre processos por palavra-chave, estado, modalidade e status.",
    icon: SlidersHorizontal,
  },
  {
    title: "Portal oficial",
    description:
      "Acesse a publicação original para conferir edital e documentos.",
    icon: ExternalLink,
  },
  {
    title: "Alertas futuros",
    description:
      "Estrutura pronta para receber favoritos e avisos personalizados.",
    icon: BellRing,
  },
] as const;

export default async function Home() {
  const statusDados = await getStatusDados();
  const totalLicitacoes = statusDados?.total_licitacoes ?? null;
  return (
    <main>
      <section className="container-page pb-20 pt-16 sm:pt-24 lg:pb-28 lg:pt-32">
        <div className="grid items-center gap-14 lg:grid-cols-[1.15fr_0.85fr]">
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-navy-100 bg-white px-4 py-2 text-sm font-semibold text-navy-700 shadow-sm">
              <span className="h-2 w-2 rounded-full bg-mint-500" />
              Dados públicos, oportunidades reais
            </div>
            <h1 className="max-w-4xl text-balance text-5xl font-bold leading-[1.05] tracking-[-0.045em] text-navy-950 sm:text-6xl lg:text-7xl">
              Licitações públicas,{" "}
              <span className="text-navy-600">sem o ruído.</span>
            </h1>
            <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-600 sm:text-xl">
              Encontre licitações públicas em uma única plataforma. Pesquise,
              filtre e vá direto à fonte oficial quando surgir a oportunidade
              certa.
            </p>
            <div className="mt-9 flex flex-col gap-4 sm:flex-row">
              <Link
                href="/licitacoes"
                className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl bg-navy-900 px-6 py-3.5 font-semibold text-white shadow-lg shadow-navy-900/20 transition hover:-translate-y-0.5 hover:bg-navy-800"
              >
                Ver licitações
                <ExternalLink aria-hidden="true" size={18} />
              </Link>
              <a
                href="#como-funciona"
                className="focus-ring inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-6 py-3.5 font-semibold text-slate-700 transition hover:border-navy-100 hover:text-navy-700"
              >
                Conhecer a plataforma
              </a>
            </div>
            <dl className="mt-12 grid max-w-xl grid-cols-3 gap-5 border-t border-slate-200 pt-7">
              <div>
                <dt className="text-sm text-slate-500">Licitações indexadas</dt>
                <dd className="mt-1 font-mono text-lg font-semibold text-navy-950">
                  {totalLicitacoes !== null
                    ? totalLicitacoes.toLocaleString("pt-BR")
                    : "—"}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-slate-500">Fontes integradas</dt>
                <dd className="mt-1 font-mono text-lg font-semibold text-navy-950">
                  2 fontes
                </dd>
              </div>
              <div>
                <dt className="text-sm text-slate-500">Cobertura</dt>
                <dd className="mt-1 font-mono text-lg font-semibold text-navy-950">
                  Brasil
                </dd>
              </div>
            </dl>
          </div>

          <div className="relative">
            <div className="absolute -inset-5 -z-10 rounded-[2.5rem] bg-navy-100/50 blur-2xl" />
            <div className="overflow-hidden rounded-[2rem] border border-white/80 bg-navy-950 p-3 shadow-2xl shadow-navy-950/20">
              <div className="rounded-[1.4rem] bg-white p-5 sm:p-7">
                <div className="flex items-center justify-between border-b border-slate-100 pb-5">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-[0.16em] text-navy-600">
                      Radar de oportunidades
                    </p>
                    <p className="mt-1 text-lg font-bold text-navy-950">
                      Licitações em destaque
                    </p>
                  </div>
                  <span className="rounded-lg bg-mint-50 px-3 py-1.5 text-xs font-bold text-mint-600">
                    Atualizado
                  </span>
                </div>
                <div className="space-y-3 pt-5">
                  {[
                    ["Tecnologia e software", "Pregão eletrônico", "SP"],
                    ["Materiais hospitalares", "Concorrência", "MG"],
                    ["Serviços de engenharia", "Dispensa", "PR"],
                  ].map(([title, modalidade, uf], index) => (
                    <div
                      key={title}
                      className="group flex items-center gap-4 rounded-xl border border-slate-100 p-4 transition hover:border-navy-100 hover:bg-navy-50/40"
                    >
                      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-navy-50 font-mono text-sm font-bold text-navy-700">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate font-semibold text-navy-950">
                          {title}
                        </p>
                        <p className="mt-1 text-sm text-slate-500">
                          {modalidade}
                        </p>
                      </div>
                      <span className="font-mono text-sm font-bold text-slate-400">
                        {uf}
                      </span>
                    </div>
                  ))}
                </div>
                <div className="mt-5 flex items-center gap-3 rounded-xl bg-navy-50 p-4 text-sm text-navy-800">
                  <Building2 aria-hidden="true" className="shrink-0" size={20} />
                  <p>
                    Informações normalizadas com acesso à publicação oficial.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        id="como-funciona"
        className="border-y border-slate-200 bg-white py-20 sm:py-24"
      >
        <div className="container-page">
          <div className="max-w-2xl">
            <p className="text-sm font-bold uppercase tracking-[0.16em] text-navy-600">
              Tudo em um só radar
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
              Menos tempo procurando. Mais tempo decidindo.
            </h2>
          </div>
          <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {features.map(({ title, description, icon: Icon }, index) => (
              <article
                key={title}
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card transition hover:-translate-y-1 hover:border-navy-100"
              >
                <div className="flex items-center justify-between">
                  <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-navy-50 text-navy-700">
                    <Icon aria-hidden="true" size={21} />
                  </span>
                  <span className="font-mono text-xs text-slate-400">
                    0{index + 1}
                  </span>
                </div>
                <h3 className="mt-6 text-lg font-bold text-navy-950">{title}</h3>
                <p className="mt-2 leading-7 text-slate-600">{description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="container-page py-20 sm:py-24">
        <div className="flex flex-col items-start justify-between gap-8 rounded-[2rem] bg-navy-950 px-7 py-10 text-white sm:px-12 sm:py-12 lg:flex-row lg:items-center">
          <div className="max-w-2xl">
            <p className="text-sm font-bold uppercase tracking-[0.16em] text-blue-300">
              Comece agora
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight">
              Sua próxima oportunidade pode já estar publicada.
            </h2>
          </div>
          <Link
            href="/licitacoes"
            className="focus-ring inline-flex shrink-0 items-center gap-2 rounded-xl bg-white px-6 py-3.5 font-bold text-navy-950 transition hover:bg-blue-50"
          >
            Explorar licitações
            <ExternalLink aria-hidden="true" size={18} />
          </Link>
        </div>
      </section>
    </main>
  );
}
