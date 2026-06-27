import {
  AlertTriangle,
  ArrowLeft,
  Building2,
  CalendarDays,
  CheckCircle2,
  CircleHelp,
  ExternalLink,
  FileText,
  Landmark,
  MapPin,
  Sparkles,
  WalletCards,
} from "lucide-react";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { DeadlineCountdown } from "@/components/DeadlineCountdown";
import { FavoriteButton } from "@/components/FavoriteButton";
import { ReminderForm } from "@/components/ReminderForm";
import { OfficialPortalLink } from "@/components/OfficialPortalLink";
import { StatusBadge } from "@/components/StatusBadge";
import { getLicitacao } from "@/lib/api";
import { sourceLabel } from "@/lib/licitacao";
import { getCurrentUser, sessionToken } from "@/lib/session";

type DetailPageProps = {
  params: Promise<{ id: string }>;
};

function formatDate(value: string | null): string {
  if (!value) return "Não informada";
  return new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(
    new Date(`${value}T00:00:00Z`),
  );
}

function formatDateTime(value: string | null): string {
  if (!value) return "Não informada";
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
    timeZone: "America/Sao_Paulo",
  }).format(new Date(value));
}

function formatCurrency(value: string | null): string {
  if (!value) return "Não informado";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Number(value));
}

export default async function LicitacaoDetailPage({ params }: DetailPageProps) {
  const { id } = await params;
  const numericId = Number(id);
  if (!Number.isInteger(numericId) || numericId <= 0) notFound();

  const token = await sessionToken();
  if (!token) redirect("/login");
  const usuario = await getCurrentUser();
  if (!usuario) redirect("/login");
  if (!usuario.acesso_liberado) redirect("/comprar");

  const result = await getLicitacao(numericId, token);
  if (result.notFound) notFound();

  if (!result.data) {
    return (
      <main className="container-page py-16">
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-8">
          <h1 className="text-2xl font-bold text-amber-950">
            Não foi possível carregar a licitação
          </h1>
          <p className="mt-2 text-amber-900">{result.error}</p>
          <Link href="/licitacoes" className="mt-6 inline-flex font-bold text-navy-700">
            Voltar para a busca
          </Link>
        </div>
      </main>
    );
  }

  const licitacao = result.data;
  const location = [licitacao.municipio, licitacao.uf]
    .filter(Boolean)
    .join(" / ");
  const facts = [
    { icon: Building2, label: "Órgão", value: licitacao.orgao || "Não informado" },
    { icon: MapPin, label: "Local", value: location || "Não informado" },
    {
      icon: Landmark,
      label: "Modalidade",
      value: licitacao.modalidade || "Não informada",
    },
    {
      icon: WalletCards,
      label: "Valor estimado",
      value: formatCurrency(licitacao.valor_estimado),
    },
    {
      icon: CalendarDays,
      label: "Divulgação",
      value: formatDate(licitacao.data_publicacao),
    },
    {
      icon: CalendarDays,
      label: "Prazo informado para propostas",
      value: formatDateTime(licitacao.prazo_encerramento),
    },
  ];

  return (
    <main className="pb-20">
      <section className="border-b border-slate-200 bg-white">
        <div className="container-page py-10 sm:py-14">
          <Link
            href="/licitacoes"
            className="focus-ring inline-flex items-center gap-2 rounded-lg text-sm font-bold text-navy-700"
          >
            <ArrowLeft aria-hidden="true" size={17} />
            Voltar às licitações
          </Link>
          <div className="mt-7 flex flex-wrap items-center gap-2">
            <StatusBadge status={licitacao.status} />
            <span className="rounded-full bg-navy-50 px-3 py-1 font-mono text-xs font-bold text-navy-700">
              {sourceLabel(licitacao)}
            </span>
            <span className="font-mono text-xs text-slate-400">
              #{licitacao.id}
            </span>
          </div>
          <h1 className="mt-5 max-w-5xl text-3xl font-bold leading-tight tracking-tight text-navy-950 sm:text-4xl">
            {licitacao.titulo}
          </h1>
          <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center">
            <DeadlineCountdown deadline={licitacao.prazo_encerramento} />
            <FavoriteButton licitacaoId={licitacao.id} />
            {licitacao.link_original ? (
              <OfficialPortalLink
                href={licitacao.link_original}
                licitacaoId={licitacao.id}
                authenticated={Boolean(usuario)}
              />
            ) : null}
          </div>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-500">
            O selo “aberta” indica a situação geral do processo e não garante,
            sozinho, que o envio de propostas ainda esteja disponível.
          </p>
        </div>
      </section>

      <div className="container-page grid gap-7 pt-8 lg:grid-cols-[1fr_360px]">
        <div className="space-y-7">
          <section className="rounded-2xl border border-sky-200 bg-sky-50 p-6 sm:p-8">
            <div className="flex items-start gap-4">
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white text-sky-700">
                <CircleHelp aria-hidden="true" size={22} />
              </span>
              <div>
                <h2 className="text-xl font-bold text-navy-950">
                  Como participar desta licitação
                </h2>
                <p className="mt-2 leading-7 text-slate-700">
                  Você pode enviar a proposta enquanto o portal oficial aceitar
                  documentos e o prazo do edital não tiver encerrado. O Radar
                  não recebe propostas: o envio acontece exclusivamente na
                  plataforma indicada pelo órgão.
                </p>
                <ol className="mt-4 space-y-2 text-sm leading-6 text-slate-700">
                  <li>
                    <strong>1.</strong> Confira o prazo, os itens e os requisitos
                    de habilitação no edital.
                  </li>
                  <li>
                    <strong>2.</strong> Verifique se sua empresa está cadastrada
                    e habilitada na plataforma indicada.
                  </li>
                  <li>
                    <strong>3.</strong> Envie a proposta no portal oficial e
                    acompanhe a sessão pública, quando aplicável.
                  </li>
                </ol>
                <p className="mt-4 text-xs leading-5 text-slate-500">
                  Em caso de divergência, as datas e regras publicadas no edital
                  e no portal oficial sempre prevalecem.
                </p>
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-navy-100 bg-white p-6 shadow-card sm:p-8">
            <div className="flex items-center gap-3">
              <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-navy-50 text-navy-700">
                <Sparkles aria-hidden="true" size={21} />
              </span>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.14em] text-navy-600">
                  Leitura rápida
                </p>
                <h2 className="text-xl font-bold text-navy-950">
                  Resumo automático
                </h2>
              </div>
            </div>
            <p className="mt-5 text-base leading-8 text-slate-700">
              {licitacao.resumo_automatico.texto}
            </p>
            <div className="mt-6 grid gap-5 md:grid-cols-2">
              <div className="rounded-xl bg-mint-50 p-5">
                <h3 className="flex items-center gap-2 font-bold text-mint-600">
                  <CheckCircle2 aria-hidden="true" size={18} />
                  Pontos principais
                </h3>
                <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
                  {licitacao.resumo_automatico.pontos_chave.map((item) => (
                    <li key={item}>• {item}</li>
                  ))}
                </ul>
              </div>
              <div className="rounded-xl bg-amber-50 p-5">
                <h3 className="flex items-center gap-2 font-bold text-amber-800">
                  <AlertTriangle aria-hidden="true" size={18} />
                  Pontos de atenção
                </h3>
                <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
                  {licitacao.resumo_automatico.pontos_atencao.map((item) => (
                    <li key={item}>• {item}</li>
                  ))}
                </ul>
              </div>
            </div>
            <p className="mt-5 text-xs leading-5 text-slate-400">
              Resumo gerado a partir dos dados públicos. O edital oficial
              prevalece em caso de divergência.
            </p>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8">
            <h2 className="text-xl font-bold text-navy-950">
              Objeto da contratação
            </h2>
            <p className="mt-4 whitespace-pre-line leading-8 text-slate-700">
              {licitacao.objeto || licitacao.titulo}
            </p>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8">
            <h2 className="flex items-center gap-2 text-xl font-bold text-navy-950">
              <FileText aria-hidden="true" size={21} />
              Documentos e links
            </h2>
            {licitacao.documentos.length > 0 ? (
              <div className="mt-5 divide-y divide-slate-100 rounded-xl border border-slate-200">
                {licitacao.documentos.map((documento) => (
                  <a
                    key={documento.url}
                    href={documento.url}
                    target="_blank"
                    rel="noreferrer"
                    className="focus-ring flex items-center justify-between gap-4 px-5 py-4 font-semibold text-navy-800 transition hover:bg-navy-50"
                  >
                    <span>{documento.titulo}</span>
                    <ExternalLink aria-hidden="true" className="shrink-0" size={17} />
                  </a>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-slate-500">
                Nenhum documento ou link foi informado pela fonte.
              </p>
            )}
          </section>
        </div>

        <aside>
          <div className="space-y-5">
            <section className="rounded-2xl border border-slate-200 bg-white p-6">
              <h2 className="font-bold text-navy-950">
                Dados da oportunidade
              </h2>
              <dl className="mt-5 space-y-5 text-sm">
                {facts.map(({ icon: Icon, label, value }) => (
                  <div key={label} className="flex items-start gap-3">
                    <Icon
                      aria-hidden="true"
                      className="mt-0.5 shrink-0 text-navy-600"
                      size={17}
                    />
                    <div>
                      <dt className="text-xs font-bold uppercase tracking-wide text-slate-400">
                        {label}
                      </dt>
                      <dd className="mt-1 leading-6 text-slate-700">{value}</dd>
                    </div>
                  </div>
                ))}
              </dl>
            </section>
            <ReminderForm
              licitacaoId={licitacao.id}
              deadline={licitacao.prazo_encerramento}
              telegramConnected={usuario?.telegram_conectado ?? false}
            />
          </div>
        </aside>
      </div>
    </main>
  );
}
