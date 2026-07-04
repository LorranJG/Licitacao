import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="container-page flex flex-col justify-between gap-3 py-7 text-sm text-slate-500 sm:flex-row sm:items-center">
        <p>Radar Licitações — dados públicos para apoio à pesquisa.</p>
        <nav className="flex gap-5" aria-label="Informações legais">
          <Link href="/privacidade" className="hover:text-navy-800">
            Privacidade
          </Link>
          <Link href="/termos" className="hover:text-navy-800">
            Termos de uso
          </Link>
          <Link href="/reembolso" className="hover:text-navy-800">
            Reembolso
          </Link>
        </nav>
      </div>
    </footer>
  );
}
