from sqlalchemy.orm import Session
from app.models.movie import Movie


class TestMovieModel:
    """Testes para a model Movie."""

    def test_create_movie(self, db_session: Session) -> None:
        """Testa a criação de um filme no banco de dados."""
        movie = Movie(title="The Matrix", year=1999)
        db_session.add(movie)
        db_session.commit()

        fetched_movie = db_session.query(Movie).filter_by(title="The Matrix").first()
        assert fetched_movie is not None
        assert fetched_movie.title == "The Matrix"
        assert fetched_movie.year == 1999

    def test_create_multiple_movies(self, db_session: Session) -> None:
        """Testa a criação de múltiplos filmes no banco de dados."""
        movies = [
            Movie(title="The Matrix", year=1999),
            Movie(title="Gladiator", year=2010),
            Movie(title="Interstellar", year=2014),
        ]

        db_session.add_all(movies)
        db_session.commit()

        fetched_movies = db_session.query(Movie).all()
        assert len(fetched_movies) == 3
        assert {m.title for m in fetched_movies} == {
            "The Matrix",
            "Gladiator",
            "Interstellar",
        }

    def test_get_movie_by_id(self, db_session: Session) -> None:
        """Testa a busca de um filme pelo ID."""
        movie = Movie(title="Gladiator", year=2000)
        db_session.add(movie)
        db_session.commit()

        fetched_movie = db_session.get(Movie, movie.id)
        assert fetched_movie is not None
        assert fetched_movie.id == movie.id
        assert fetched_movie.title == "Gladiator"

    def test_get_movie_by_title(self, db_session: Session) -> None:
        """Testa a busca de um filme pelo título."""
        movie = Movie(title="Fight Club", year=1999)
        db_session.add(movie)
        db_session.commit()

        fetched_movie = db_session.query(Movie).filter_by(title="Fight Club").first()
        assert fetched_movie is not None
        assert fetched_movie.title == "Fight Club"

    def test_update_movie(self, db_session: Session) -> None:
        """Testa a atualização de um filme."""
        movie = Movie(title="The Dark Knight", year=2008)
        db_session.add(movie)
        db_session.commit()

        movie.year = 2009
        db_session.commit()

        fetched_movie = (
            db_session.query(Movie).filter_by(title="The Dark Knight").first()
        )
        assert fetched_movie is not None
        assert fetched_movie.year == 2009

    def test_delete_movie(self, db_session: Session) -> None:
        """Testa a remoção de um filme."""
        movie = Movie(title="Titanic", year=1997)
        db_session.add(movie)
        db_session.commit()

        db_session.delete(movie)
        db_session.commit()

        fetched_movie = db_session.query(Movie).filter_by(title="Titanic").first()
        assert fetched_movie is None
