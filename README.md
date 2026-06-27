# Radar Licitações

MVP SaaS para reunir licitações públicas em uma única plataforma. As fontes
integradas são o Portal Nacional de Contratações Públicas (PNCP) e os módulos
legados de Dados Abertos do Compras.gov.br.

## Tecnologias

- Backend: Python, FastAPI, SQLAlchemy, Pydantic e Alembic
- Banco: PostgreSQL
- Coleta: HTTPX, API pública do PNCP e API de Dados Abertos do Compras.gov.br
- Frontend: Next.js, React, TypeScript e Tailwind CSS
- Infraestrutura local: Docker e Docker Compose

## Rodar com Docker

1. Copie as variáveis de ambiente:

   ```bash
   cp .env.example .env
   ```

   No PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Suba os serviços:

   ```bash
   docker compose up --build
   ```

   Se alguma porta já estiver em uso, ajuste `POSTGRES_PORT`, `BACKEND_PORT`
   ou `FRONTEND_PORT` no `.env`.

3. Acesse:

   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - Swagger: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

O backend executa `alembic upgrade head` automaticamente ao iniciar no Docker.

## Deploy: frontend na Vercel e API na VPS

Use este fluxo para publicar o frontend na Vercel e manter backend e banco no
servidor web.

### VPS

1. Instale Docker, Nginx e Certbot:

   ```bash
   apt update
   apt install -y docker.io docker-compose-plugin nginx certbot python3-certbot-nginx
   ```

2. Clone o projeto e prepare as variaveis da VPS:

   ```bash
   git clone https://github.com/LorranJG/Licitacao.git
   cd Licitacao
   cp .env.vps.example .env.vps
   nano .env.vps
   ```

   Preencha pelo menos `POSTGRES_PASSWORD`, `JWT_SECRET`, `APP_PUBLIC_URL`,
   `BACKEND_PUBLIC_URL` e `CORS_ORIGINS`.

3. Suba PostgreSQL, backend e workers de coleta:

   ```bash
   docker compose --env-file .env.vps -f docker-compose.prod.yml up -d --build
   curl http://127.0.0.1:8000/health
   docker compose --env-file .env.vps -f docker-compose.prod.yml ps
   ```

   Em producao, os workers sobem por padrao. Eles mantem a base atualizada e
   recuperam dias perdidos gradualmente por backfill. Se a pagina mostrar
   `sem_dados` para PNCP ou Compras.gov.br, confirme se os containers
   `pncp-worker`, `pncp-open-worker`, `pncp-backfill-worker`,
   `compras-gov-worker` e `compras-gov-backfill-worker` estao `Up`.

4. Configure o Nginx como proxy reverso:

   ```bash
   cp deploy/nginx/licitacao-api.conf /etc/nginx/sites-available/licitacao-api
   nano /etc/nginx/sites-available/licitacao-api
   ln -s /etc/nginx/sites-available/licitacao-api /etc/nginx/sites-enabled/licitacao-api
   nginx -t
   systemctl reload nginx
   ```

   Troque `api.seu-dominio.com` pelo dominio real antes de recarregar.

5. Ative HTTPS:

   ```bash
   certbot --nginx -d api.seu-dominio.com
   ```

### Vercel

Ao importar o repositorio, configure:

- Root Directory: `frontend`
- Framework Preset: Next.js
- Install Command: `npm install`
- Build Command: `npm run build`

Variaveis de ambiente na Vercel:

```env
NEXT_PUBLIC_API_URL=https://api.seu-dominio.com
API_INTERNAL_URL=https://api.seu-dominio.com
APP_PUBLIC_URL=https://seu-frontend.vercel.app
SESSION_COOKIE_SECURE=true
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### Login com Google em producao

No Google Cloud Console, crie ou edite um cliente OAuth do tipo **Aplicativo da
Web** e cadastre a URI de redirecionamento da Vercel:

```text
https://seu-frontend.vercel.app/api/session/google/callback
```

Se usar dominio proprio no frontend, cadastre tambem:

```text
https://seu-dominio.com/api/session/google/callback
```

Na Vercel, configure:

```env
APP_PUBLIC_URL=https://seu-frontend.vercel.app
GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-client-secret
SESSION_COOKIE_SECURE=true
```

Na VPS, o backend precisa do mesmo `GOOGLE_CLIENT_ID` para validar o token:

```bash
cd /opt/licitacao
nano .env.vps
docker-compose --env-file .env.vps -f docker-compose.prod.yml restart backend
```

Depois de alterar variaveis na Vercel, faca um novo deploy para que o Next.js
use os valores de producao.

Os serviços `pncp-worker`, `pncp-open-worker`, `pncp-backfill-worker`,
`compras-gov-worker` e `compras-gov-backfill-worker` mantêm a base
sincronizada. Por padrão:

- o `pncp-worker` consulta alterações recentes do PNCP a cada 5 minutos;
- o `pncp-open-worker` varre oportunidades com recebimento de propostas aberto;
- o `pncp-backfill-worker` preenche os últimos 30 dias gradualmente, sem
  bloquear as atualizações recentes;
- o `compras-gov-worker` consulta o Compras.gov.br a cada 15 minutos;
- o `compras-gov-backfill-worker` recupera histórico legado em lotes
  gradualmente;
- atualiza registros existentes usando o identificador do PNCP;
- marca como encerradas as oportunidades cuja data de encerramento já passou.
- atualiza automaticamente a página de licitações aberta no navegador a cada
  5 minutos.

Os registros do Compras.gov.br marcados como pertencentes à Lei 14.133 não são
importados novamente, pois já chegam pelo PNCP.

A listagem abre com o status `aberta`. O histórico continua disponível ao
selecionar “Todos os status”. O backfill do Compras.gov.br persiste somente
oportunidades classificadas como abertas.

Esses valores podem ser alterados com `PNCP_SYNC_INTERVAL_SECONDS`,
`PNCP_INITIAL_BACKFILL_DAYS`, `PNCP_BACKFILL_INTERVAL_SECONDS`,
`PNCP_BACKFILL_START_DELAY_SECONDS`, `PNCP_MAX_PAGES`,
`PNCP_REQUEST_DELAY_SECONDS` e
`PNCP_BACKFILL_REQUEST_DELAY_SECONDS`. O progresso histórico fica salvo no
banco e continua do ponto correto após reinícios.

## Rodar o backend manualmente

É necessário ter Python 3.11+ e PostgreSQL em execução.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/radar_licitacoes"
alembic upgrade head
uvicorn app.main:app --reload
```

Teste o health check:

```bash
curl http://localhost:8000/health
```

## Rodar o frontend manualmente

É necessário ter Node.js 20.9+.

```powershell
cd frontend
npm install
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"
$env:API_INTERNAL_URL="http://localhost:8000"
npm run dev
```

## Migrations

Aplicar migrations:

```powershell
cd backend
alembic upgrade head
```

Criar uma nova migration após alterar os models:

```powershell
alembic revision --autogenerate -m "descricao da alteracao"
```

## Coletar licitações do PNCP

Pela API, usando o dia atual e o anterior:

```bash
curl -X POST http://localhost:8000/licitacoes/coletar/pncp \
  -H "Content-Type: application/json" \
  -d "{}"
```

Com período e modalidade específicos:

```bash
curl -X POST http://localhost:8000/licitacoes/coletar/pncp \
  -H "Content-Type: application/json" \
  -d '{"data_inicial":"2026-06-17","data_final":"2026-06-18","modalidade_codigo":6}'
```

Também é possível executar o job diretamente:

```powershell
cd backend
python -m app.jobs.coletar_pncp --data-inicial 2026-06-17 --data-final 2026-06-18
```

## Coletar dados do Compras.gov.br

```bash
curl -X POST http://localhost:8000/licitacoes/coletar/compras-gov \
  -H "Content-Type: application/json" \
  -d '{"data_inicial":"2025-01-01","data_final":"2025-01-31"}'
```

A integração consulta licitações e compras sem licitação dos módulos legados,
enriquece os registros com dados da UASG e cria links para o acompanhamento no
Compras.gov.br.

## Endpoints principais

- `GET /health`
- `GET /licitacoes`
- `GET /licitacoes/{id}`
- `POST /licitacoes/coletar/pncp`
- `POST /licitacoes/coletar/compras-gov`

Filtros disponíveis em `GET /licitacoes`: `palavra_chave`, `uf`, `municipio`,
`modalidade`, `status`, `data_inicio`, `data_fim`, `fonte`, `limite` e `offset`.
O total de registros filtrados é retornado no cabeçalho `X-Total-Count`.

O frontend exibe 20 licitações por página e preserva os filtros ao navegar entre
as páginas.

## Integração com o PNCP

O coletor usa o endpoint oficial
`/api/consulta/v1/contratacoes/publicacao`. Esse endpoint exige uma modalidade
por chamada; por isso o serviço percorre os códigos definidos em
`PNCP_MODALIDADES`.

Pontos que podem exigir ajuste em produção:

- Revisar a lista de modalidades se o catálogo do PNCP mudar.
- Ajustar `PNCP_MAX_PAGES` conforme o volume e os limites operacionais do PNCP.
- Adicionar retentativas com backoff e observabilidade.
- Confirmar periodicamente os nomes dos campos retornados pela API.
- Em múltiplas réplicas, manter apenas uma instância de cada worker.

## Integração com o Compras.gov.br

A integração usa a API oficial em
`https://dadosabertos.compras.gov.br`. Os módulos da Lei 14.133 são evitados
para não duplicar as contratações já recebidas do PNCP. A deduplicação cruzada
também utiliza o identificador interno da compra quando ele aparece no link do
Compras.gov.br.

## Estrutura principal

- `backend/app/routes`: endpoints FastAPI
- `backend/app/services`: cliente PNCP, normalização e persistência
- `backend/app/jobs`: execução manual da coleta
- `backend/alembic`: migrations
- `frontend/app`: páginas do App Router
- `frontend/components`: cards, filtros, header e badges
- `frontend/lib/api.ts`: cliente da API para o frontend

## Próximos passos

- Configurar domínio de envio e chave do Resend para e-mails reais
- Adicionar painel administrativo para métricas e falhas operacionais
- Automatizar backups no provedor escolhido
- Novas fontes públicas além do PNCP
- Testes de integração e monitoramento

## Recursos de validação do MVP

- buscas salvas com alertas sem repetição;
- recuperação de senha e confirmação de e-mail;
- exclusão de conta e páginas de privacidade e termos;
- transparência da última sincronização por fonte;
- eventos básicos de produto, como favoritos e cliques no portal oficial.

Para habilitar e-mails de confirmação, recuperação e alertas:

```env
RESEND_API_KEY=re_...
EMAIL_FROM=Radar Licitações <alertas@seu-dominio.com>
```

### Certificado local do Avast

Quando o Avast estiver com a inspeção HTTPS ativa, ele substitui os certificados
dos sites por certificados assinados pelo `Avast Web/Mail Shield Root`. Para o
ambiente Docker local, use:

```env
RELAX_X509_STRICT=true
```

A imagem inclui essa CA pública e continua validando assinatura, validade e
hostname. Em VPS e produção, mantenha `RELAX_X509_STRICT=false`, pois essa
compatibilidade só é necessária na máquina que utiliza a inspeção do Avast.

## Contas, favoritos e Telegram

O sistema possui cadastro por nome, e-mail e senha. Usuários autenticados podem:

- salvar licitações como favoritas;
- criar lembretes com data, horário e anotação;
- preencher dados pessoais e da empresa;
- configurar segmentos, regiões, valores e palavras-chave de interesse;
- escolher horários e antecedências para notificações;
- alterar a própria senha;
- conectar uma conta do Telegram;
- receber os lembretes pelo bot;
- consultar favoritos pelo comando `/favoritos`.

### Login com Google

O login tradicional por e-mail e senha pode ser usado junto com o Google.
Contas que possuem o mesmo e-mail verificado são vinculadas automaticamente.

1. No Google Cloud Console, crie um cliente OAuth do tipo **Aplicativo da Web**.
2. Cadastre a URI de redirecionamento local:

   ```text
   http://localhost:3001/api/session/google/callback
   ```

3. Preencha no `.env`:

   ```env
   GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=seu-client-secret
   ```

Em produção, cadastre também a URL HTTPS correspondente ao domínio publicado.

Para configurar o bot:

1. Crie um bot com o `@BotFather` no Telegram.
2. Preencha no `.env`:

   ```env
   JWT_SECRET=uma-chave-aleatoria-longa
   APP_PUBLIC_URL=https://seu-frontend.example
   BACKEND_PUBLIC_URL=https://sua-api.example
   TELEGRAM_BOT_TOKEN=token-fornecido-pelo-botfather
   TELEGRAM_BOT_USERNAME=nome_do_seu_bot
   TELEGRAM_WEBHOOK_SECRET=outro-segredo-aleatorio
   SESSION_COOKIE_SECURE=true
   ```

3. Suba os serviços e configure o webhook:

   ```powershell
   docker compose exec backend python -m app.jobs.configurar_telegram
   ```

O serviço `telegram-reminder-worker` verifica lembretes pendentes a cada minuto.
Em desenvolvimento local, o Telegram precisa alcançar uma URL HTTPS pública;
use um túnel ou configure o webhook somente no ambiente publicado.
