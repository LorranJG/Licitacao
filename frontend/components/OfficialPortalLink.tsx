"use client";

import { ExternalLink } from "lucide-react";

export function OfficialPortalLink({
  href,
  licitacaoId,
  authenticated,
}: {
  href: string;
  licitacaoId: number;
  authenticated: boolean;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      onClick={() => {
        if (!authenticated) return;
        void fetch("/api/conta/eventos", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            nome: "clique_portal_oficial",
            dados: { licitacao_id: licitacaoId },
          }),
          keepalive: true,
        });
      }}
      className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl bg-navy-900 px-5 py-3 text-sm font-bold text-white transition hover:bg-navy-800"
    >
      Acessar portal oficial para enviar proposta
      <ExternalLink aria-hidden="true" size={17} />
    </a>
  );
}
