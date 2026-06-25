export const metadata = { title: "Termos de uso" };

export default function TermosPage() {
  return (
    <main className="container-page py-14">
      <article className="mx-auto max-w-3xl rounded-2xl border border-slate-200 bg-white p-7 shadow-card sm:p-10">
        <h1 className="text-3xl font-bold text-navy-950">Termos de uso</h1>
        <div className="mt-6 space-y-5 leading-7 text-slate-700">
          <p>
            O Radar reúne e organiza informações de fontes públicas. O edital e
            o portal oficial do órgão sempre prevalecem sobre qualquer resumo,
            prazo ou classificação apresentada aqui.
          </p>
          <p>
            O Radar não recebe propostas, não representa órgãos públicos e não
            garante habilitação, participação ou vitória em processos
            licitatórios.
          </p>
          <p>
            Alertas são recursos auxiliares e podem sofrer atrasos por falhas de
            terceiros, indisponibilidade das fontes ou configurações do usuário.
          </p>
          <p>
            O usuário é responsável por conferir o edital, manter seus dados
            seguros e utilizar a plataforma de acordo com a legislação.
          </p>
          <p>
            Durante a fase de testes, funcionalidades podem mudar ou ficar
            temporariamente indisponíveis.
          </p>
        </div>
      </article>
    </main>
  );
}
