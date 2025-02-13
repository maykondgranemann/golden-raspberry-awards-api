import pytest
import datetime
import pytz

TESTS_CACHE_FILE = "tests/.last_test_run"


@pytest.fixture(scope="session", autouse=True)
def save_test_execution_time() -> None:
    """Salva a data da última execução dos testes no horário de Brasília (UTC-3)."""
    brasilia_tz = pytz.timezone("America/Sao_Paulo")
    now_brasilia = datetime.datetime.now(datetime.UTC).astimezone(brasilia_tz)

    with open(TESTS_CACHE_FILE, "w") as f:
        f.write(now_brasilia.isoformat())
