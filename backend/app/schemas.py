from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LicitacaoBase(BaseModel):
    fonte: str
    fonte_id: str
    titulo: str
    objeto: str | None = None
    orgao: str | None = None
    cnpj_orgao: str | None = None
    modalidade: str | None = None
    status: str | None = None
    uf: str | None = None
    municipio: str | None = None
    valor_estimado: Decimal | None = None
    data_publicacao: date | None = None
    data_abertura: date | None = None
    data_encerramento: date | None = None
    data_atualizacao: datetime | None = None
    link_original: str | None = None
    dados_originais: dict[str, Any] = Field(default_factory=dict)


class LicitacaoResponse(LicitacaoBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentoResponse(BaseModel):
    titulo: str
    url: str
    tipo: str


class ResumoAutomaticoResponse(BaseModel):
    texto: str
    pontos_chave: list[str]
    pontos_atencao: list[str]


class LicitacaoDetalheResponse(LicitacaoResponse):
    prazo_encerramento: datetime | None = None
    documentos: list[DocumentoResponse] = Field(default_factory=list)
    resumo_automatico: ResumoAutomaticoResponse


class IndicadorItemResponse(BaseModel):
    nome: str
    quantidade: int
    valor_estimado: Decimal = Decimal("0")


class IndicadorMensalResponse(BaseModel):
    periodo: str
    quantidade: int
    valor_estimado: Decimal = Decimal("0")


class IndicadoresResponse(BaseModel):
    total: int
    total_abertas: int
    total_com_valor: int
    valor_total_estimado: Decimal
    valor_medio_estimado: Decimal
    valor_mediano_estimado: Decimal
    publicadas_ultimos_30_dias: int
    publicadas_30_dias_anteriores: int
    variacao_publicacoes_30_dias: Decimal | None = None
    encerram_em_7_dias: int
    encerram_em_30_dias: int
    percentual_com_valor: Decimal
    percentual_com_prazo: Decimal
    data_inicial_base: date | None = None
    data_final_base: date | None = None
    ultima_atualizacao: datetime | None = None
    por_uf: list[IndicadorItemResponse]
    por_modalidade: list[IndicadorItemResponse]
    principais_orgaos: list[IndicadorItemResponse]
    por_fonte: list[IndicadorItemResponse]
    por_status: list[IndicadorItemResponse]
    evolucao_mensal: list[IndicadorMensalResponse]


class ColetaPNCPRequest(BaseModel):
    data_inicial: date | None = None
    data_final: date | None = None
    modalidade_codigo: int | None = Field(default=None, ge=1)


class ColetaPNCPResponse(BaseModel):
    recebidas: int
    criadas: int
    atualizadas: int
    periodo: str


class ColetaComprasGovRequest(BaseModel):
    data_inicial: date | None = None
    data_final: date | None = None


class ColetaComprasGovResponse(BaseModel):
    recebidas: int
    criadas: int
    atualizadas: int
    periodo: str


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str


class UsuarioRegistroRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=160)
    email: str = Field(min_length=5, max_length=255)
    senha: str = Field(min_length=8, max_length=128)


class UsuarioLoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    senha: str = Field(min_length=1, max_length=128)


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(min_length=20)
    nonce: str = Field(min_length=8, max_length=255)


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str | None = None
    razao_social: str | None = None
    nome_fantasia: str | None = None
    cnpj: str | None = None
    segmentos: list[str] = Field(default_factory=list)
    ufs_interesse: list[str] = Field(default_factory=list)
    municipios_interesse: list[str] = Field(default_factory=list)
    valor_minimo_interesse: Decimal | None = None
    valor_maximo_interesse: Decimal | None = None
    palavras_chave: list[str] = Field(default_factory=list)
    palavras_ignoradas: list[str] = Field(default_factory=list)
    modalidades_interesse: list[str] = Field(default_factory=list)
    orgaos_interesse: list[str] = Field(default_factory=list)
    prazo_minimo_dias: int | None = None
    alertar_novas_oportunidades: bool = True
    alertas_antecedencia_horas: list[int] = Field(
        default_factory=lambda: [168, 72, 24, 2]
    )
    frequencia_resumo: str = "diario"
    horario_inicio_alertas: str = "08:00"
    horario_fim_alertas: str = "20:00"
    google_conectado: bool = False
    tem_senha: bool = True
    telegram_conectado: bool = False
    telegram_username: str | None = None
    email_verificado: bool = False
    acesso_liberado: bool = False
    plano_status: str = "pendente"
    acesso_liberado_em: datetime | None = None


class UsuarioUpdateRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=160)
    telefone: str | None = Field(default=None, max_length=30)
    razao_social: str | None = Field(default=None, max_length=255)
    nome_fantasia: str | None = Field(default=None, max_length=255)
    cnpj: str | None = Field(default=None, max_length=18)
    segmentos: list[str] = Field(default_factory=list, max_length=30)
    ufs_interesse: list[str] = Field(default_factory=list, max_length=27)
    municipios_interesse: list[str] = Field(default_factory=list, max_length=100)
    valor_minimo_interesse: Decimal | None = Field(default=None, ge=0)
    valor_maximo_interesse: Decimal | None = Field(default=None, ge=0)
    palavras_chave: list[str] = Field(default_factory=list, max_length=50)
    palavras_ignoradas: list[str] = Field(default_factory=list, max_length=50)
    modalidades_interesse: list[str] = Field(default_factory=list, max_length=30)
    orgaos_interesse: list[str] = Field(default_factory=list, max_length=50)
    prazo_minimo_dias: int | None = Field(default=None, ge=0, le=365)
    alertar_novas_oportunidades: bool = True
    alertas_antecedencia_horas: list[int] = Field(default_factory=list, max_length=10)
    frequencia_resumo: str = Field(pattern="^(nenhum|diario|semanal)$")
    horario_inicio_alertas: str = Field(pattern=r"^\d{2}:\d{2}$")
    horario_fim_alertas: str = Field(pattern=r"^\d{2}:\d{2}$")


class AlterarSenhaRequest(BaseModel):
    senha_atual: str | None = Field(default=None, max_length=128)
    nova_senha: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str


class SolicitarRedefinicaoRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)


class RedefinirSenhaRequest(BaseModel):
    token: str = Field(min_length=20, max_length=255)
    nova_senha: str = Field(min_length=8, max_length=128)


class ConfirmarEmailRequest(BaseModel):
    token: str = Field(min_length=20, max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: UsuarioResponse


class CheckoutResponse(BaseModel):
    url: str


class FavoritoResponse(BaseModel):
    id: int
    criado_em: datetime
    licitacao: LicitacaoResponse

    model_config = ConfigDict(from_attributes=True)


class FavoritoStatusResponse(BaseModel):
    favorito: bool


class LembreteCreateRequest(BaseModel):
    licitacao_id: int = Field(gt=0)
    lembrar_em: datetime
    mensagem: str | None = Field(default=None, max_length=500)


class LembreteResponse(BaseModel):
    id: int
    lembrar_em: datetime
    mensagem: str | None
    enviado_em: datetime | None
    erro_envio: str | None
    criado_em: datetime
    licitacao: LicitacaoResponse

    model_config = ConfigDict(from_attributes=True)


class TelegramLinkResponse(BaseModel):
    url: str
    expira_em: datetime


class TelegramStatusResponse(BaseModel):
    conectado: bool
    username: str | None = None


class BuscaSalvaCreateRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    filtros: dict[str, str | None] = Field(default_factory=dict)
    alertas_ativos: bool = True


class BuscaSalvaUpdateRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    alertas_ativos: bool = True


class BuscaSalvaResponse(BaseModel):
    id: int
    nome: str
    filtros: dict[str, Any]
    alertas_ativos: bool
    ultima_verificacao_em: datetime | None
    criado_em: datetime
    total_correspondencias: int = 0


class EventoCreateRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=80)
    dados: dict[str, Any] = Field(default_factory=dict)


class AtualizacaoFonteResponse(BaseModel):
    fonte: str
    ultima_execucao_em: datetime | None
    status: str
    recebidas: int = 0
    criadas: int = 0
    atualizadas: int = 0
    mensagem: str | None = None


class StatusDadosResponse(BaseModel):
    ultima_licitacao_atualizada_em: datetime | None
    total_licitacoes: int
    fontes: list[AtualizacaoFonteResponse]
