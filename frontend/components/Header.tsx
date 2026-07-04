import { Bell, BellRing, Heart, LayoutDashboard, Radar, UserRound } from "lucide-react";
import Link from "next/link";

import { LogoutButton } from "@/components/AccountActions";
import { MobileMenu } from "@/components/MobileMenu";
import { getCurrentUser } from "@/lib/session";

export async function Header() {
  const usuario = await getCurrentUser();
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
      <div className="container-page flex h-[72px] items-center justify-between py-4">
        <Link
          href={usuario ? "/licitacoes" : "/"}
          className="focus-ring flex items-center gap-3 rounded-lg"
          aria-label="Radar Licitações — página inicial"
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-navy-900 text-white">
            <Radar aria-hidden="true" size={22} />
          </span>
          <span>
            <span className="block text-base font-extrabold leading-none tracking-tight text-navy-950">
              Radar Licitações
            </span>
            <span className="mt-1 block text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
              Oportunidades públicas
            </span>
          </span>
        </Link>
        <nav aria-label="Navegação principal" className="flex items-center gap-2">
          <Link
            href={usuario ? "/conta" : "/"}
            className="focus-ring hidden items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-navy-900 sm:inline-flex"
          >
            {usuario ? <UserRound aria-hidden="true" size={17} /> : null}
            {usuario ? "Minha conta" : "Início"}
          </Link>
          <Link
            href="/indicadores"
            className="focus-ring hidden rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-navy-900 xl:block"
          >
            Indicadores
          </Link>
          {usuario?.acesso_liberado ? (
            <>
              <Link
                href="/dashboard"
                className="focus-ring hidden items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-navy-900 sm:inline-flex"
              >
                <LayoutDashboard aria-hidden="true" size={17} />
                Dashboard
              </Link>
              <Link
                href="/favoritos"
                className="focus-ring hidden items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-navy-900 md:inline-flex"
              >
                <Heart aria-hidden="true" size={17} />
                Favoritos
              </Link>
              <Link
                href="/lembretes"
                className="focus-ring hidden items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-navy-900 lg:inline-flex"
              >
                <Bell aria-hidden="true" size={17} />
                Lembretes
              </Link>
              <Link
                href="/buscas"
                className="focus-ring hidden items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-navy-900 xl:inline-flex"
              >
                <BellRing aria-hidden="true" size={17} />
                Buscas
              </Link>
            </>
          ) : null}
          <Link
            href={usuario && !usuario.acesso_liberado ? "/comprar" : "/licitacoes"}
            className="focus-ring rounded-lg bg-navy-900 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-navy-800"
          >
            {usuario && !usuario.acesso_liberado ? "Comprar" : "Ver licitações"}
          </Link>
          {usuario ? (
            <span className="hidden xl:block">
              <LogoutButton />
            </span>
          ) : (
            <Link
              href="/login"
              className="focus-ring hidden rounded-lg px-3 py-2 text-sm font-bold text-navy-800 hover:bg-navy-50 xl:block"
            >
              Área do cliente
            </Link>
          )}
          <MobileMenu
            logado={!!usuario}
            acessoLiberado={!!usuario?.acesso_liberado}
          />
        </nav>
      </div>
    </header>
  );
}
