"use client";

import { Bell, BellRing, Heart, LayoutDashboard, LogOut, Menu, UserRound, X } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

type Props = {
  logado: boolean;
  acessoLiberado: boolean;
};

export function MobileMenu({ logado, acessoLiberado }: Props) {
  const [aberto, setAberto] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    if (!aberto) return;
    function onClickFora(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setAberto(false);
      }
    }
    document.addEventListener("mousedown", onClickFora);
    return () => document.removeEventListener("mousedown", onClickFora);
  }, [aberto]);

  useEffect(() => {
    function onEsc(e: KeyboardEvent) {
      if (e.key === "Escape") setAberto(false);
    }
    document.addEventListener("keydown", onEsc);
    return () => document.removeEventListener("keydown", onEsc);
  }, []);

  async function sair() {
    setAberto(false);
    await fetch("/api/session/logout", { method: "POST" });
    router.push("/");
    router.refresh();
  }

  return (
    <div className="relative xl:hidden" ref={ref}>
      <button
        type="button"
        onClick={() => setAberto((v) => !v)}
        aria-label={aberto ? "Fechar menu" : "Abrir menu"}
        aria-expanded={aberto}
        className="focus-ring flex h-10 w-10 items-center justify-center rounded-lg text-slate-600 hover:bg-slate-100"
      >
        {aberto ? <X size={20} aria-hidden /> : <Menu size={20} aria-hidden />}
      </button>

      {aberto && (
        <div className="absolute right-0 top-12 z-50 w-56 overflow-hidden rounded-xl border border-slate-200 bg-white py-1.5 shadow-xl">
          <Link
            href={logado ? "/conta" : "/"}
            onClick={() => setAberto(false)}
            className="flex items-center gap-3 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            <UserRound size={16} aria-hidden />
            {logado ? "Minha conta" : "Início"}
          </Link>
          <Link
            href="/indicadores"
            onClick={() => setAberto(false)}
            className="flex items-center gap-3 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            Indicadores
          </Link>
          {acessoLiberado && (
            <>
              <Link
                href="/dashboard"
                onClick={() => setAberto(false)}
                className="flex items-center gap-3 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                <LayoutDashboard size={16} aria-hidden />
                Dashboard
              </Link>
              <Link
                href="/favoritos"
                onClick={() => setAberto(false)}
                className="flex items-center gap-3 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                <Heart size={16} aria-hidden />
                Favoritos
              </Link>
              <Link
                href="/lembretes"
                onClick={() => setAberto(false)}
                className="flex items-center gap-3 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                <Bell size={16} aria-hidden />
                Lembretes
              </Link>
              <Link
                href="/buscas"
                onClick={() => setAberto(false)}
                className="flex items-center gap-3 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                <BellRing size={16} aria-hidden />
                Buscas
              </Link>
            </>
          )}
          {logado ? (
            <>
              <div className="my-1.5 border-t border-slate-100" />
              <button
                type="button"
                onClick={sair}
                className="flex w-full items-center gap-3 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                <LogOut size={16} aria-hidden />
                Sair
              </button>
            </>
          ) : (
            <>
              <div className="my-1.5 border-t border-slate-100" />
              <Link
                href="/login"
                onClick={() => setAberto(false)}
                className="flex items-center gap-3 px-4 py-2.5 text-sm font-semibold text-navy-800 hover:bg-slate-50"
              >
                Área do cliente
              </Link>
            </>
          )}
        </div>
      )}
    </div>
  );
}
