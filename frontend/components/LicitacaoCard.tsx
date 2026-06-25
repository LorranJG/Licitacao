import {
  Building2,
  CalendarDays,
  Clock3,
  ExternalLink,
  Landmark,
  MapPin,
  WalletCards,
} from "lucide-react";
import Link from "next/link";

import { DeadlineCountdown } from "@/components/DeadlineCountdown";
import { FavoriteButton } from "@/components/FavoriteButton";
import { StatusBadge } from "@/components/StatusBadge";
import { getDeadline, sourceLabel } from "@/lib/licitacao";
import type { Licitacao } from "@/types/licitacao";

type LicitacaoCardProps = {
  licitacao: Licitacao;
};

function formatDate(value: string | null): string {
  if (!value) return "Não informada";
  return new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(
    new Date(`${value}T00:00:00Z`),
  );
}

function formatDateTime(value: string | null): string {
  if (!value) return "Não informada";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Não informada";
  return new Intl.DateTimeFormat("pt-BR", {
    timeZone: "America/Sao_Paulo",
  }).format(date);
}

function formatCurrency(value: string | null): string {
  if (!value) return "Não informado";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Number(value));
}

export function LicitacaoCard({ licitacao }: LicitacaoCardProps) {
  const location = [licitacao.municipio, licitacao.uf]
    .filter(Boolean)
    .join(" / ");
  const deadline = getDeadline(licitacao);

  return (
    <article className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-card transition hover:-translate-y-0.5 hover:border-navy-100 sm:p-7">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <StatusBadge status={licitacao.status} />
          <span className="rounded-full bg-navy-50 px-2.5 py-1 font-mono text-xs font-bold text-navy-700">
            {sourceLabel(licitacao)}
          </span>
        </div>
        <span className="font-mono text-xs text-slate-400">
          #{licitacao.id}
        </span>
      </div>

      <h2 className="mt-5 line-clamp-3 text-xl font-bold leading-7 tracking-tight text-navy-950">
        {licitacao.titulo}
      </h2>

      <div className="mt-5 space-y-3 text-sm text-slate-600">
        <p className="flex items-start gap-3">
          <Building2
            aria-hidden="true"
            className="mt-0.5 shrink-0 text-navy-600"
            size={17}
          />
          <span>{licitacao.orgao || "Órgão não informado"}</span>
        </p>
        <p className="flex items-start gap-3">
          <MapPin
            aria-hidden="true"
            className="mt-0.5 shrink-0 text-navy-600"
            size={17}
          />
          <span>{location || "Local não informado"}</span>
        </p>
        <p className="flex items-start gap-3">
          <Landmark
            aria-hidden="true"
            className="mt-0.5 shrink-0 text-navy-600"
            size={17}
          />
          <span>{licitacao.modalidade || "Modalidade não informada"}</span>
        </p>
      </div>

      <dl className="mt-6 grid grid-cols-2 gap-4 border-y border-slate-100 py-5 sm:grid-cols-3">
        <div>
          <dt className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
            <CalendarDays aria-hidden="true" size={14} />
            Divulgação
          </dt>
          <dd className="mt-2 font-mono text-sm font-semibold text-slate-700">
            {formatDate(licitacao.data_publicacao)}
          </dd>
        </div>
        <div>
          <dt className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
            <Clock3 aria-hidden="true" size={14} />
            Última atualização
          </dt>
          <dd className="mt-2 font-mono text-sm font-semibold text-slate-700">
            {formatDateTime(
              licitacao.data_atualizacao || licitacao.atualizado_em,
            )}
          </dd>
        </div>
        <div className="col-span-2 sm:col-span-1">
          <dt className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
            <WalletCards aria-hidden="true" size={14} />
            Valor estimado
          </dt>
          <dd className="mt-2 font-mono text-sm font-semibold text-slate-700">
            {formatCurrency(licitacao.valor_estimado)}
          </dd>
        </div>
      </dl>

      <div className="mt-auto pt-5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <DeadlineCountdown deadline={deadline} compact />
          <FavoriteButton licitacaoId={licitacao.id} compact />
        </div>
        <p className="mt-2 text-xs leading-5 text-slate-500">
          O status “aberta” indica a situação do processo. Confirme no edital
          se o recebimento de propostas está disponível.
        </p>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <Link
            href={`/licitacoes/${licitacao.id}`}
            className="focus-ring inline-flex items-center justify-center rounded-xl bg-navy-900 px-5 py-3 font-bold text-white transition hover:bg-navy-800"
          >
            Ver detalhes
          </Link>
          {licitacao.link_original ? (
            <a
              href={licitacao.link_original}
              target="_blank"
              rel="noreferrer"
              className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 font-bold text-navy-900 transition hover:border-navy-100 hover:bg-navy-50"
            >
              Conferir no portal
              <ExternalLink aria-hidden="true" size={17} />
            </a>
          ) : (
            <span className="rounded-xl bg-slate-100 px-5 py-3 text-center text-sm font-semibold text-slate-500">
              Link oficial indisponível
            </span>
          )}
        </div>
      </div>
    </article>
  );
}
