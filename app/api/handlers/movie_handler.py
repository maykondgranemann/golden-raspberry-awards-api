from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.movie_service import MovieService
from app.schemas.movie import MovieCreate, MovieResponse, MovieListResponse
from typing import Optional


class MovieHandler:
    """Camada de manipulação de requisições para Movies."""

    ALLOWED_EXPANDS = {"producers", "studios"}

    @staticmethod
    def create_movie(db: Session, movie_data: MovieCreate) -> MovieResponse:
        """Cria um novo filme e retorna os dados formatados."""
        return MovieService.create_movie(db, movie_data)

    @staticmethod
    def get_movie_by_id(db: Session, movie_id: int) -> MovieResponse:
        """Obtém um filme pelo ID."""
        movie = MovieService.get_movie_by_id(db, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie

    @staticmethod
    def get_movie_by_title(db: Session, title: str) -> MovieResponse:
        """Obtém um filme pelo título."""
        movie = MovieService.get_movie_by_title(db, title)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie

    @staticmethod
    def get_all_movies(db: Session, expand: str) -> MovieListResponse:
        """
        Obtém todos os filmes, permitindo expandir os relacionamentos.

        :param db: Sessão do banco de dados.
        :param expand: String com os campos a serem expandidos, separados por vírgula.
        :return: Lista de filmes.
        """
        expand_list = expand.split(",") if expand else []
        invalid_expands = set(expand_list) - MovieHandler.ALLOWED_EXPANDS

        if invalid_expands:
            raise HTTPException(
                status_code=400,
                detail=f"Campos inválidos em expand: {', '.join(invalid_expands)}",
            )

        return MovieService.get_all_movies(db, expand_list)

    @staticmethod
    def delete_movie(db: Session, movie_id: int) -> None:
        """Deleta um filme pelo ID."""
        if not MovieService.delete_movie(db, movie_id):
            raise HTTPException(status_code=404, detail="Movie not found")
