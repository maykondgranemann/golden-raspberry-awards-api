from sqlalchemy import Column, Integer, String
from app.models.base import Base
from app.models.movie_studio import movie_studio
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import relationship, Mapped

if TYPE_CHECKING:
    from app.models.movie import Movie


class Studio(Base):
    """Modelo da Tabela Studios"""

    __tablename__ = "studios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    movies: Mapped[List["Movie"]] = relationship(
        "Movie", secondary=movie_studio, back_populates="studios"
    )
