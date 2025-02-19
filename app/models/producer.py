from __future__ import annotations
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped
from app.models.base import Base
from app.models.movie_producer import movie_producer
from typing import List, TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.movie import Movie


class Producer(Base):
    """Modelo da Tabela Producers"""

    __tablename__ = "producers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    movies: Mapped[List["Movie"]] = relationship(
        "Movie", secondary=movie_producer, back_populates="producers"
    )
