from functools import lru_cache
from typing import Annotated

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Radar Licitações API"
    app_version: str = "0.1.0"
    environment: str = "development"
    app_timezone: str = "America/Sao_Paulo"
    database_url: str = (
        "postgresql://postgres:postgres@localhost:5432/radar_licitacoes"
    )
    jwt_secret: str = "troque-esta-chave-em-producao"
    jwt_expiration_hours: int = 168
    app_public_url: str = "http://localhost:3000"
    backend_public_url: str = "http://localhost:8000"
    google_client_id: str | None = None
    resend_api_key: str | None = None
    email_from: str = "Radar Licitações <onboarding@resend.dev>"
    relax_x509_strict: bool = False
    telegram_bot_token: str | None = None
    telegram_bot_username: str | None = None
    telegram_webhook_secret: str | None = None
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_id: str | None = None
    pncp_base_url: str = "https://pncp.gov.br/api/consulta"
    pncp_modalidades: Annotated[list[int], NoDecode] = list(range(1, 14))
    pncp_max_pages: int = 100
    pncp_sync_interval_seconds: int = 900
    pncp_open_sync_interval_seconds: int = 21600
    pncp_open_start_delay_seconds: int = 600
    pncp_open_horizon_days: int = 180
    pncp_open_max_pages: int = 500
    pncp_initial_backfill_days: int = 30
    pncp_backfill_interval_seconds: int = 900
    pncp_backfill_start_delay_seconds: int = 120
    pncp_request_delay_seconds: float = 1.5
    compras_gov_base_url: str = "https://dadosabertos.compras.gov.br"
    compras_gov_max_pages: int = 100
    compras_gov_sync_interval_seconds: int = 900
    compras_gov_sync_lookback_days: int = 7
    compras_gov_initial_backfill_days: int = 730
    compras_gov_backfill_chunk_days: int = 90
    compras_gov_backfill_interval_seconds: int = 900
    compras_gov_backfill_start_delay_seconds: int = 300
    compras_gov_request_delay_seconds: float = 0.5
    compras_gov_uasg_enrichment_limit: int = 50
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("pncp_modalidades", mode="before")
    @classmethod
    def parse_modalidades(cls, value: object) -> object:
        if isinstance(value, str):
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.environment.lower() != "production":
            return self
        if (
            self.jwt_secret == "troque-esta-chave-em-producao"
            or self.jwt_secret.startswith("troque-")
            or len(self.jwt_secret) < 32
        ):
            raise ValueError(
                "JWT_SECRET precisa ter pelo menos 32 caracteres em producao."
            )
        if "*" in self.cors_origins:
            raise ValueError("CORS_ORIGINS nao pode usar '*' em producao.")
        return self

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace(
                "postgresql://", "postgresql+psycopg://", 1
            )
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
