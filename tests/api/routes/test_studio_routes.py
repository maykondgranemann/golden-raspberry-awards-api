from fastapi.testclient import TestClient


class TestStudioRoutes:
    """Testes para as rotas de Studio."""

    def test_create_studio(self, client: TestClient) -> None:
        """Testa a criação de um estúdio via API."""
        payload = {"name": "Warner Bros"}
        response = client.post("/studios/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Warner Bros"
        assert isinstance(data["id"], int)

    def test_get_studio_by_id(self, client: TestClient) -> None:
        """Testa a obtenção de um estúdio pelo ID."""
        payload = {"name": "Universal Pictures"}
        create_response = client.post("/studios/", json=payload)
        studio_id = create_response.json()["id"]

        response = client.get(f"/studios/{studio_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == studio_id
        assert data["name"] == "Universal Pictures"

    def test_get_studio_by_name(self, client: TestClient) -> None:
        """Testa a obtenção de um estúdio pelo nome."""
        payload = {"name": "Paramount Pictures"}
        client.post("/studios/", json=payload)

        response = client.get("/studios/name/Paramount Pictures")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Paramount Pictures"

    def test_get_all_studios(self, client: TestClient) -> None:
        """Testa a obtenção de todos os estúdios."""
        client.post("/studios/", json={"name": "20th Century Studios"})
        client.post("/studios/", json={"name": "MGM"})

        response = client.get("/studios/")
        assert response.status_code == 200

        data = response.json()["studios"]
        assert isinstance(data, list)
        assert len(data) >= 2  # Garante que pelo menos 2 estúdios foram adicionados

    def test_delete_studio(self, client: TestClient) -> None:
        """Testa a exclusão de um estúdio."""
        payload = {"name": "DreamWorks"}
        create_response = client.post("/studios/", json=payload)
        studio_id = create_response.json()["id"]

        delete_response = client.delete(f"/studios/{studio_id}")
        assert delete_response.status_code == 204  # Deve retornar No Content

        # Verifica se o estúdio foi removido
        response = client.get(f"/studios/{studio_id}")
        assert response.status_code == 404  # Deve retornar Not Found

    def test_delete_studio_not_found(self, client: TestClient) -> None:
        """Testa a remoção de um estúdio inexistente."""
        response = client.delete("/studios/9999")  # ID que não existe

        assert response.status_code == 404
        assert response.json()["detail"] == "Studio not found"
