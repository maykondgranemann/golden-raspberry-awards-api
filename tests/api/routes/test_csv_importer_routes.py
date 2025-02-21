from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from io import BytesIO
from app.repositories.movie_repository import MovieRepository


def test_upload_csv(
    client: TestClient, db_session: Session, csv_content: bytes
) -> None:
    """
    Testa o endpoint de upload de CSV e verifica a importação dos dados.
    """
    files = {"file": ("test.csv", BytesIO(csv_content), "text/csv")}
    response = client.post("/csv/upload", files=files)

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Importação concluída com sucesso!"
    assert data["imported_movies"] == 3
    assert data["ignored_movies"] == 0

    # Verificar se os filmes foram inseridos corretamente no banco de dados
    movies = MovieRepository.get_all(db_session)
    assert len(movies) == 3


def test_upload_duplicate_csv(
    client: TestClient, db_session: Session, csv_content: bytes
) -> None:
    """
    Testa o upload do mesmo CSV duas vezes e verifica se a segunda vez ignora
    os registros duplicados.
    """
    files = {"file": ("test.csv", BytesIO(csv_content), "text/csv")}

    # Primeira importação
    response1 = client.post("/csv/upload", files=files)
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["imported_movies"] == 3
    assert data1["ignored_movies"] == 0

    # Segunda importação do mesmo arquivo
    response2 = client.post("/csv/upload", files=files)
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["imported_movies"] == 0
    assert data2["ignored_movies"] == 3  # Todos já existem no banco

    # Verifica se o banco tem apenas 3 registros e não duplicou
    movies = MovieRepository.get_all(db_session)
    assert len(movies) == 3


def test_upload_invalid_file_format(client: TestClient) -> None:
    """
    Testa o upload de um arquivo inválido (não CSV) e verifica se retorna erro 400.
    """
    files = {"file": ("test.txt", BytesIO(b"Este nao eh um CSV"), "text/plain")}
    response = client.post("/csv/upload", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "O arquivo deve ser um CSV."


def test_upload_corrupted_csv(client: TestClient) -> None:
    """
    Testa o upload de um CSV corrompido e verifica se retorna erro 500.
    """
    files = {
        "file": ("test.csv", BytesIO(b"year;title\n1980;Missing Columns"), "text/csv")
    }
    response = client.post("/csv/upload", files=files)

    assert response.status_code == 500
    assert "Erro ao processar o CSV" in response.json()["detail"]
