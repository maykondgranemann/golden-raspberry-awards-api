from fastapi.testclient import TestClient
from io import BytesIO
from pytest_mock import MockFixture


class TestAwardIntervalsAPI:
    """Testes para o endpoint `/awards/intervals`"""

    def test_get_award_intervals_with_imported_data(
        self, client: TestClient, csv_content_for_intervals: bytes
    ) -> None:
        """
        Testa o endpoint `/awards/intervals` após importar um CSV,
        garantindo que os intervalos são calculados corretamente.
        """
        # Enviar um CSV válido para o endpoint de upload
        files = {"file": ("test.csv", BytesIO(csv_content_for_intervals), "text/csv")}
        response = client.post("/csv/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["imported_movies"] > 0  # Deve importar filmes
        assert data["ignored_movies"] == 0  # Nenhum filme duplicado

        # Chamar o endpoint `/awards/intervals`
        response = client.get("/awards/intervals")
        assert response.status_code == 200

        data = response.json()
        assert "min" in data
        assert "max" in data

        # Verificar se os produtores com menor e maior
        # intervalo foram retornados corretamente
        min_intervals = data["min"]
        max_intervals = data["max"]

        assert len(min_intervals) > 0, "Deveria haver pelo menos um produtor no 'min'."
        assert len(max_intervals) > 0, "Deveria haver pelo menos um produtor no 'max'."

        # Exemplo de validação (ajustar conforme dados reais do CSV de teste)
        assert any(entry["producer"] == "Producer B" for entry in min_intervals)
        assert any(entry["producer"] == "Producer A" for entry in max_intervals)

    def test_get_award_intervals_no_data(self, client: TestClient) -> None:
        """
        Testa o endpoint `/awards/intervals` sem importar nenhum dado,
        garantindo que retorna listas vazias corretamente.
        """
        response = client.get("/awards/intervals")
        assert response.status_code == 200
        assert response.json() == {"min": [], "max": []}

    def test_get_award_intervals_database_error(
        self, client: TestClient, mocker: MockFixture
    ) -> None:
        """
        Testa se o endpoint `/awards/intervals` retorna erro 500 quando ocorre
        uma falha no banco de dados.
        """
        mocker.patch(
            "app.repositories.movie_repository.MovieRepository.get_winning_movies",
            side_effect=Exception("Erro no banco"),
        )
        response = client.get("/awards/intervals")

        assert response.status_code == 500
        assert "Erro no banco" in response.text
