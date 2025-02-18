from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from loguru import logger
from app.config import Config
from typing import Iterator
from sqlalchemy.orm import Session


# Criar engine do banco
engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})

# Criar sessão do banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Session]:
    """Retorna uma sessão de banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_database_connection() -> bool:
    """Verifica se a conexão com o banco de dados está ativa."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Conexão com o banco de dados estabelecida com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return False
