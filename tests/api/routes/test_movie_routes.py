from fastapi.testclient import TestClient


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
