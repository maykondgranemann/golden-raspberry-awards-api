import pytest
import pandas as pd
from pytest_mock import MockFixture
from app.services.csv_importer import CSVImporter
from io import StringIO
from typing import Any, List, Dict


class TestCSVImporter:
    """
    Testes unitários para a classe CSVImporter.
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

    def test_import_csv(self, mocker: MockFixture, df_sample: pd.DataFrame) -> None:
        """
        Testa a importação completa do CSV.
        """
        mocker.patch.object(CSVImporter, "_read_csv", return_value=df_sample)

        movies: List[Dict[str, Any]] = CSVImporter.import_csv("fake_path.csv")

        assert isinstance(movies, list)
        assert len(movies) == 5
        assert movies[0]["year"] == 1980
        assert movies[0]["producers"] == ["Allan Carr"]
        assert movies[0]["winner"] is True

    def test_read_csv(self, sample_csv: str) -> None:
        """
        Testa a leitura do CSV garantindo que o DataFrame seja carregado corretamente.
        """
        df: pd.DataFrame = CSVImporter._read_csv(StringIO(sample_csv))
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_validate_columns(self, df_sample: pd.DataFrame) -> None:
        """
        Testa se a validação das colunas funciona corretamente.
        """
        df_validated: pd.DataFrame = CSVImporter._validate_columns(df_sample)
        assert isinstance(df_validated, pd.DataFrame)

    def test_validate_columns_missing(self) -> None:
        """
        Testa se a validação das colunas levanta erro quando há colunas faltando.
        """
        df_invalid = pd.DataFrame({"title": ["Movie 1"], "producers": ["John Doe"]})

        with pytest.raises(ValueError, match=r"Arquivo CSV inválido! Faltando: {.*}"):
            CSVImporter._validate_columns(df_invalid)

    def test_normalize_columns(self, df_sample: pd.DataFrame) -> None:
        """
        Testa se a normalização dos nomes das colunas funciona corretamente.
        """
        df_normalized: pd.DataFrame = CSVImporter._normalize_columns(df_sample)
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
        df_filtered: pd.DataFrame = CSVImporter._filter_valid_rows(df_sample)
        assert (
            len(df_filtered) == 5
        )  # Certifica-se de que todas as linhas sejam válidas

    def test_convert_data_types(self, df_sample: pd.DataFrame) -> None:
        """
        Testa a conversão da coluna 'year' para inteiro.
        """
        df_converted: pd.DataFrame = CSVImporter._convert_data_types(df_sample)
        assert df_converted["year"].dtype == "int64"

    def test_normalize_winner_column(self, df_sample: pd.DataFrame) -> None:
        """
        Testa a normalização da coluna 'winner'.
        """
        df_normalized: pd.DataFrame = CSVImporter._normalize_winner_column(df_sample)
        assert df_normalized["winner"].tolist() == [True, False, True, False, False]

    def test_split_producers(self, df_sample: pd.DataFrame) -> None:
        """
        Testa a separação da coluna 'producers' em listas corretamente.
        """
        df_split: pd.DataFrame = CSVImporter._split_producers(df_sample)
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
        df_split: pd.DataFrame = CSVImporter._split_producers(df_test)
        assert df_split["producers"].tolist() == [
            ["John Doe", "Jane Smith", "Bob Brown"]
        ]
