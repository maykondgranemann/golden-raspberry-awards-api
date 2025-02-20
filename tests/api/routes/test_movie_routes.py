from typing import cast
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.movie_repository import MovieRepository
from app.repositories.producer_repository import ProducerRepository
from app.repositories.studio_repository import StudioRepository
from app.schemas.movie import MovieCreate
from app.schemas.producer import ProducerCreate
from app.schemas.studio import StudioCreate
from app.services.movie_service import MovieService
from app.services.producer_service import ProducerService
from app.services.studio_service import StudioService


class TestMovieRoutes:
    """Testes para as rotas de Movie."""

    def test_create_movie(self, client: TestClient) -> None:
        """Testa a criação de um novo filme via API."""
        payload = {"title": "Inception", "year": 2010, "winner": True}
        response = client.post("/movies/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Inception"
        assert data["year"] == 2010
        assert data["winner"] is True
        assert "id" in data

    def test_get_movie_by_id(self, client: TestClient) -> None:
        """Testa a busca de um filme pelo ID."""
        payload = {"title": "The Matrix", "year": 1999, "winner": False}
        create_response = client.post("/movies/", json=payload)
        assert create_response.status_code == 201

        movie_id = create_response.json()["id"]
        response = client.get(f"/movies/{movie_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == movie_id
        assert data["title"] == "The Matrix"
        assert data["winner"] is False

    def test_get_movie_by_id_not_found(self, client: TestClient) -> None:
        """Testa erro ao buscar um filme por ID inexistente via API."""
        response = client.get("/movies/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"

    def test_get_movie_by_title(self, client: TestClient) -> None:
        """Testa a busca de um filme pelo título."""
        payload = {"title": "Interstellar", "year": 2014, "winner": True}
        client.post("/movies/", json=payload)

        response = client.get("/movies/title/Interstellar")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Interstellar"
        assert data["year"] == 2014
        assert data["winner"] is True

    def test_get_movie_by_title_not_found(self, client: TestClient) -> None:
        """Testa erro ao buscar um filme por título inexistente via API."""
        response = client.get("/movies/title/Unknown Movie")
        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"

    def test_get_all_movies(self, client: TestClient) -> None:
        """Testa a obtenção de todos os filmes cadastrados."""
        client.post(
            "/movies/", json={"title": "Titanic", "year": 1997, "winner": False}
        )
        client.post(
            "/movies/", json={"title": "Gladiator", "year": 2000, "winner": True}
        )

        response = client.get("/movies/")
        assert response.status_code == 200
        data = response.json()["movies"]

        assert isinstance(data, list)
        assert len(data) >= 2
        assert "title" in data[0]
        assert "winner" in data[0]

    def test_delete_movie(self, client: TestClient) -> None:
        """Testa a exclusão de um filme."""
        payload = {"title": "Avatar", "year": 2009, "winner": True}
        create_response = client.post("/movies/", json=payload)
        assert create_response.status_code == 201

        movie_id = create_response.json()["id"]
        delete_response = client.delete(f"/movies/{movie_id}")

        assert delete_response.status_code == 204

        # Verifica se o filme foi removido
        response = client.get(f"/movies/{movie_id}")
        assert response.status_code == 404

    def test_delete_movie_not_found(self, client: TestClient) -> None:
        """Testa a remoção de um filme inexistente."""
        assert client.delete("/movies/9999").status_code == 404

    def test_get_all_movies_with_expand_producers(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Testa a obtenção de filmes expandindo apenas os produtores via API."""
        movie_data = MovieCreate(title="Inception", year=2010, winner=True)
        created_movie = MovieService.create_movie(cast(Session, db_session), movie_data)

        producer_data = ProducerCreate(name="Christopher Nolan")
        ProducerService.create_producer(cast(Session, db_session), producer_data)

        movie = MovieRepository.get_by_id(
            cast(Session, db_session), cast(int, created_movie.id)
        )
        assert movie is not None

        producer_obj = ProducerRepository.get_by_name(
            cast(Session, db_session), "Christopher Nolan"
        )
        assert producer_obj is not None

        movie.producers.append(producer_obj)
        cast(Session, db_session).commit()

        response = client.get("/movies/?expand=producers")
        assert response.status_code == 200

        data = response.json()["movies"]
        assert len(data) > 0
        assert "producers" in data[0]
        assert len(data[0]["producers"]) == 1
        assert data[0]["producers"][0]["name"] == "Christopher Nolan"

    def test_get_all_movies_with_expand_studios(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Testa a obtenção de filmes expandindo apenas os estúdios via API."""
        movie_data = MovieCreate(title="The Matrix", year=1999, winner=False)
        created_movie = MovieService.create_movie(cast(Session, db_session), movie_data)

        studio_data = StudioCreate(name="Warner Bros")
        StudioService.create_studio(cast(Session, db_session), studio_data)

        movie = MovieRepository.get_by_id(
            cast(Session, db_session), cast(int, created_movie.id)
        )
        assert movie is not None

        studio_obj = StudioRepository.get_by_name(
            cast(Session, db_session), "Warner Bros"
        )
        assert studio_obj is not None

        movie.studios.append(studio_obj)
        cast(Session, db_session).commit()

        response = client.get("/movies/?expand=studios")
        assert response.status_code == 200

        data = response.json()["movies"]
        assert len(data) > 0
        assert "studios" in data[0]
        assert len(data[0]["studios"]) == 1
        assert data[0]["studios"][0]["name"] == "Warner Bros"

    def test_get_all_movies_with_expand_producers_and_studios(
        self, client: TestClient, db_session: Session
    ) -> None:
        """
        Testa a obtenção de filmes expandindo produtores e estúdios
        simultaneamente via API.
        """
        movie_data = MovieCreate(title="Interstellar", year=2014, winner=True)
        created_movie = MovieService.create_movie(cast(Session, db_session), movie_data)

        producer_data = ProducerCreate(name="Christopher Nolan")
        ProducerService.create_producer(cast(Session, db_session), producer_data)

        studio_data = StudioCreate(name="Paramount Pictures")
        StudioService.create_studio(cast(Session, db_session), studio_data)

        movie = MovieRepository.get_by_id(
            cast(Session, db_session), cast(int, created_movie.id)
        )
        assert movie is not None

        producer_obj = ProducerRepository.get_by_name(
            cast(Session, db_session), "Christopher Nolan"
        )
        studio_obj = StudioRepository.get_by_name(
            cast(Session, db_session), "Paramount Pictures"
        )

        assert producer_obj is not None
        assert studio_obj is not None

        movie.producers.append(producer_obj)
        movie.studios.append(studio_obj)
        cast(Session, db_session).commit()

        response = client.get("/movies/?expand=producers,studios")
        assert response.status_code == 200

        data = response.json()["movies"]
        assert len(data) > 0

        assert "producers" in data[0]
        assert len(data[0]["producers"]) == 1
        assert data[0]["producers"][0]["name"] == "Christopher Nolan"

        assert "studios" in data[0]
        assert len(data[0]["studios"]) == 1
        assert data[0]["studios"][0]["name"] == "Paramount Pictures"
