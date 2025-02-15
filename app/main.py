from fastapi import FastAPI
from app.config import Config
from app.db.database import test_database_connection
import os
import datetime
import pytz

app = FastAPI(
    title="Golden Raspberry Awards API",
    description=(
        "API para processar e analisar vencedores do prêmio " "Golden Raspberry Awards."
    ),
    version="0.0.1",
)

TESTS_CACHE_FILE = "tests/.last_test_run"


def get_last_test_execution() -> str:
    """Retorna a última data de execução dos testes no horário de Brasília (UTC-3)"""
    brasilia_tz = pytz.timezone("America/Sao_Paulo")
    if os.path.exists(TESTS_CACHE_FILE):
        with open(TESTS_CACHE_FILE, "r") as f:
            return (
                datetime.datetime.fromisoformat(f.read())
                .astimezone(brasilia_tz)
                .isoformat()
            )
    return "No tests executed yet"


@app.get("/health")
def health_check() -> dict[str, str | bool]:
    """Retorna informações sobre o estado da API"""
    return {
        "api_status": "running",
        "csv_loaded": os.path.exists(Config.CSV_PATH),
        "database_status": (
            "connected" if test_database_connection() else "disconnected"
        ),
        "environment": Config.ENV,
        "last_tests_run": get_last_test_execution(),
    }


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Golden Raspberry Awards API is running!"}
