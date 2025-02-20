import re
import pandas as pd
from typing import cast
from typing import List, Dict, Set, Any, Union, IO
from app.repositories import MovieRepository, ProducerRepository, StudioRepository
from app.utils.logger import logger
from sqlalchemy.orm import Session


class CSVImporterService:
    """
    Classe responsável por importar, validar e processar arquivos CSV
    contendo informações
    sobre filmes e seus respectivos produtores premiados.
    """

    REQUIRED_COLUMNS: Set[str] = {"year", "producers", "winner"}
    # Facilmente expansível para novos separadores
    SEPARATORS: List[str] = [",", " and "]

    @classmethod
    def import_csv(cls, db: Session, filepath: str) -> List[Dict[str, Any]]:
        """
        Lê um arquivo CSV, valida os dados e retorna uma lista de dicionários com os
        filmes.

        :param filepath: Caminho para o arquivo CSV ou objeto IO.
        :return: Lista de dicionários representando os filmes e seus respectivos dados.
        :raises ValueError: Se ocorrer um erro na leitura do arquivo ou se
        os dados forem inválidos.
        """

        logger.info(f"Iniciando importação do CSV: {filepath}")

        df: pd.DataFrame = cls._read_csv(filepath)
        df = cls._validate_columns(df)
        df = cls._normalize_columns(df)
        df = cls._filter_valid_rows(df)
        df = cls._convert_data_types(df)
        df = cls._normalize_winner_column(df)
        df = cls._split_producers(df)
        df = cls._split_studios(df)

        movies_data = df.to_dict(orient="records")
        logger.success(
            f"Importação do CSV concluída com {len(movies_data)} registros válidos."
        )

        # Chama a função para salvar os dados no banco de dados
        cls.save_to_database(db, movies_data)

        return cast(List[Dict[str, Any]], movies_data)

    @staticmethod
    def _read_csv(filepath: Union[str, IO[str]]) -> pd.DataFrame:
        """
        Lê um arquivo CSV e retorna um DataFrame Pandas.

        :param filepath: Caminho para o arquivo CSV ou objeto IO.
        :return: DataFrame contendo os dados do arquivo CSV.
        :raises ValueError: Se ocorrer um erro ao ler o arquivo.
        """
        try:
            logger.info(f"Lendo arquivo CSV: {filepath}")
            df = pd.read_csv(filepath, sep=None, engine="python", dtype=str).fillna("")
            logger.info("Arquivo CSV carregado com sucesso.")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo CSV: {e}")
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
            logger.error(f"Colunas ausentes no CSV: {missing_columns}")
            raise ValueError(f"Arquivo CSV inválido! Faltando: {missing_columns}")

        logger.info("Todas as colunas essenciais estão presentes.")
        return df

    @staticmethod
    def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Renomeia as colunas para um formato padronizado.

        :param df: DataFrame contendo os dados do CSV.
        :return: DataFrame com colunas normalizadas.
        """
        df.columns = df.columns.str.lower().str.strip()
        logger.info("Colunas normalizadas.")
        return df

    @staticmethod
    def _filter_valid_rows(df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra apenas as linhas que possuem ano numérico e pelo menos um
        produtor válido.

        :param df: DataFrame contendo os dados do CSV.
        :return: DataFrame filtrado.
        """
        before_count = len(df)
        df = df[df["year"].str.isnumeric() & df["producers"].str.strip().ne("")]
        after_count = len(df)
        rm_count = before_count - after_count

        logger.info(f"Linhas filtradas: {rm_count} removidas, {after_count} válidas.")
        return df

    @staticmethod
    def _convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
        """
        Converte a coluna 'year' para inteiro.

        :param df: DataFrame contendo os dados do CSV.
        :return: DataFrame com tipos convertidos.
        """
        df["year"] = df["year"].astype(int)

        logger.info("Coluna 'year' convertida para inteiro.")
        return df

    @staticmethod
    def _normalize_winner_column(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza a coluna 'winner', convertendo valores para booleano.

        :param df: DataFrame contendo os dados do CSV.
        :return: DataFrame com valores booleanos na coluna 'winner'.
        """
        df["winner"] = df["winner"].str.lower().str.strip().eq("yes")

        logger.info("Coluna 'winner' normalizada para booleano.")
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

        logger.info("Coluna 'producers' dividida corretamente.")
        return df

    @classmethod
    def _split_studios(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Divide a coluna 'studios' em listas de estudios individuais.

        :param df: DataFrame contendo os dados do CSV.
        :return: DataFrame com a coluna 'studios' ajustada para listas de nomes.
        """
        split_pattern: str = (
            r"\s*" + r"\s*|\s*".join(map(re.escape, cls.SEPARATORS)) + r"\s*"
        )

        df["studios"] = df["studios"].apply(
            lambda x: [
                studio.strip()
                for studio in re.split(split_pattern, x)
                if studio.strip()
            ]
        )
        logger.info("Coluna 'studios' dividida corretamente.")
        return df

    @classmethod
    def save_to_database(cls, db: Session, movies_data: List[Dict[str, Any]]) -> None:
        """
        Salva os filmes, produtores e estúdios no banco de dados e
        estabelece os relacionamentos.

        :param db: Sessão do banco de dados.
        :param movies_data: Lista de dicionários representando os filmes importados.
        """
        logger.info("Salvando os dados no banco de dados...")

        for movie_data in movies_data:
            title = movie_data["title"]
            year = movie_data["year"]
            winner = movie_data["winner"]
            producer_names = movie_data["producers"]
            studio_names = movie_data["studios"]

            # Criar ou recuperar o filme
            movie = MovieRepository.create(db, title, year, winner)

            if movie is None:
                raise ValueError(
                    f"Erro ao criar ou recuperar o filme: {title} ({year})"
                )

            # Criar ou recuperar produtores e associar ao filme
            producers = ProducerRepository.create_multiple(db, producer_names)
            movie.producers.extend(producers)

            # Criar ou recuperar estúdios e associar ao filme
            studios = StudioRepository.create_multiple(db, studio_names)
            movie.studios.extend(studios)

            db.commit()  # Confirma as operações no banco de dados
            logger.info(f"Filme '{title}' ({year}) salvo com sucesso.")

        logger.success(
            "Todos os filmes e seus relacionamentos foram salvos no banco de dados."
        )
