from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

# Tabela de associação entre filmes e estúdios (Many-to-Many)
movie_studio = Table(
    "movie_studio",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("studio_id", Integer, ForeignKey("studios.id"), primary_key=True),
)
