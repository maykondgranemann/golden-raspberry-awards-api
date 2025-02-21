from io import StringIO
from unittest.mock import MagicMock
import pandas as pd
import os
from fastapi.testclient import TestClient
import pytest
import datetime
import pytz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import get_db
from app.models import Base
from typing import Iterator, List
from sqlalchemy.orm import Session
from app.main import app


TESTS_CACHE_FILE = "tests/.last_test_run"
# Ativar modo de teste
os.environ["TEST_MODE"] = "true"


@pytest.fixture(scope="session", autouse=True)
def save_test_execution_time() -> None:
    """Salva a data da última execução dos testes no horário de Brasília (UTC-3)."""
    brasilia_tz = pytz.timezone("America/Sao_Paulo")
    now_brasilia = datetime.datetime.now(datetime.UTC).astimezone(brasilia_tz)

    with open(TESTS_CACHE_FILE, "w") as f:
        f.write(now_brasilia.isoformat())


# Criar uma engine temporária para os testes
TEST_DATABASE_URL = "sqlite:///test.db"
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
def client(db_session: Session) -> Iterator[TestClient]:
    """Garante que o client use a mesma sessão de banco para evitar desconexões."""

    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db  # Substitui a conexão do banco

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="class")
def sample_csv() -> str:
    """
    Retorna um exemplo de CSV em formato de string para testes.
    """
    return """year;title;studios;producers;winner
1980;Can't Stop the Music;Associated Film Distribution;Allan Carr;yes
1980;Cruising;Lorimar Productions, United Artists;Jerry Weintraub;
1983;The Lonely Lady;Universal Studios;Robert R. Weston;yes
1983;Two of a Kind;20th Century Fox;Roger M. Rothstein and Joe Wizan;
1984;Rhinestone;20th Century Fox;Marvin Worth and Howard Smith;
"""


@pytest.fixture(scope="class")
def df_sample(sample_csv: str) -> pd.DataFrame:
    """
    Retorna um DataFrame baseado no CSV de exemplo.
    """
    df: pd.DataFrame = pd.read_csv(StringIO(sample_csv), sep=";", dtype=str).fillna("")
    df.columns = df.columns.str.lower().str.strip()
    return df


@pytest.fixture
def csv_content() -> bytes:
    """
    Retorna um conteúdo de CSV válido como bytes.
    """
    return (
        b"year;title;studios;producers;winner\n"
        b"1980;Can't Stop the Music;Associated Film Distribution;Allan Carr;yes\n"
        b"1983;The Lonely Lady;Universal Studios;Robert R. Weston;yes\n"
        b"1984;Rhinestone;20th Century Fox;Marvin Worth and Howard Smith;\n"
    )


@pytest.fixture
def mock_winning_movies() -> List[MagicMock]:
    """Mock dos filmes vencedores, simulando o retorno da MovieRepository."""

    # Criando objetos MagicMock para produtores e definindo explicitamente os nomes
    producer_a = MagicMock()
    producer_a.name = "Producer A"
    producer_b = MagicMock()
    producer_b.name = "Producer B"

    return [
        MagicMock(year=2000, producers=[producer_a]),
        MagicMock(year=2005, producers=[producer_a]),
        MagicMock(year=2010, producers=[producer_a]),
        MagicMock(year=2018, producers=[producer_b]),
        MagicMock(year=2020, producers=[producer_b]),
    ]


@pytest.fixture
def csv_content_for_intervals() -> bytes:
    """
    Retorna um conteúdo de CSV válido com dados fictícios
    para teste da importação e cálculo de intervalos.
    """
    return (
        b"year;title;studios;producers;winner\n"
        b"1990;Movie A;Studio X;Producer A;yes\n"
        b"1995;Movie B;Studio Y;Producer A;yes\n"
        b"2000;Movie C;Studio Z;Producer A;yes\n"
        b"2010;Movie D;Studio W;Producer B;yes\n"
        b"2012;Movie E;Studio W;Producer B;yes\n"
        b"2020;Movie F;Studio Y;Producer C;yes\n"
    )


@pytest.fixture
def csv_content_for_second_upload() -> bytes:
    """
    Retorna um novo conjunto de dados CSV com prêmios diferentes para forçar
    a invalidação do cache e garantir que os novos dados sejam processados.
    """
    return (
        b"year;title;studios;producers;winner\n"
        b"1991;Movie X;Studio A;Producer X;yes\n"
        b"1996;Movie Y;Studio B;Producer X;yes\n"
        b"2001;Movie Z;Studio C;Producer Y;yes\n"
        b"2011;Movie W;Studio D;Producer Y;yes\n"
        b"2013;Movie V;Studio D;Producer Y;yes\n"
        b"2021;Movie U;Studio E;Producer Z;yes\n"
    )
