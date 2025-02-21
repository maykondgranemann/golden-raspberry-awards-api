import time
from fastapi.testclient import TestClient
from io import BytesIO
from pytest_mock import MockFixture


class TestAwardIntervalsAPI:
    """Testes para os endpoints `/awards/intervals` e `/awards/invalidate-cache`"""

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

        # Chamar o endpoint `/awards/intervals` para calcular e armazenar no cache
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

        # Exemplo de validação
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

    def test_get_award_intervals_cache_usage(self, client: TestClient) -> None:
        """
        Testa se o cache está sendo utilizado corretamente no
        endpoint `/awards/intervals`.
        """
        # Primeira chamada (deve armazenar no cache)
        response = client.get("/awards/intervals")
        assert response.status_code == 200

        # Segunda chamada (deve usar o cache)
        response = client.get("/awards/intervals")
        assert response.status_code == 200

    def test_invalidate_cache(self, client: TestClient) -> None:
        """
        Testa se o endpoint `/awards/invalidate-cache` reseta corretamente o cache.
        """
        # Primeira chamada (deve armazenar no cache)
        response = client.get("/awards/intervals")
        assert response.status_code == 200

        # Invalida o cache
        response = client.post("/awards/invalidate-cache")
        assert response.status_code == 200
        assert response.json() == {"message": "Cache invalidado com sucesso"}

        # Nova chamada deve recalcular e não usar o cache antigo
        response = client.get("/awards/intervals")
        assert response.status_code == 200

    def test_get_award_intervals_database_error(
        self, client: TestClient, mocker: MockFixture
    ) -> None:
        """
        Testa se o endpoint `/awards/intervals` retorna erro 500 quando ocorre
        uma falha no banco de dados.
        """
        # Invalida o cache antes para garantir que o erro venha do banco
        client.post("/awards/invalidate-cache")

        mocker.patch(
            "app.repositories.movie_repository.MovieRepository.get_winning_movies",
            side_effect=Exception("Erro no banco"),
        )
        response = client.get("/awards/intervals")

        assert response.status_code == 500
        assert "Erro no banco" in response.text

    def test_get_award_intervals_cache_performance(
        self, client: TestClient, csv_content_for_intervals: bytes
    ) -> None:
        """
        Testa se a resposta do endpoint `/awards/intervals` é mais rápida na
        segunda chamada devido ao cache.
        """
        # Enviar um CSV válido para o endpoint de upload
        files = {"file": ("test.csv", BytesIO(csv_content_for_intervals), "text/csv")}
        response = client.post("/csv/upload", files=files)
        assert response.status_code == 200

        # Primeira chamada ao endpoint (sem cache)
        start_time = time.perf_counter()
        response1 = client.get("/awards/intervals")
        end_time = time.perf_counter()
        assert response1.status_code == 200
        uncached_duration = end_time - start_time

        # Segunda chamada ao endpoint (com cache)
        start_time = time.perf_counter()
        response2 = client.get("/awards/intervals")
        end_time = time.perf_counter()
        assert response2.status_code == 200
        cached_duration = end_time - start_time

        # Verificações
        assert cached_duration < uncached_duration, (
            f"A segunda chamada ({cached_duration:.6f}s) deve ser mais rápida "
            f"que a primeira ({uncached_duration:.6f}s)"
        )

    def test_get_award_intervals_cache_consistency(
        self, client: TestClient, csv_content_for_intervals: bytes
    ) -> None:
        """
        Testa se os valores retornados pelo cache são consistentes
        ao chamar `/awards/intervals` múltiplas vezes.
        """
        # Enviar um CSV válido para garantir dados para teste
        files = {"file": ("test.csv", BytesIO(csv_content_for_intervals), "text/csv")}
        response = client.post("/csv/upload", files=files)
        assert response.status_code == 200

        # Primeira chamada ao endpoint (sem cache)
        response1 = client.get("/awards/intervals")
        assert response1.status_code == 200
        data1 = response1.json()

        # Segunda chamada ao endpoint (com cache)
        response2 = client.get("/awards/intervals")
        assert response2.status_code == 200
        data2 = response2.json()

        # Verificar se os valores do cache são idênticos aos da primeira resposta
        assert (
            data1 == data2
        ), "Os dados retornados pelo cache devem ser idênticos à primeira chamada!"

    def test_cache_invalidation_and_recalculation(
        self,
        client: TestClient,
        csv_content_for_intervals: bytes,
        csv_content_for_second_upload: bytes,
    ) -> None:
        """
        Testa se o cache é invalidado corretamente quando novos dados
        são processados após a importação de um novo CSV.
        """

        # Importar o primeiro conjunto de dados
        files = {"file": ("test.csv", BytesIO(csv_content_for_intervals), "text/csv")}
        response = client.post("/csv/upload", files=files)
        assert response.status_code == 200

        # Fazer a primeira chamada ao endpoint e verifica resposta
        response = client.get("/awards/intervals")
        assert response.status_code == 200
        data_before = response.json()

        # Garantir que o cache foi criado
        assert "min" in data_before and "max" in data_before
        assert len(data_before["min"]) > 0
        assert len(data_before["max"]) > 0

        # Importar um novo conjunto de dados
        files = {
            "file": ("test2.csv", BytesIO(csv_content_for_second_upload), "text/csv")
        }
        response = client.post("/csv/upload", files=files)
        assert response.status_code == 200

        # Invalidar o cache manualmente
        response = client.post("/awards/invalidate-cache")
        assert response.status_code == 200
        assert response.json() == {"message": "Cache invalidado com sucesso"}

        # Fazer uma nova chamada e garantir que os dados mudaram
        response = client.get("/awards/intervals")
        assert response.status_code == 200
        data_after = response.json()

        # Os dados antes e depois devem ser diferentes,
        # pois novos filmes foram importados
        assert data_before != data_after, "O cache não foi invalidado corretamente"

        # Verificar a nova resposta do endpoint
        assert "min" in data_after and "max" in data_after
        assert len(data_after["min"]) > 0
        assert len(data_after["max"]) > 0

    def test_cache_auto_invalidation_on_csv_import(
        self,
        client: TestClient,
        csv_content_for_intervals: bytes,
        csv_content_for_second_upload: bytes,
    ) -> None:
        """
        Testa se o cache é invalidado automaticamente pela service csv_importer_service
        quando novos dados são processados após a importação de um novo CSV.
        """

        # Importar o primeiro conjunto de dados
        files = {"file": ("test.csv", BytesIO(csv_content_for_intervals), "text/csv")}
        response = client.post("/csv/upload", files=files)
        assert response.status_code == 200

        # Fazer a primeira chamada ao endpoint e verifica resposta
        response = client.get("/awards/intervals")
        assert response.status_code == 200
        data_before = response.json()

        # Garantir que o cache foi criado
        assert "min" in data_before and "max" in data_before
        assert len(data_before["min"]) > 0
        assert len(data_before["max"]) > 0

        # Importar um novo conjunto de dados
        files = {
            "file": ("test2.csv", BytesIO(csv_content_for_second_upload), "text/csv")
        }
        response = client.post("/csv/upload", files=files)
        assert response.status_code == 200

        # Fazer uma nova chamada e garantir que os dados mudaram
        response = client.get("/awards/intervals")
        assert response.status_code == 200
        data_after = response.json()

        # Os dados antes e depois devem ser diferentes,
        # pois novos filmes foram importados
        assert data_before != data_after, "O cache não foi invalidado corretamente"

        # Verificar a nova resposta do endpoint
        assert "min" in data_after and "max" in data_after
        assert len(data_after["min"]) > 0
        assert len(data_after["max"]) > 0
