from sqlalchemy import Column, Integer, String
from app.models.base import Base


class Studio(Base):
    """Modelo da Tabela Studios"""

    __tablename__ = "studios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
