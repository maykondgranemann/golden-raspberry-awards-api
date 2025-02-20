from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from app.config import Config
from app.db.database import SessionLocal, create_tables, test_database_connection
import os
import datetime
import pytz
from app.utils.logger import logger

from app.api.routes import (
    csv_importer_routes,
    producer_routes,
    movie_routes,
    studio_routes,
)
from app.services.csv_importer_service import CSVImporterService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Executa operações ao iniciar e finalizar a aplicação."""

    # Verifica se está rodando em modo de teste
    TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

    if not TEST_MODE:
        # Criação das tabelas ao iniciar
        create_tables()

        # Carregar CSV ao iniciar, se existir
        db = SessionLocal()
        CSVImporterService.load_csv_on_startup(db)
        db.close()

    yield  # Aqui é o ponto de entrada da aplicação

    logger.info("Aplicação finalizando...")


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


app = FastAPI(
    title="Golden Raspberry Awards API",
    description=(
        "API para processar e analisar vencedores do prêmio " "Golden Raspberry Awards."
    ),
    version="0.0.1",
    lifespan=lifespan,
)


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


# Incluindo as rotas de produtores
app.include_router(producer_routes.router)

# Registrar rotas de filmes
app.include_router(movie_routes.router)

# Registrar rotas de estúdios
app.include_router(studio_routes.router)

# Registrar rotas de csv_importer
app.include_router(csv_importer_routes.router)
