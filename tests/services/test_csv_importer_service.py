import pandas as pd
from pytest_mock import MockFixture
from app.repositories import MovieRepository, ProducerRepository, StudioRepository
from sqlalchemy.orm import Session
from app.services.csv_importer_service import CSVImporterService
from app.schemas.csv_importer import CSVImportRequest, CSVImportResponse


class TestCSVImporterService:
    """
    Testes unitários para a classe CSVImporterService.
    """

    def test_import_csv(
        self, db_session: Session, mocker: MockFixture, df_sample: pd.DataFrame
    ) -> None:
        """
        Testa a importação completa do CSV e valida a resposta.
        """
        # Mock para evitar leitura real de arquivos
        mocker.patch.object(CSVImporterService, "_load_csv", return_value=df_sample)

        response: CSVImportResponse = CSVImporterService.import_csv(
            db_session, "fake_csv_content"
        )

        assert isinstance(response, CSVImportResponse)
        assert response.imported_movies == 5
        assert response.message == "Importação concluída com sucesso!"

    def test_load_csv(self, sample_csv: str) -> None:
        """
        Testa a leitura do CSV garantindo que o DataFrame seja carregado corretamente.
        """
        df: pd.DataFrame = CSVImporterService._load_csv(sample_csv)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "title" in df.columns
        assert "year" in df.columns

    def test_load_csv_from_file(
        self, mocker: MockFixture, df_sample: pd.DataFrame
    ) -> None:
        """
        Testa a leitura do CSV a partir de um arquivo no disco.
        """
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch.object(pd, "read_csv", return_value=df_sample)

        df: pd.DataFrame = CSVImporterService._load_csv_from_file("fake_path.csv")
        assert not df.empty
        assert len(df) == 5

    def test_load_csv_on_startup(
        self, db_session: Session, mocker: MockFixture, df_sample: pd.DataFrame
    ) -> None:
        """
        Testa a importação automática de CSVs ao iniciar a aplicação.
        """
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.listdir", return_value=["movies.csv"])
        mocker.patch.object(
            CSVImporterService, "_load_csv_from_file", return_value=df_sample
        )

        CSVImporterService.load_csv_on_startup(db_session, "data")

        movies = MovieRepository.get_all(db_session)
        assert len(movies) == 5

    def test_validate_and_prepare(self, df_sample: pd.DataFrame) -> None:
        """
        Testa se a validação e formatação dos dados ocorre corretamente.
        """
        df_validated: pd.DataFrame = CSVImporterService._validate_and_prepare(df_sample)
        assert isinstance(df_validated, pd.DataFrame)
        assert df_validated["year"].dtype == "int64"
        assert all(
            isinstance(producers, list) for producers in df_validated["producers"]
        )
        assert all(isinstance(studios, list) for studios in df_validated["studios"])

    def test_save_to_database(
        self, db_session: Session, df_sample: pd.DataFrame
    ) -> None:
        """
        Testa se os filmes, produtores e estúdios são corretamente
        salvos no banco de dados.
        """
        movies_data = [
            CSVImportRequest(
                title=row["title"],
                year=row["year"],
                winner=(
                    row["winner"].strip().lower() == "yes"
                    if isinstance(row["winner"], str)
                    else bool(row["winner"])
                ),
                producers=(
                    row["producers"]
                    if isinstance(row["producers"], list)
                    else [row["producers"]]
                ),
                studios=(
                    row["studios"]
                    if isinstance(row["studios"], list)
                    else [row["studios"]]
                ),
            )
            for _, row in df_sample.iterrows()
        ]

        CSVImporterService._save_to_database(db_session, movies_data)
        db_session.commit()

        movies = MovieRepository.get_all(db_session)
        assert len(movies) == 5

        producers = ProducerRepository.get_all(db_session)
        assert len(producers) > 0

        studios = StudioRepository.get_all(db_session)
        assert len(studios) > 0
