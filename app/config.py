import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

class Config:
    ENV = os.getenv("ENV", "development")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gra.db")
    CSV_PATH = os.getenv("CSV_PATH", "data/movielist.csv")
