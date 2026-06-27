from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Licitacao(Base):
    __tablename__ = "licitacoes"
    __table_args__ = (
        UniqueConstraint("fonte", "fonte_id", name="uq_licitacoes_fonte_fonte_id"),
        Index("ix_licitacoes_data_abertura", "data_abertura"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fonte: Mapped[str] = mapped_column(String(50), index=True)
    fonte_id: Mapped[str] = mapped_column(String(160))
    chave_origem: Mapped[str | None] = mapped_column(
        String(220), unique=True, index=True
    )
    titulo: Mapped[str] = mapped_column(Text)
    objeto: Mapped[str | None] = mapped_column(Text)
    orgao: Mapped[str | None] = mapped_column(String(255))
    cnpj_orgao: Mapped[str | None] = mapped_column(String(20))
    modalidade: Mapped[str | None] = mapped_column(String(120), index=True)
    status: Mapped[str | None] = mapped_column(String(80), index=True)
    uf: Mapped[str | None] = mapped_column(String(2), index=True)
    municipio: Mapped[str | None] = mapped_column(String(160))
    valor_estimado: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    data_publicacao: Mapped[date | None] = mapped_column(Date)
    data_abertura: Mapped[date | None] = mapped_column(Date)
    data_encerramento: Mapped[date | None] = mapped_column(Date)
    data_atualizacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    link_original: Mapped[str | None] = mapped_column(Text)
    dados_originais: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    favoritos: Mapped[list["Favorito"]] = relationship(
        back_populates="licitacao", cascade="all, delete-orphan"
    )
    lembretes: Mapped[list["Lembrete"]] = relationship(
        back_populates="licitacao", cascade="all, delete-orphan"
    )
    alertas_busca: Mapped[list["AlertaBusca"]] = relationship(
        back_populates="licitacao", cascade="all, delete-orphan"
    )


class SyncState(Base):
    __tablename__ = "sync_states"

    chave: Mapped[str] = mapped_column(String(100), primary_key=True)
    valor: Mapped[str] = mapped_column(Text)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    senha_hash: Mapped[str | None] = mapped_column(String(255))
    google_sub: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True
    )
    email_verificado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    token_verificacao_hash: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True
    )
    token_verificacao_expira_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    token_redefinicao_hash: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True
    )
    token_redefinicao_expira_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    telefone: Mapped[str | None] = mapped_column(String(30))
    razao_social: Mapped[str | None] = mapped_column(String(255))
    nome_fantasia: Mapped[str | None] = mapped_column(String(255))
    cnpj: Mapped[str | None] = mapped_column(String(18))
    segmentos: Mapped[list[str]] = mapped_column(JSON, default=list)
    ufs_interesse: Mapped[list[str]] = mapped_column(JSON, default=list)
    municipios_interesse: Mapped[list[str]] = mapped_column(JSON, default=list)
    valor_minimo_interesse: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    valor_maximo_interesse: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    palavras_chave: Mapped[list[str]] = mapped_column(JSON, default=list)
    palavras_ignoradas: Mapped[list[str]] = mapped_column(JSON, default=list)
    modalidades_interesse: Mapped[list[str]] = mapped_column(JSON, default=list)
    orgaos_interesse: Mapped[list[str]] = mapped_column(JSON, default=list)
    prazo_minimo_dias: Mapped[int | None] = mapped_column()
    alertar_novas_oportunidades: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
    )
    alertas_antecedencia_horas: Mapped[list[int]] = mapped_column(
        JSON, default=lambda: [168, 72, 24, 2]
    )
    frequencia_resumo: Mapped[str] = mapped_column(
        String(20), default="diario", server_default="diario"
    )
    horario_inicio_alertas: Mapped[str] = mapped_column(
        String(5), default="08:00", server_default="08:00"
    )
    horario_fim_alertas: Mapped[str] = mapped_column(
        String(5), default="20:00", server_default="20:00"
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    acesso_liberado: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    acesso_liberado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    plano_status: Mapped[str] = mapped_column(
        String(30), default="pendente", server_default="pendente"
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True
    )
    stripe_checkout_session_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True
    )
    telegram_chat_id: Mapped[int | None] = mapped_column(
        BigInteger, unique=True, index=True
    )
    telegram_username: Mapped[str | None] = mapped_column(String(160))
    telegram_link_token_hash: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True
    )
    telegram_link_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    favoritos: Mapped[list["Favorito"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    lembretes: Mapped[list["Lembrete"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    buscas_salvas: Mapped[list["BuscaSalva"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    eventos: Mapped[list["EventoProduto"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )


class Favorito(Base):
    __tablename__ = "favoritos"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "licitacao_id", name="uq_favoritos_usuario_licitacao"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    licitacao_id: Mapped[int] = mapped_column(
        ForeignKey("licitacoes.id", ondelete="CASCADE"), index=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    usuario: Mapped[Usuario] = relationship(back_populates="favoritos")
    licitacao: Mapped[Licitacao] = relationship(back_populates="favoritos")


class Lembrete(Base):
    __tablename__ = "lembretes"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    licitacao_id: Mapped[int] = mapped_column(
        ForeignKey("licitacoes.id", ondelete="CASCADE"), index=True
    )
    lembrar_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    mensagem: Mapped[str | None] = mapped_column(String(500))
    enviado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    erro_envio: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    usuario: Mapped[Usuario] = relationship(back_populates="lembretes")
    licitacao: Mapped[Licitacao] = relationship(back_populates="lembretes")


class BuscaSalva(Base):
    __tablename__ = "buscas_salvas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    nome: Mapped[str] = mapped_column(String(120))
    filtros: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    alertas_ativos: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
    )
    ultima_verificacao_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    usuario: Mapped[Usuario] = relationship(back_populates="buscas_salvas")
    alertas: Mapped[list["AlertaBusca"]] = relationship(
        back_populates="busca", cascade="all, delete-orphan"
    )


class AlertaBusca(Base):
    __tablename__ = "alertas_busca"
    __table_args__ = (
        UniqueConstraint(
            "busca_id", "licitacao_id", name="uq_alertas_busca_licitacao"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    busca_id: Mapped[int] = mapped_column(
        ForeignKey("buscas_salvas.id", ondelete="CASCADE"), index=True
    )
    licitacao_id: Mapped[int] = mapped_column(
        ForeignKey("licitacoes.id", ondelete="CASCADE"), index=True
    )
    enviado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    erro_envio: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    busca: Mapped[BuscaSalva] = relationship(back_populates="alertas")
    licitacao: Mapped[Licitacao] = relationship(back_populates="alertas_busca")


class EventoProduto(Base):
    __tablename__ = "eventos_produto"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), index=True
    )
    nome: Mapped[str] = mapped_column(String(80), index=True)
    dados: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    usuario: Mapped[Usuario | None] = relationship(back_populates="eventos")
