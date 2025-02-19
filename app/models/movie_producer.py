from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

# Tabela de associação entre filmes e produtores (Many-to-Many)
movie_producer = Table(
    "movie_producer",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("producer_id", Integer, ForeignKey("producers.id"), primary_key=True),
)
