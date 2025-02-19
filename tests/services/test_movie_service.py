from sqlalchemy.orm import Session
from app.services.movie_service import MovieService
from app.schemas.movie import MovieCreate, MovieResponse
from typing import cast


class TestMovieService:
    """Testes unitários para a service de filmes."""

    def test_create_movie(self, db_session: Session) -> None:
        """Testa a criação de um filme via service."""
        movie_data = MovieCreate(title="Titanic", year=1997)
        movie = MovieService.create_movie(db_session, movie_data)

        assert movie is not None
        assert movie.title == "Titanic"
        assert movie.year == 1997
        assert isinstance(movie, MovieResponse)

    def test_get_movie_by_id(self, db_session: Session) -> None:
        """Testa a busca de um filme pelo ID."""
        movie_data = MovieCreate(title="Interstellar", year=2014)
        created_movie = MovieService.create_movie(db_session, movie_data)
        fetched_movie = MovieService.get_movie_by_id(
            db_session, cast(int, created_movie.id)
        )

        assert fetched_movie is not None
        assert fetched_movie.id == created_movie.id
        assert fetched_movie.title == "Interstellar"

    def test_get_movie_by_id_not_found(self, db_session: Session) -> None:
        """Testa a busca de um filme por ID inexistente."""
        movie = MovieService.get_movie_by_id(db_session, 9999)  # ID que não existe
        assert movie is None

    def test_get_movie_by_title(self, db_session: Session) -> None:
        """Testa a busca de um filme pelo título."""
        movie_data = MovieCreate(title="The Dark Knight", year=2008)
        MovieService.create_movie(db_session, movie_data)

        fetched_movie = MovieService.get_movie_by_title(db_session, "The Dark Knight")
        assert fetched_movie is not None
        assert fetched_movie.title == "The Dark Knight"

    def test_get_movie_by_title_not_found(self, db_session: Session) -> None:
        """Testa a busca de um filme por título inexistente."""
        movie = MovieService.get_movie_by_title(db_session, "Unknown Movie")
        assert movie is None

    def test_get_all_movies(self, db_session: Session) -> None:
        """Testa a obtenção de todos os filmes."""
        MovieService.create_movie(db_session, MovieCreate(title="Gladiator", year=2000))
        MovieService.create_movie(db_session, MovieCreate(title="Avatar", year=2009))

        all_movies = MovieService.get_all_movies(db_session)

        assert len(all_movies.movies) == 2
        assert all(isinstance(m, MovieResponse) for m in all_movies.movies)

    def test_delete_movie(self, db_session: Session) -> None:
        """Testa a remoção de um filme."""
        movie_data = MovieCreate(title="Titanic", year=1997)
        created_movie = MovieService.create_movie(db_session, movie_data)

        assert (
            MovieService.delete_movie(db_session, cast(int, created_movie.id)) is True
        )

        # Tentar buscar o filme removido
        deleted_movie = MovieService.get_movie_by_id(
            db_session, cast(int, created_movie.id)
        )
        assert deleted_movie is None

    def test_delete_movie_not_found(self, db_session: Session) -> None:
        """Testa a remoção de um filme inexistente."""
        assert MovieService.delete_movie(db_session, 9999) is False
