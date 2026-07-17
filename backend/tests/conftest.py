import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.services import licitacao_service


@pytest.fixture(autouse=True)
def _limpar_cache_contagem():
    """Isola o cache TTL do COUNT entre testes (é um dict global do módulo)."""
    licitacao_service._count_cache.clear()
    yield
    licitacao_service._count_cache.clear()


@pytest.fixture
def db_app():
    """App FastAPI com um banco SQLite em memória isolado por teste."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine)

    def override_db():
        with test_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    try:
        yield engine
    finally:
        app.dependency_overrides.clear()
