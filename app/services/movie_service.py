from sqlalchemy.orm import Session
from app.repositories.movie_repository import MovieRepository
from app.schemas.movie import MovieCreate, MovieResponse, MovieListResponse
from typing import Optional, List, cast


class MovieService:
    """Camada de serviço para Movies, aplicando regras de negócio."""

    @staticmethod
    def create_movie(db: Session, movie_data: MovieCreate) -> MovieResponse:
        """Cria um novo filme e retorna os dados formatados."""
        movie = MovieRepository.create(db, movie_data.title, movie_data.year)

        if movie is None:
            raise ValueError("Erro ao criar o filme. O repositório retornou None.")

        return MovieResponse(
            id=cast(int, movie.id),
            title=cast(str, movie.title),
            year=cast(int, movie.year),
        )

    @staticmethod
    def get_movie_by_id(db: Session, movie_id: int) -> Optional[MovieResponse]:
        """Obtém um filme pelo ID, retornando no formato correto."""
        movie = MovieRepository.get_by_id(db, movie_id)
        if movie is None:
            return None
        return MovieResponse(
            id=cast(int, movie.id),
            title=cast(str, movie.title),
            year=cast(int, movie.year),
        )

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
        )

    @staticmethod
    def get_all_movies(db: Session) -> MovieListResponse:
        """Obtém todos os filmes cadastrados no banco."""
        movies = MovieRepository.get_all(db)
        return MovieListResponse(
            movies=[
                MovieResponse(
                    id=cast(int, m.id), title=cast(str, m.title), year=cast(int, m.year)
                )
                for m in movies
            ]
        )

    @staticmethod
    def delete_movie(db: Session, movie_id: int) -> bool:
        """Deleta um filme pelo ID."""
        return MovieRepository.delete(db, movie_id)
