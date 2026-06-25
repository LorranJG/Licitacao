import Link from "next/link";

export default function NotFound() {
  return (
    <main className="container-page flex min-h-[70vh] flex-col items-center justify-center text-center">
      <p className="font-mono text-sm font-bold text-navy-600">ERRO 404</p>
      <h1 className="mt-3 text-4xl font-bold text-navy-950">
        Página não encontrada
      </h1>
      <p className="mt-3 text-slate-600">
        O endereço pode ter mudado ou não existe.
      </p>
      <Link
        href="/"
        className="focus-ring mt-7 rounded-xl bg-navy-900 px-6 py-3 font-bold text-white"
      >
        Voltar ao início
      </Link>
    </main>
  );
}

