from fastapi.testclient import TestClient


class TestProducerRoutes:
    """Testes para as rotas de Producer."""

    def test_create_producer(self, client: TestClient) -> None:
        """Testa a criação de um produtor via API."""
        payload = {"name": "Steven Spielberg"}
        response = client.post("/producers/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Steven Spielberg"
        assert isinstance(data["id"], int)

    def test_get_producer_by_id(self, client: TestClient) -> None:
        """Testa a obtenção de um produtor pelo ID."""
        payload = {"name": "Christopher Nolan"}
        create_response = client.post("/producers/", json=payload)
        producer_id = create_response.json()["id"]

        response = client.get(f"/producers/{producer_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == producer_id
        assert data["name"] == "Christopher Nolan"

    def test_get_producer_by_name(self, client: TestClient) -> None:
        """Testa a obtenção de um produtor pelo nome."""
        payload = {"name": "Quentin Tarantino"}
        client.post("/producers/", json=payload)

        response = client.get("/producers/name/Quentin Tarantino")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Quentin Tarantino"

    def test_get_all_producers(self, client: TestClient) -> None:
        """Testa a obtenção de todos os produtores."""
        client.post("/producers/", json={"name": "Tarantino"})
        client.post("/producers/", json={"name": "Scorsese"})

        response = client.get("/producers/")
        assert response.status_code == 200

        data = response.json()["producers"]
        assert isinstance(data, list)
        assert len(data) >= 2  # Garante que pelo menos 2 produtores foram adicionados

    def test_delete_producer(self, client: TestClient) -> None:
        """Testa a exclusão de um produtor."""
        payload = {"name": "George Lucas"}
        create_response = client.post("/producers/", json=payload)
        producer_id = create_response.json()["id"]

        delete_response = client.delete(f"/producers/{producer_id}")
        assert delete_response.status_code == 204  # Deve retornar No Content

        # Verifica se o produtor foi removido
        response = client.get(f"/producers/{producer_id}")
        assert response.status_code == 404  # Deve retornar Not Found

    def test_delete_producer_not_found(self, client: TestClient) -> None:
        """Testa a remoção de um produtor inexistente."""
        response = client.delete("/producers/9999")  # ID que não existe

        assert response.status_code == 404
        assert response.json()["detail"] == "Producer not found"
