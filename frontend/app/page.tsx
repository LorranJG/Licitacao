import {
  Bell,
  BellRing,
  CheckCircle2,
  ChevronDown,
  Clock,
  ExternalLink,
  Heart,
  Search,
  SlidersHorizontal,
  Zap,
} from "lucide-react";
import Link from "next/link";

import { getStatusDados } from "@/lib/api";

const features = [
  {
    icon: Search,
    title: "Busca full-text em português",
    description:
      "Pesquise por palavra-chave, órgão, UF, município, modalidade, valor e prazo — tudo num único filtro inteligente.",
  },
  {
    icon: BellRing,
    title: "Alertas por e-mail e Telegram",
    description:
      "Crie buscas salvas e receba uma notificação sempre que surgir uma nova licitação no seu perfil de interesse.",
  },
  {
    icon: Heart,
    title: "Favoritos e lembretes",
    description:
      "Salve as oportunidades mais relevantes e configure lembretes via Telegram antes do prazo de abertura.",
  },
  {
    icon: SlidersHorizontal,
    title: "Indicadores e dashboard",
    description:
      "Veja em tempo real o volume de abertura, valores médios e ranking por órgão e modalidade.",
  },
  {
    icon: ExternalLink,
    title: "Link direto ao portal oficial",
    description:
      "Cada licitação leva direto ao edital no PNCP ou Compras.gov.br — sem retrabalho de busca manual.",
  },
  {
    icon: Zap,
    title: "Atualizado a cada 15 minutos",
    description:
      "Os coletores rodam automaticamente e sincronizam PNCP e Compras.gov.br dia e noite.",
  },
] as const;

const faqs = [
  {
    q: "Quais fontes de dados são integradas?",
    a: "PNCP (Portal Nacional de Contratações Públicas) e Compras.gov.br. Juntos cobrem a grande maioria das licitações federais, estaduais e municipais publicadas no Brasil.",
  },
  {
    q: "Com que frequência a base é atualizada?",
    a: "A cada 15 minutos durante o dia. Um coletor exclusivo de oportunidades abertas roda a cada 6 horas para garantir que nenhum prazo ativo fique desatualizado.",
  },
  {
    q: "Preciso de CNPJ para usar?",
    a: "Não. Qualquer pessoa pode se cadastrar com e-mail e senha. O CNPJ é opcional e serve apenas para personalizar o perfil de alertas.",
  },
  {
    q: "Como funcionam os alertas?",
    a: "Você cria uma busca salva com os filtros que quiser (palavra-chave, UF, modalidade…). Quando uma nova licitação corresponder, você recebe um e-mail automaticamente. Para lembretes de prazo, basta conectar o Telegram.",
  },
  {
    q: "E se eu quiser cancelar?",
    a: "Sem fidelidade. Pelo Código de Defesa do Consumidor você tem 7 dias de garantia com reembolso total. Fora do prazo legal, basta entrar em contato que analisamos o pedido individualmente.",
  },
] as const;

export default async function Home() {
  const statusDados = await getStatusDados();
  const totalLicitacoes = statusDados?.total_licitacoes ?? null;

  return (
    <main>
      {/* ── HERO ─────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-gradient-to-b from-slate-50 to-white">
        <div className="container-page pb-20 pt-16 sm:pt-24 lg:pb-28 lg:pt-32">
          <div className="grid items-center gap-14 lg:grid-cols-[1.1fr_0.9fr]">
            <div>
              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-navy-100 bg-white px-4 py-2 text-sm font-semibold text-navy-700 shadow-sm">
                <span className="h-2 w-2 rounded-full bg-emerald-500" />
                Atualizado a cada 15 minutos
              </div>

              <h1 className="max-w-3xl text-balance text-5xl font-bold leading-[1.05] tracking-[-0.04em] text-navy-950 sm:text-6xl lg:text-7xl">
                Nunca mais perca uma{" "}
                <span className="text-navy-600">licitação pública.</span>
              </h1>

              <p className="mt-7 max-w-xl text-lg leading-8 text-slate-600 sm:text-xl">
                Radar Licitações reúne PNCP e Compras.gov.br em um só lugar.
                Pesquise, filtre e receba alertas automáticos quando surgir uma
                oportunidade no seu perfil.
              </p>

              <div className="mt-9 flex flex-col gap-4 sm:flex-row">
                <Link
                  href="/cadastro"
                  className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl bg-navy-900 px-7 py-4 font-bold text-white shadow-lg shadow-navy-900/25 transition hover:-translate-y-0.5 hover:bg-navy-800"
                >
                  Começar agora — R$ 49,90/mês
                </Link>
                <a
                  href="#como-funciona"
                  className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-7 py-4 font-semibold text-slate-700 transition hover:border-navy-200 hover:text-navy-800"
                >
                  Ver como funciona
                  <ChevronDown size={17} />
                </a>
              </div>

              <dl className="mt-12 grid max-w-lg grid-cols-3 gap-5 border-t border-slate-200 pt-7">
                <div>
                  <dt className="text-sm text-slate-500">Licitações indexadas</dt>
                  <dd className="mt-1 font-mono text-xl font-bold text-navy-950">
                    {totalLicitacoes !== null
                      ? totalLicitacoes.toLocaleString("pt-BR")
                      : "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-slate-500">Fontes integradas</dt>
                  <dd className="mt-1 font-mono text-xl font-bold text-navy-950">
                    2 fontes
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-slate-500">Cobertura</dt>
                  <dd className="mt-1 font-mono text-xl font-bold text-navy-950">
                    Brasil
                  </dd>
                </div>
              </dl>
            </div>

            {/* Mock UI */}
            <div className="relative">
              <div className="absolute -inset-6 -z-10 rounded-[3rem] bg-navy-100/40 blur-3xl" />
              <div className="overflow-hidden rounded-[2rem] border border-white/80 bg-navy-950 p-3 shadow-2xl shadow-navy-950/25">
                <div className="rounded-[1.5rem] bg-white p-5 sm:p-6">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                    <div>
                      <p className="text-xs font-bold uppercase tracking-widest text-navy-600">
                        Radar de oportunidades
                      </p>
                      <p className="mt-1 text-base font-bold text-navy-950">
                        Licitações em destaque
                      </p>
                    </div>
                    <span className="rounded-lg bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700">
                      Ao vivo
                    </span>
                  </div>
                  <div className="mt-4 space-y-2.5">
                    {[
                      ["Tecnologia e software", "Pregão eletrônico", "SP", "R$ 280.000"],
                      ["Materiais hospitalares", "Concorrência", "MG", "R$ 1.200.000"],
                      ["Serviços de engenharia", "Dispensa", "PR", "R$ 95.000"],
                    ].map(([title, modalidade, uf, valor], i) => (
                      <div
                        key={title}
                        className="flex items-center gap-3 rounded-xl border border-slate-100 p-3.5"
                      >
                        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-navy-50 font-mono text-xs font-bold text-navy-700">
                          {String(i + 1).padStart(2, "0")}
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-semibold text-navy-950">
                            {title}
                          </p>
                          <p className="mt-0.5 text-xs text-slate-400">
                            {modalidade} · {uf}
                          </p>
                        </div>
                        <span className="shrink-0 text-xs font-bold text-slate-500">
                          {valor}
                        </span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 flex items-center gap-2 rounded-xl bg-navy-50 px-4 py-3 text-xs text-navy-700">
                    <Clock size={14} className="shrink-0" />
                    <p>Atualizado há 4 minutos · 2 novas desde ontem</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── PROBLEMA ─────────────────────────────────────────────────── */}
      <section className="border-y border-slate-200 bg-slate-50 py-16 sm:py-20">
        <div className="container-page max-w-4xl text-center">
          <p className="text-sm font-bold uppercase tracking-widest text-navy-600">
            O problema
          </p>
          <h2 className="mt-4 text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
            Monitorar licitações manualmente é inviável.
          </h2>
          <p className="mt-5 text-lg leading-8 text-slate-600">
            PNCP e Compras.gov.br publicam centenas de editais por dia, cada um
            com interface diferente, sem alertas, sem histórico e sem filtros
            úteis. Quem depende de varredura manual perde oportunidades todos os
            dias — simplesmente porque não tem como checar tudo.
          </p>
        </div>

        <div className="container-page mt-12 grid gap-5 sm:grid-cols-3">
          {[
            {
              icon: Clock,
              title: "Horas perdidas por dia",
              text: "Entrar em 2+ portais, aplicar filtros e anotar o que mudou consome tempo que poderia ir para a proposta.",
            },
            {
              icon: Bell,
              title: "Sem alertas automáticos",
              text: "Os portais oficiais não enviam notificação quando surge um edital no seu segmento. Você precisa entrar e checar.",
            },
            {
              icon: SlidersHorizontal,
              title: "Dados fragmentados",
              text: "Uma oportunidade pode estar no PNCP e não no Compras.gov.br e vice-versa. Checar um só portal não basta.",
            },
          ].map(({ icon: Icon, title, text }) => (
            <div
              key={title}
              className="rounded-2xl border border-slate-200 bg-white p-6"
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-50 text-red-500">
                <Icon size={20} />
              </span>
              <h3 className="mt-4 font-bold text-navy-950">{title}</h3>
              <p className="mt-2 text-sm leading-7 text-slate-600">{text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── COMO FUNCIONA ────────────────────────────────────────────── */}
      <section id="como-funciona" className="bg-white py-16 sm:py-24">
        <div className="container-page">
          <div className="max-w-2xl">
            <p className="text-sm font-bold uppercase tracking-widest text-navy-600">
              Como funciona
            </p>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
              Configure uma vez. Receba sempre.
            </h2>
          </div>

          <div className="mt-12 grid gap-8 sm:grid-cols-3">
            {[
              {
                step: "01",
                title: "Crie sua conta",
                text: "Cadastro em menos de 1 minuto com e-mail e senha. Sem burocracia.",
              },
              {
                step: "02",
                title: "Configure seus filtros",
                text: "Defina palavras-chave, UF, modalidade e faixa de valor. O Radar faz o resto.",
              },
              {
                step: "03",
                title: "Receba os alertas",
                text: "Quando uma licitação corresponder ao seu perfil, você recebe um e-mail na hora.",
              },
            ].map(({ step, title, text }) => (
              <div key={step} className="relative">
                <span className="font-mono text-5xl font-black text-navy-100 select-none">
                  {step}
                </span>
                <h3 className="mt-3 text-lg font-bold text-navy-950">{title}</h3>
                <p className="mt-2 leading-7 text-slate-600">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FUNCIONALIDADES ──────────────────────────────────────────── */}
      <section className="border-y border-slate-200 bg-slate-50 py-16 sm:py-24">
        <div className="container-page">
          <div className="max-w-2xl">
            <p className="text-sm font-bold uppercase tracking-widest text-navy-600">
              Funcionalidades
            </p>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
              Tudo que você precisa para monitorar licitações.
            </h2>
          </div>

          <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {features.map(({ icon: Icon, title, description }) => (
              <article
                key={title}
                className="rounded-2xl border border-slate-200 bg-white p-6 transition hover:-translate-y-0.5 hover:border-navy-200"
              >
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-navy-50 text-navy-700">
                  <Icon aria-hidden size={21} />
                </span>
                <h3 className="mt-5 font-bold text-navy-950">{title}</h3>
                <p className="mt-2 text-sm leading-7 text-slate-600">
                  {description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ── PREÇO ────────────────────────────────────────────────────── */}
      <section className="bg-white py-16 sm:py-24">
        <div className="container-page max-w-lg text-center">
          <p className="text-sm font-bold uppercase tracking-widest text-navy-600">
            Preço
          </p>
          <h2 className="mt-4 text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
            Um plano. Acesso completo.
          </h2>

          <div className="mt-10 overflow-hidden rounded-3xl border-2 border-navy-900 bg-white shadow-2xl shadow-navy-900/10">
            <div className="bg-navy-900 px-8 py-5 text-center text-white">
              <p className="text-sm font-bold uppercase tracking-widest text-blue-200">
                Radar Licitações
              </p>
            </div>
            <div className="px-8 py-8">
              <div className="flex items-end justify-center gap-1">
                <span className="text-2xl font-bold text-slate-400">R$</span>
                <span className="text-6xl font-black tracking-tight text-navy-950">
                  49
                </span>
                <span className="mb-2 text-3xl font-bold text-navy-950">,90</span>
                <span className="mb-2 text-base font-semibold text-slate-400">
                  /mês
                </span>
              </div>

              <ul className="mt-8 space-y-3 text-sm text-slate-700">
                {[
                  "Acesso ilimitado à base de licitações",
                  "Busca com 12 filtros combinados",
                  "Alertas por e-mail em tempo real",
                  "Lembretes de prazo via Telegram",
                  "Dashboard e indicadores",
                  "Favoritos e buscas salvas",
                  "Link direto ao edital oficial",
                  "7 dias de garantia (CDC)",
                ].map((item) => (
                  <li key={item} className="flex items-center gap-3">
                    <CheckCircle2
                      className="shrink-0 text-emerald-600"
                      size={17}
                    />
                    {item}
                  </li>
                ))}
              </ul>

              <Link
                href="/cadastro"
                className="focus-ring mt-8 inline-flex h-13 w-full items-center justify-center rounded-xl bg-navy-900 px-6 py-4 font-bold text-white transition hover:bg-navy-800"
              >
                Criar conta e assinar
              </Link>
              <p className="mt-3 text-center text-xs text-slate-400">
                Pagamento pelo Mercado Pago · Cancele quando quiser
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── FAQ ──────────────────────────────────────────────────────── */}
      <section className="border-t border-slate-200 bg-slate-50 py-16 sm:py-24">
        <div className="container-page max-w-3xl">
          <h2 className="text-2xl font-bold tracking-tight text-navy-950 sm:text-3xl">
            Perguntas frequentes
          </h2>
          <div className="mt-8 divide-y divide-slate-200">
            {faqs.map(({ q, a }) => (
              <div key={q} className="py-6">
                <h3 className="font-semibold text-navy-950">{q}</h3>
                <p className="mt-2 leading-7 text-slate-600">{a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA FINAL ────────────────────────────────────────────────── */}
      <section className="bg-white py-16 sm:py-20">
        <div className="container-page">
          <div className="flex flex-col items-center justify-between gap-8 rounded-[2rem] bg-navy-950 px-8 py-12 text-center text-white sm:px-14 lg:flex-row lg:text-left">
            <div className="max-w-xl">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Sua próxima licitação pode já estar publicada.
              </h2>
              <p className="mt-3 text-base leading-7 text-blue-200">
                Configure seus alertas hoje e nunca mais perca um prazo.
              </p>
            </div>
            <Link
              href="/cadastro"
              className="focus-ring inline-flex shrink-0 items-center gap-2 rounded-xl bg-white px-8 py-4 font-bold text-navy-950 transition hover:bg-blue-50"
            >
              Começar agora
              <ExternalLink size={17} />
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
