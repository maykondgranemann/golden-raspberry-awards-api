from sqlalchemy import Column, Integer, String
from app.models.base import Base


class Movie(Base):
    """Modelo da Tabela Movies"""

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    year = Column(Integer, nullable=False)
