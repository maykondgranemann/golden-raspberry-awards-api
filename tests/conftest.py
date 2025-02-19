from fastapi.testclient import TestClient
import pytest
import datetime
import pytz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import get_db
from app.models import Base
from typing import Iterator
from sqlalchemy.orm import Session
from app.main import app


TESTS_CACHE_FILE = "tests/.last_test_run"


@pytest.fixture(scope="session", autouse=True)
def save_test_execution_time() -> None:
    """Salva a data da última execução dos testes no horário de Brasília (UTC-3)."""
    brasilia_tz = pytz.timezone("America/Sao_Paulo")
    now_brasilia = datetime.datetime.now(datetime.UTC).astimezone(brasilia_tz)

    with open(TESTS_CACHE_FILE, "w") as f:
        f.write(now_brasilia.isoformat())


# Criar uma engine temporária para os testes (SQLite em memória)
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Criar sessão independente para os testes
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Iterator[Session]:
    """Cria um banco em memória e uma sessão isolada para cada teste"""
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    yield db  # Retorna a sessão para o teste usar

    db.rollback()  # Desfaz alterações após o teste
    db.close()  # Fecha a sessão
    Base.metadata.drop_all(bind=engine)  # Remove todas as tabelas ao final do teste


@pytest.fixture
def sample_producers() -> list[str]:
    """
    Retorna uma lista de nomes de produtores para testes.
    """
    return ["John Doe", "Jane Smith", "Alice Johnson"]


@pytest.fixture(scope="function")
def client() -> Iterator[TestClient]:
    """Retorna um cliente de teste da API utilizando o mesmo banco em memória."""

    with TestClient(app) as test_client:
        yield test_client  # Retorna o cliente de teste
