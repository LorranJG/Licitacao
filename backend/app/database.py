from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()

# statement_timeout protege contra queries travadas que seguram uma conexão
# do pool indefinidamente. Aplicado só quando configurado (>0), tipicamente
# apenas no backend/API — os workers de coleta não o definem, para não
# interromper lotes longos de backfill.
_connect_args: dict = {}
if settings.db_statement_timeout_ms > 0:
    _connect_args["options"] = f"-c statement_timeout={settings.db_statement_timeout_ms}"

engine = create_engine(
    settings.sqlalchemy_database_url,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    connect_args=_connect_args,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
