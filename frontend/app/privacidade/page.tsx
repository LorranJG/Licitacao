export const metadata = { title: "Política de privacidade" };

export default function PrivacidadePage() {
  return (
    <main className="container-page py-14">
      <article className="mx-auto max-w-3xl rounded-2xl border border-slate-200 bg-white p-7 shadow-card sm:p-10">
        <h1 className="text-3xl font-bold text-navy-950">Política de privacidade</h1>
        <div className="mt-6 space-y-5 leading-7 text-slate-700">
          <p>
            O Radar utiliza os dados informados para autenticação, personalização
            de buscas, favoritos, lembretes e envio de alertas solicitados.
          </p>
          <p>
            Senhas são armazenadas somente em formato protegido. Tokens de
            confirmação e recuperação são temporários e também não são
            armazenados em texto puro.
          </p>
          <p>
            Dados podem ser enviados aos provedores escolhidos para autenticação
            e notificações, como Google, Telegram e o serviço de e-mail
            configurado. Não vendemos dados pessoais.
          </p>
          <p>
            O usuário pode excluir sua conta na área “Minha conta”. Essa ação
            remove dados pessoais, favoritos, lembretes e buscas salvas.
          </p>
          <p>
            Esta é uma versão inicial para testes do produto e deve ser revisada
            juridicamente antes de uma operação comercial ampla.
          </p>
        </div>
      </article>
    </main>
  );
}
