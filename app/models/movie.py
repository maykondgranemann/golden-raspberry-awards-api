from __future__ import annotations
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship, Mapped
from app.models.base import Base
from app.models.movie_producer import movie_producer
from app.models.movie_studio import movie_studio
from typing import List, TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.producer import Producer
    from app.models.studio import Studio


class Movie(Base):
    """Modelo da Tabela Movies"""

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    year = Column(Integer, nullable=False)
    winner = Column(Boolean, nullable=False, default=False)

    producers: Mapped[List["Producer"]] = relationship(
        "Producer", secondary=movie_producer, back_populates="movies"
    )
    studios: Mapped[List["Studio"]] = relationship(
        "Studio", secondary=movie_studio, back_populates="movies"
    )
