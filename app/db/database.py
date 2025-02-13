from sqlalchemy import create_engine, text
from app.config import Config

# Criar engine do banco
engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})

def test_database_connection():
    """Verifica se a conexão com o banco de dados está ativa."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")) 
        return True
    except Exception as e:
        return False
