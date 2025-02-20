from sqlalchemy.orm import Session
from app.models.movie import Movie
from app.repositories.movie_repository import MovieRepository
from typing import List, cast


class TestMovieRepository:
    """
    Testes unitários para a repository de filmes.
    """

    def test_create_movie(self, db_session: Session) -> None:
        """
        Testa a criação de um novo filme.
        """
        movie = MovieRepository.create(db_session, "Inception", 2010, True)

        assert movie is not None
        assert movie.title == "Inception"
        assert movie.year == 2010
        assert movie.winner is True
        assert isinstance(movie, Movie)

    def test_create_existing_movie(self, db_session: Session) -> None:
        """
        Testa a criação de um filme que já existe no banco de dados.
        """
        first_movie = MovieRepository.create(db_session, "The Matrix", 1999, False)
        assert first_movie is not None

        # Deve retornar o mesmo filme
        second_movie = MovieRepository.create(db_session, "The Matrix", 1999, False)
        assert second_movie is not None

        assert first_movie.id == second_movie.id
        assert first_movie.title == "The Matrix"
        assert first_movie.winner is False

    def test_get_by_id(self, db_session: Session) -> None:
        """
        Testa a busca de um filme pelo ID.
        """
        movie = MovieRepository.create(db_session, "Interstellar", 2014, True)
        assert movie is not None

        fetched_movie = MovieRepository.get_by_id(db_session, cast(int, movie.id))
        assert fetched_movie is not None

        assert fetched_movie.id == movie.id
        assert fetched_movie.title == "Interstellar"
        assert fetched_movie.winner is True

    def test_get_by_id_not_found(self, db_session: Session) -> None:
        """
        Testa a busca de um filme por ID inexistente.
        """
        movie = MovieRepository.get_by_id(db_session, 9999)
        assert movie is None

    def test_get_by_title(self, db_session: Session) -> None:
        """
        Testa a busca de um filme pelo título.
        """
        MovieRepository.create(db_session, "The Dark Knight", 2008, False)
        fetched_movie = MovieRepository.get_by_title(db_session, "The Dark Knight")

        assert fetched_movie is not None
        assert fetched_movie.title == "The Dark Knight"
        assert fetched_movie.winner is False

    def test_get_by_title_not_found(self, db_session: Session) -> None:
        """
        Testa a busca de um filme por título inexistente.
        """
        movie = MovieRepository.get_by_title(db_session, "Unknown Movie")
        assert movie is None

    def test_get_all(self, db_session: Session) -> None:
        """
        Testa a obtenção de todos os filmes cadastrados.
        """
        MovieRepository.create(db_session, "Gladiator", 2000, True)
        MovieRepository.create(db_session, "Avatar", 2009, False)

        all_movies: List[Movie] = MovieRepository.get_all(db_session)

        assert len(all_movies) == 2
        assert all(isinstance(m, Movie) for m in all_movies)

    def test_delete_movie(self, db_session: Session) -> None:
        """
        Testa a remoção de um filme pelo ID.
        """
        movie = MovieRepository.create(db_session, "Titanic", 1997, True)
        assert movie is not None

        assert MovieRepository.delete(db_session, cast(int, movie.id)) is True

        # Tentar buscar o filme removido
        deleted_movie = MovieRepository.get_by_id(db_session, cast(int, movie.id))
        assert deleted_movie is None

    def test_delete_movie_not_found(self, db_session: Session) -> None:
        """
        Testa a remoção de um filme inexistente.
        """
        assert MovieRepository.delete(db_session, 9999) is False
