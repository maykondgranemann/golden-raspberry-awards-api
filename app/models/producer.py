from sqlalchemy import Column, Integer, String
from app.models import Base


class Producer(Base):
    """Modelo da Tabela Producers"""

    __tablename__ = "producers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
