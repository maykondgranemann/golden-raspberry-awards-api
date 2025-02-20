from sqlalchemy.orm import Session
from app.repositories.movie_repository import MovieRepository
from app.schemas.movie import (
    MovieCreate,
    MovieDetailedResponse,
    MovieResponse,
    MovieListResponse,
)
from typing import List, Optional, cast

from app.schemas.producer import ProducerResponse
from app.schemas.studio import StudioResponse


class MovieService:
    """Camada de serviço para Movies, aplicando regras de negócio."""

    @staticmethod
    def create_movie(db: Session, movie_data: MovieCreate) -> MovieResponse:
        """Cria um novo filme e retorna os dados formatados."""
        movie = MovieRepository.create(
            db, movie_data.title, movie_data.year, movie_data.winner
        )

        if movie is None:
            raise ValueError("Erro ao criar o filme. O repositório retornou None.")

        return MovieResponse(
            id=cast(int, movie.id),
            title=cast(str, movie.title),
            year=cast(int, movie.year),
            winner=cast(bool, movie.winner),
        )

    @staticmethod
    def get_movie_by_id(db: Session, movie_id: int) -> Optional[MovieResponse]:
        """Obtém um filme pelo ID, retornando no formato correto."""
        movie = MovieRepository.get_by_id(db, movie_id)
        if movie:
            return MovieResponse(
                id=cast(int, movie.id),
                title=cast(str, movie.title),
                year=cast(int, movie.year),
                winner=cast(bool, movie.winner),
            )
        return None

    @staticmethod
    def get_movie_by_title(db: Session, title: str) -> Optional[MovieResponse]:
        """Obtém um filme pelo título."""
        movie = MovieRepository.get_by_title(db, title)
        if movie is None:
            return None
        return MovieResponse(
            id=cast(int, movie.id),
            title=cast(str, movie.title),
            year=cast(int, movie.year),
            winner=cast(bool, movie.winner),
        )

    @staticmethod
    def get_all_movies(db: Session, expand: List[str]) -> MovieListResponse:
        """
        Obtém todos os filmes, permitindo expandir os relacionamentos.

        :param db: Sessão do banco de dados.
        :param expand: Lista de expansões desejadas, ex: ["producers", "studios"]
        :return: Lista de filmes com ou sem os relacionamentos.
        """
        movies = MovieRepository.get_all(db, expand)

        return MovieListResponse(
            movies=[
                MovieDetailedResponse(
                    id=cast(int, m.id),
                    title=cast(str, m.title),
                    year=cast(int, m.year),
                    winner=cast(bool, m.winner),
                    producers=(
                        [
                            ProducerResponse(id=cast(int, p.id), name=str(p.name))
                            for p in m.producers
                        ]
                        if "producers" in expand
                        else None
                    ),
                    studios=(
                        [
                            StudioResponse(id=cast(int, s.id), name=str(s.name))
                            for s in m.studios
                        ]
                        if "studios" in expand
                        else None
                    ),
                )
                for m in movies
            ]
        )

    @staticmethod
    def delete_movie(db: Session, movie_id: int) -> bool:
        """Deleta um filme pelo ID."""
        return MovieRepository.delete(db, movie_id)
