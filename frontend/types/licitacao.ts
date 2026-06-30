export type Licitacao = {
  id: number;
  fonte: string;
  fonte_id: string;
  titulo: string;
  objeto: string | null;
  orgao: string | null;
  cnpj_orgao: string | null;
  modalidade: string | null;
  status: string | null;
  uf: string | null;
  municipio: string | null;
  valor_estimado: string | null;
  data_publicacao: string | null;
  data_abertura: string | null;
  data_encerramento: string | null;
  data_atualizacao: string | null;
  link_original: string | null;
  dados_originais?: Record<string, unknown>;
  criado_em: string;
  atualizado_em: string;
};

export type DocumentoLicitacao = {
  titulo: string;
  url: string;
  tipo: string;
};

export type ResumoAutomatico = {
  texto: string;
  pontos_chave: string[];
  pontos_atencao: string[];
};

export type LicitacaoDetalhe = Licitacao & {
  prazo_encerramento: string | null;
  documentos: DocumentoLicitacao[];
  resumo_automatico: ResumoAutomatico;
};

export type IndicadorItem = {
  nome: string;
  quantidade: number;
  valor_estimado: string;
};

export type IndicadorMensal = {
  periodo: string;
  quantidade: number;
  valor_estimado: string;
};

export type Indicadores = {
  total: number;
  total_abertas: number;
  total_com_valor: number;
  valor_total_estimado: string;
  valor_medio_estimado: string;
  valor_mediano_estimado: string;
  publicadas_ultimos_30_dias: number;
  publicadas_30_dias_anteriores: number;
  variacao_publicacoes_30_dias: string | null;
  encerram_em_7_dias: number;
  encerram_em_30_dias: number;
  percentual_com_valor: string;
  percentual_com_prazo: string;
  data_inicial_base: string | null;
  data_final_base: string | null;
  ultima_atualizacao: string | null;
  por_uf: IndicadorItem[];
  por_modalidade: IndicadorItem[];
  principais_orgaos: IndicadorItem[];
  por_fonte: IndicadorItem[];
  por_status: IndicadorItem[];
  evolucao_mensal: IndicadorMensal[];
};

export type LicitacaoFilters = {
  palavra_chave: string;
  uf: string;
  municipio: string;
  orgao: string;
  modalidade: string;
  status: string;
  data_inicio: string;
  data_fim: string;
  encerramento_inicio: string;
  encerramento_fim: string;
  fonte: string;
  valor_minimo: string;
  valor_maximo: string;
};

export type LicitacaoPagination = {
  page: number;
  pageSize: number;
};

export type Usuario = {
  id: number;
  nome: string;
  email: string;
  telefone: string | null;
  razao_social: string | null;
  nome_fantasia: string | null;
  cnpj: string | null;
  segmentos: string[];
  ufs_interesse: string[];
  municipios_interesse: string[];
  valor_minimo_interesse: string | null;
  valor_maximo_interesse: string | null;
  palavras_chave: string[];
  palavras_ignoradas: string[];
  modalidades_interesse: string[];
  orgaos_interesse: string[];
  prazo_minimo_dias: number | null;
  alertar_novas_oportunidades: boolean;
  alertas_antecedencia_horas: number[];
  frequencia_resumo: "nenhum" | "diario" | "semanal";
  horario_inicio_alertas: string;
  horario_fim_alertas: string;
  google_conectado: boolean;
  tem_senha: boolean;
  telegram_conectado: boolean;
  telegram_username: string | null;
  email_verificado: boolean;
  acesso_liberado: boolean;
  plano_status: string;
  acesso_liberado_em: string | null;
};

export type Favorito = {
  id: number;
  criado_em: string;
  licitacao: Licitacao;
};

export type Lembrete = {
  id: number;
  lembrar_em: string;
  mensagem: string | null;
  enviado_em: string | null;
  erro_envio: string | null;
  criado_em: string;
  licitacao: Licitacao;
};

export type BuscaSalva = {
  id: number;
  nome: string;
  filtros: Record<string, string>;
  alertas_ativos: boolean;
  ultima_verificacao_em: string | null;
  criado_em: string;
  total_correspondencias: number;
};

export type AtualizacaoFonte = {
  fonte: string;
  ultima_execucao_em: string | null;
  status: string;
  recebidas: number;
  criadas: number;
  atualizadas: number;
  mensagem: string | null;
};

export type StatusDados = {
  ultima_licitacao_atualizada_em: string | null;
  total_licitacoes: number;
  fontes: AtualizacaoFonte[];
};
