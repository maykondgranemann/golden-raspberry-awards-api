import pytest
import pandas as pd
from pytest_mock import MockFixture
from app.repositories import MovieRepository, ProducerRepository, StudioRepository
from sqlalchemy.orm import Session
from app.services.csv_importer_service import CSVImporterService
from io import StringIO
from typing import Any, List, Dict


class TestCSVImporterServiceService:
    """
    Testes unitários para a classe CSVImporterService.
    """

    @pytest.fixture(scope="class")
    def sample_csv(self) -> str:
        """
        Retorna um exemplo de CSV em formato de string para testes.
        """
        return """year;title;studios;producers;winner
1980;Can't Stop the Music;Associated Film Distribution;Allan Carr;yes
1980;Cruising;Lorimar Productions, United Artists;Jerry Weintraub;
1983;The Lonely Lady;Universal Studios;Robert R. Weston;yes
1983;Two of a Kind;20th Century Fox;Roger M. Rothstein and Joe Wizan;
1984;Rhinestone;20th Century Fox;Marvin Worth and Howard Smith;
"""

    @pytest.fixture(scope="class")
    def df_sample(self, sample_csv: str) -> pd.DataFrame:
        """
        Retorna um DataFrame baseado no CSV de exemplo.
        """
        df: pd.DataFrame = pd.read_csv(StringIO(sample_csv), sep=";", dtype=str).fillna(
            ""
        )
        df.columns = df.columns.str.lower().str.strip()
        df["year"] = df["year"].str.strip()
        df["producers"] = df["producers"].str.strip()
        return df

    def test_import_csv(
        self, db_session: Session, mocker: MockFixture, df_sample: pd.DataFrame
    ) -> None:
        """
        Testa a importação completa do CSV.
        """
        mocker.patch.object(CSVImporterService, "_read_csv", return_value=df_sample)

        movies: List[Dict[str, Any]] = CSVImporterService.import_csv(
            db_session, "fake_path.csv"
        )

        assert isinstance(movies, list)
        assert len(movies) == 5
        assert movies[0]["year"] == 1980
        assert movies[0]["producers"] == ["Allan Carr"]
        assert movies[0]["winner"] is True

    def test_read_csv(self, sample_csv: str) -> None:
        """
        Testa a leitura do CSV garantindo que o DataFrame seja carregado corretamente.
        """
        df: pd.DataFrame = CSVImporterService._read_csv(StringIO(sample_csv))
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_validate_columns(self, df_sample: pd.DataFrame) -> None:
        """
        Testa se a validação das colunas funciona corretamente.
        """
        df_validated: pd.DataFrame = CSVImporterService._validate_columns(df_sample)
        assert isinstance(df_validated, pd.DataFrame)

    def test_validate_columns_missing(self) -> None:
        """
        Testa se a validação das colunas levanta erro quando há colunas faltando.
        """
        df_invalid = pd.DataFrame({"title": ["Movie 1"], "producers": ["John Doe"]})

        with pytest.raises(ValueError, match=r"Arquivo CSV inválido! Faltando: {.*}"):
            CSVImporterService._validate_columns(df_invalid)

    def test_normalize_columns(self, df_sample: pd.DataFrame) -> None:
        """
        Testa se a normalização dos nomes das colunas funciona corretamente.
        """
        df_normalized: pd.DataFrame = CSVImporterService._normalize_columns(df_sample)
        assert list(df_normalized.columns) == [
            "year",
            "title",
            "studios",
            "producers",
            "winner",
        ]

    def test_filter_valid_rows(self, df_sample: pd.DataFrame) -> None:
        """
        Testa se o filtro de linhas inválidas funciona corretamente.
        """
        df_filtered: pd.DataFrame = CSVImporterService._filter_valid_rows(df_sample)
        assert (
            len(df_filtered) == 5
        )  # Certifica-se de que todas as linhas sejam válidas

    def test_convert_data_types(self, df_sample: pd.DataFrame) -> None:
        """
        Testa a conversão da coluna 'year' para inteiro.
        """
        df_converted: pd.DataFrame = CSVImporterService._convert_data_types(df_sample)
        assert df_converted["year"].dtype == "int64"

    def test_normalize_winner_column(self, df_sample: pd.DataFrame) -> None:
        """
        Testa a normalização da coluna 'winner'.
        """
        df_normalized: pd.DataFrame = CSVImporterService._normalize_winner_column(
            df_sample
        )
        assert df_normalized["winner"].tolist() == [True, False, True, False, False]

    def test_split_producers(self, df_sample: pd.DataFrame) -> None:
        """
        Testa a separação da coluna 'producers' em listas corretamente.
        """
        df_split: pd.DataFrame = CSVImporterService._split_producers(df_sample)
        assert df_split["producers"].tolist() == [
            ["Allan Carr"],
            ["Jerry Weintraub"],
            ["Robert R. Weston"],
            ["Roger M. Rothstein", "Joe Wizan"],
            ["Marvin Worth", "Howard Smith"],
        ]

    def test_split_producers_with_multiple_separators(self) -> None:
        """
        Testa se a separação dos produtores funciona corretamente com
        diferentes separadores.
        """
        df_test = pd.DataFrame({"producers": ["John Doe, Jane Smith and Bob Brown"]})
        df_split: pd.DataFrame = CSVImporterService._split_producers(df_test)
        assert df_split["producers"].tolist() == [
            ["John Doe", "Jane Smith", "Bob Brown"]
        ]

    def test_split_studios(self, df_sample: pd.DataFrame) -> None:
        """
        Testa a separação da coluna 'studios' em listas corretamente.
        """
        df_split: pd.DataFrame = CSVImporterService._split_studios(df_sample)
        assert df_split["studios"].tolist() == [
            ["Associated Film Distribution"],
            ["Lorimar Productions", "United Artists"],
            ["Universal Studios"],
            ["20th Century Fox"],
            ["20th Century Fox"],
        ]

    def test_split_studios_with_multiple_separators(self) -> None:
        """
        Testa se a separação dos estúdios funciona corretamente com
        diferentes separadores.
        """
        df_test = pd.DataFrame(
            {"studios": ["Warner Bros, Paramount and Sony Pictures"]}
        )
        df_split: pd.DataFrame = CSVImporterService._split_studios(df_test)
        assert df_split["studios"].tolist() == [
            ["Warner Bros", "Paramount", "Sony Pictures"]
        ]

    def test_save_to_database(self, db_session: Session, sample_csv: str) -> None:
        """
        Testa se os filmes, produtores e estúdios são corretamente salvos
        no banco de dados.
        """
        df = pd.read_csv(StringIO(sample_csv), sep=";", dtype=str).fillna("")
        df.columns = df.columns.str.lower().str.strip()

        # Normaliza winner antes de passar para a função
        df = CSVImporterService._normalize_winner_column(df)

        # Chama o método de salvar no banco
        CSVImporterService.save_to_database(db_session, df.to_dict(orient="records"))

        db_session.commit()

        # Verifica se os filmes foram corretamente salvos
        movies = MovieRepository.get_all(db_session)

        assert len(movies) == 5  # Certifica-se de que todos os filmes foram inseridos

        # Verifica se os produtores foram salvos corretamente
        producers = ProducerRepository.get_all(db_session)
        assert len(producers) > 0  # Deve conter pelo menos os produtores do CSV

        # Verifica se os estúdios foram salvos corretamente
        studios = StudioRepository.get_all(db_session)
        assert len(studios) > 0  # Deve conter pelo menos os estúdios do CSV
