from sqlalchemy.orm import Session
from app.repositories.movie_repository import MovieRepository
from app.services.movie_service import MovieService
from app.schemas.movie import (
    MovieCreate,
    MovieDetailedResponse,
    MovieResponse,
    MovieListResponse,
)
from app.schemas.producer import ProducerCreate, ProducerResponse
from app.schemas.studio import StudioCreate, StudioResponse
from app.repositories.producer_repository import ProducerRepository
from app.repositories.studio_repository import StudioRepository
from typing import List, cast

from app.services.producer_service import ProducerService
from app.services.studio_service import StudioService


class TestMovieService:
    """Testes unitários para a service de filmes."""

    def test_create_movie(self, db_session: Session) -> None:
        """Testa a criação de um filme via service."""
        movie_data = MovieCreate(title="Titanic", year=1997, winner=True)
        movie = MovieService.create_movie(db_session, movie_data)

        assert movie is not None
        assert movie.title == "Titanic"
        assert movie.year == 1997
        assert movie.winner is True
        assert isinstance(movie, MovieResponse)

    def test_get_movie_by_id(self, db_session: Session) -> None:
        """Testa a busca de um filme pelo ID."""
        movie_data = MovieCreate(title="Interstellar", year=2014, winner=False)
        created_movie = MovieService.create_movie(db_session, movie_data)
        fetched_movie = MovieService.get_movie_by_id(
            db_session, cast(int, created_movie.id)
        )

        assert fetched_movie is not None
        assert fetched_movie.id == created_movie.id
        assert fetched_movie.title == "Interstellar"
        assert fetched_movie.winner is False

    def test_get_movie_by_id_not_found(self, db_session: Session) -> None:
        """Testa a busca de um filme por ID inexistente."""
        movie = MovieService.get_movie_by_id(db_session, 9999)
        assert movie is None

    def test_get_movie_by_title(self, db_session: Session) -> None:
        """Testa a busca de um filme pelo título."""
        movie_data = MovieCreate(title="The Dark Knight", year=2008, winner=False)
        MovieService.create_movie(db_session, movie_data)

        fetched_movie = MovieService.get_movie_by_title(db_session, "The Dark Knight")
        assert fetched_movie is not None
        assert fetched_movie.title == "The Dark Knight"
        assert fetched_movie.winner is False

    def test_get_movie_by_title_not_found(self, db_session: Session) -> None:
        """Testa a busca de um filme por título inexistente."""
        movie = MovieService.get_movie_by_title(db_session, "Unknown Movie")
        assert movie is None

    def test_get_all_movies_without_expand(self, db_session: Session) -> None:
        """Testa a obtenção de todos os filmes sem expandir relacionamentos."""
        MovieService.create_movie(
            db_session, MovieCreate(title="Gladiator", year=2000, winner=True)
        )
        MovieService.create_movie(
            db_session, MovieCreate(title="Avatar", year=2009, winner=False)
        )

        all_movies = MovieService.get_all_movies(db_session, [])

        assert len(all_movies.movies) == 2
        assert all(isinstance(m, MovieResponse) for m in all_movies.movies)
        assert all_movies.movies[0].winner is True
        assert all_movies.movies[1].winner is False
        assert all(m.producers is None for m in all_movies.movies)
        assert all(m.studios is None for m in all_movies.movies)

    def test_delete_movie(self, db_session: Session) -> None:
        """Testa a remoção de um filme."""
        movie_data = MovieCreate(title="Titanic", year=1997, winner=True)
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

    def test_get_all_movies_with_expand_producers(self, db_session: Session) -> None:
        """Testa a obtenção de filmes expandindo apenas os produtores."""
        # Criar um filme
        movie_data = MovieCreate(title="Inception", year=2010, winner=True)
        created_movie = MovieService.create_movie(db_session, movie_data)

        # Criar um produtor e associá-lo ao filme
        producer_data = ProducerCreate(name="Christopher Nolan")
        ProducerService.create_producer(db_session, producer_data)

        movie = MovieRepository.get_by_id(db_session, cast(int, created_movie.id))
        assert movie is not None

        producer_obj = ProducerRepository.get_by_name(db_session, "Christopher Nolan")
        assert producer_obj is not None

        movie.producers.append(producer_obj)
        db_session.commit()

        # Chamar a service com expand=producers
        all_movies: MovieListResponse = MovieService.get_all_movies(
            db_session, ["producers"]
        )

        assert len(all_movies.movies) > 0
        assert isinstance(all_movies.movies[0], MovieDetailedResponse)
        assert all_movies.movies[0].producers is not None
        assert len(all_movies.movies[0].producers) == 1
        assert all_movies.movies[0].producers[0].name == "Christopher Nolan"

    def test_get_all_movies_with_expand_studios(self, db_session: Session) -> None:
        """Testa a obtenção de filmes expandindo apenas os estúdios."""
        # Criar um filme
        movie_data = MovieCreate(title="The Matrix", year=1999, winner=False)
        created_movie = MovieService.create_movie(db_session, movie_data)

        # Criar um estúdio e associá-lo ao filme
        studio_data = StudioCreate(name="Warner Bros")
        StudioService.create_studio(db_session, studio_data)

        movie = MovieRepository.get_by_id(db_session, cast(int, created_movie.id))
        assert movie is not None

        studio_obj = StudioRepository.get_by_name(db_session, "Warner Bros")
        assert studio_obj is not None

        movie.studios.append(studio_obj)
        db_session.commit()

        # Chamar a service com expand=studios
        all_movies: MovieListResponse = MovieService.get_all_movies(
            db_session, ["studios"]
        )

        assert len(all_movies.movies) > 0
        assert isinstance(all_movies.movies[0], MovieDetailedResponse)
        assert all_movies.movies[0].studios is not None
        assert len(all_movies.movies[0].studios) == 1
        assert all_movies.movies[0].studios[0].name == "Warner Bros"

    def test_get_all_movies_with_expand_producers_and_studios(
        self, db_session: Session
    ) -> None:
        """
        Testa a obtenção de filmes expandindo produtores e estúdios simultaneamente."""
        # Criar um filme
        movie_data = MovieCreate(title="Interstellar", year=2014, winner=True)
        created_movie = MovieService.create_movie(db_session, movie_data)

        # Criar produtor e estúdio e associá-los ao filme
        producer_data = ProducerCreate(name="Christopher Nolan")
        ProducerService.create_producer(db_session, producer_data)

        studio_data = StudioCreate(name="Paramount Pictures")
        StudioService.create_studio(db_session, studio_data)

        movie = MovieRepository.get_by_id(db_session, cast(int, created_movie.id))
        assert movie is not None

        producer_obj = ProducerRepository.get_by_name(db_session, "Christopher Nolan")
        studio_obj = StudioRepository.get_by_name(db_session, "Paramount Pictures")

        assert producer_obj is not None
        assert studio_obj is not None

        movie.producers.append(producer_obj)
        movie.studios.append(studio_obj)
        db_session.commit()

        # Chamar a service com expand=producers,studios
        all_movies: MovieListResponse = MovieService.get_all_movies(
            db_session, ["producers", "studios"]
        )

        assert len(all_movies.movies) > 0
        assert isinstance(all_movies.movies[0], MovieDetailedResponse)

        # Verifica produtores
        assert all_movies.movies[0].producers is not None
        assert len(all_movies.movies[0].producers) == 1
        assert all_movies.movies[0].producers[0].name == "Christopher Nolan"

        # Verifica estúdios
        assert all_movies.movies[0].studios is not None
        assert len(all_movies.movies[0].studios) == 1
        assert all_movies.movies[0].studios[0].name == "Paramount Pictures"
