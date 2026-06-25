import type { Licitacao } from "@/types/licitacao";

export function getDeadline(licitacao: Licitacao): string | null {
  const raw = licitacao.dados_originais;
  const exact =
    raw.dataEncerramentoProposta ||
    raw.data_encerramento_proposta ||
    raw.dt_fim_proposta;

  if (typeof exact === "string" && exact) return exact;
  return licitacao.data_encerramento
    ? `${licitacao.data_encerramento}T23:59:59-03:00`
    : null;
}

export function sourceLabel(licitacao: Licitacao): string {
  const isComprasGovOrigin =
    licitacao.fonte === "Compras.gov.br" ||
    licitacao.link_original?.includes("comprasnet-web");
  return licitacao.fonte === "PNCP" && isComprasGovOrigin
    ? "PNCP · Compras.gov.br"
    : licitacao.fonte;
}
