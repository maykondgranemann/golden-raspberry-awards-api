import re
import pandas as pd
from typing import cast
from typing import List, Dict, Set, Any, Union, IO


class CSVImporter:
    """
    Classe responsável por importar, validar e processar arquivos CSV
    contendo informações
    sobre filmes e seus respectivos produtores premiados.
    """

    REQUIRED_COLUMNS: Set[str] = {"year", "producers", "winner"}
    # Facilmente expansível para novos separadores
    SEPARATORS: List[str] = [",", " and "]

    @classmethod
    def import_csv(cls, filepath: Union[str, IO[str]]) -> List[Dict[str, Any]]:
        """
        Lê um arquivo CSV, valida os dados e retorna uma lista de dicionários com os
        filmes.

        :param filepath: Caminho para o arquivo CSV ou objeto IO.
        :return: Lista de dicionários representando os filmes e seus respectivos dados.
        :raises ValueError: Se ocorrer um erro na leitura do arquivo ou se
        os dados forem inválidos.
        """
        df: pd.DataFrame = cls._read_csv(filepath)
        df = cls._validate_columns(df)
        df = cls._normalize_columns(df)
        df = cls._filter_valid_rows(df)
        df = cls._convert_data_types(df)
        df = cls._normalize_winner_column(df)
        df = cls._split_producers(df)

        return cast(List[Dict[str, Any]], df.to_dict(orient="records"))

    @staticmethod
    def _read_csv(filepath: Union[str, IO[str]]) -> pd.DataFrame:
        """
        Lê um arquivo CSV e retorna um DataFrame Pandas.

        :param filepath: Caminho para o arquivo CSV ou objeto IO.
        :return: DataFrame contendo os dados do arquivo CSV.
        :raises ValueError: Se ocorrer um erro ao ler o arquivo.
        """
        try:
            return pd.read_csv(filepath, sep=None, engine="python", dtype=str).fillna(
                ""
            )
        except Exception as e:
            raise ValueError(f"Erro ao ler o arquivo CSV: {e}")

    @classmethod
    def _validate_columns(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida se as colunas essenciais existem no DataFrame.

        :param df: DataFrame contendo os dados do CSV.
        :return: DataFrame validado.
        :raises ValueError: Se colunas essenciais estiverem ausentes.
        """
        missing_columns: Set[str] = cls.REQUIRED_COLUMNS - set(
            df.columns.str.lower().str.strip()
        )
        if missing_columns:
            raise ValueError(f"Arquivo CSV inválido! Faltando: {missing_columns}")
        return df

    @staticmethod
    def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Renomeia as colunas para um formato padronizado.

        :param df: DataFrame contendo os dados do CSV.
        :return: DataFrame com colunas normalizadas.
        """
        df.columns = df.columns.str.lower().str.strip()
        return df

    @staticmethod
    def _filter_valid_rows(df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra apenas as linhas que possuem ano numérico e pelo menos um
        produtor válido.

        :param df: DataFrame contendo os dados do CSV.
        :return: DataFrame filtrado.
        """
        return df[df["year"].str.isnumeric() & df["producers"].str.strip().ne("")]

    @staticmethod
    def _convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
        """
        Converte a coluna 'year' para inteiro.

        :param df: DataFrame contendo os dados do CSV.
        :return: DataFrame com tipos convertidos.
        """
        df["year"] = df["year"].astype(int)
        return df

    @staticmethod
    def _normalize_winner_column(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza a coluna 'winner', convertendo valores para booleano.

        :param df: DataFrame contendo os dados do CSV.
        :return: DataFrame com valores booleanos na coluna 'winner'.
        """
        df["winner"] = df["winner"].str.lower().str.strip().eq("yes")
        return df

    @classmethod
    def _split_producers(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Divide a coluna 'producers' em listas de produtores individuais.

        :param df: DataFrame contendo os dados do CSV.
        :return: DataFrame com a coluna 'producers' ajustada para listas de nomes.
        """
        split_pattern: str = (
            r"\s*" + r"\s*|\s*".join(map(re.escape, cls.SEPARATORS)) + r"\s*"
        )

        df["producers"] = df["producers"].apply(
            lambda x: [
                producer.strip()
                for producer in re.split(split_pattern, x)
                if producer.strip()
            ]
        )

        return df
