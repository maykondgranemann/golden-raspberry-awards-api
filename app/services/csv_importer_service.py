import os
import re
from sqlalchemy.exc import IntegrityError
import pandas as pd
from typing import List
from sqlalchemy.orm import Session
from app.schemas.csv_importer import CSVImportRequest, CSVImportResponse
from app.repositories import MovieRepository, ProducerRepository, StudioRepository
from app.utils.logger import logger


class CSVImporterService:
    """
    Service responsável por processar e importar dados de um arquivo CSV
    contendo informações de filmes.
    """

    total_inserted: int = 0  # Contador de filmes inseridos
    ignored_count: int = 0  # Contador de filmes ignorados (duplicados)

    REQUIRED_COLUMNS = {"year", "producers", "winner"}
    SEPARATORS = [", and ", ",", " and "]  # Pode ser expandido se necessário

    @classmethod
    def import_csv(cls, db: Session, file_content: str) -> CSVImportResponse:
        """
        Processa o conteúdo do CSV e salva os dados no banco.

        :param db: Sessão do banco de dados.
        :param file_content: Conteúdo do CSV como string.
        :return: CSVImportResponse contendo o número de filmes importados.
        """
        logger.info("Iniciando importação do CSV.")

        df = cls._load_csv(file_content)
        df = cls._validate_and_prepare(df)

        movies_data = [
            CSVImportRequest(
                title=row["title"],
                year=row["year"],
                winner=row["winner"],
                producers=row["producers"],
                studios=row["studios"],
            )
            for _, row in df.iterrows()
        ]

        cls._save_to_database(db, movies_data)

        return CSVImportResponse(
            message="Importação concluída com sucesso!",
            imported_movies=cls.total_inserted,
            ignored_movies=cls.ignored_count,
        )

    @staticmethod
    def _load_csv(file_content: str) -> pd.DataFrame:
        """Carrega o CSV a partir de uma string e retorna um DataFrame."""
        try:
            df = pd.read_csv(
                pd.io.common.StringIO(file_content),
                sep=None,
                engine="python",
                dtype=str,
            ).fillna("")
            logger.info("Arquivo CSV carregado com sucesso.")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo CSV: {e}")
            raise ValueError(f"Erro ao ler o arquivo CSV: {e}")

    @staticmethod
    def _load_csv_from_file(filepath: str) -> pd.DataFrame:
        """
        Carrega um CSV a partir de um caminho no sistema de arquivos.

        :param filepath: Caminho absoluto do arquivo CSV.
        :return: DataFrame contendo os dados.
        """
        if not os.path.exists(filepath):
            logger.warning(f"Arquivo CSV '{filepath}' não encontrado.")
            return pd.DataFrame()

        try:
            logger.info(f"Lendo CSV do arquivo: {filepath}")
            df = pd.read_csv(filepath, sep=None, engine="python", dtype=str).fillna("")
            logger.info("Arquivo CSV carregado com sucesso.")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo '{filepath}': {e}")
            raise ValueError(f"Erro ao ler o arquivo '{filepath}': {e}")

    @classmethod
    def load_csv_on_startup(cls, db: Session, directory: str = "data") -> None:
        """
        Procura arquivos CSV na pasta `data/` e carrega o primeiro encontrado.

        :param db: Sessão do banco de dados.
        :param directory: Diretório onde os CSVs devem ser buscados.
        """
        if not os.path.exists(directory):
            logger.warning(f"Pasta '{directory}' não encontrada.")
            return

        csv_files = [f for f in os.listdir(directory) if f.endswith(".csv")]
        if not csv_files:
            logger.info("Nenhum arquivo CSV encontrado para importação automática.")
            return

        filepath = os.path.join(
            directory, csv_files[0]
        )  # Usa o primeiro CSV encontrado
        logger.info(f"Importando CSV automaticamente: {filepath}")

        df = cls._load_csv_from_file(filepath)
        if df.empty:
            logger.warning(f"Arquivo CSV '{filepath}' está vazio ou inválido.")
            return

        df = cls._validate_and_prepare(df)
        movies_data = [
            CSVImportRequest(
                title=row["title"],
                year=row["year"],
                winner=row["winner"],
                producers=row["producers"],
                studios=row["studios"],
            )
            for _, row in df.iterrows()
        ]

        cls._save_to_database(db, movies_data)
        logger.success(
            f"Importação automática concluída: {len(movies_data)} filmes importados."
        )

    @classmethod
    def _validate_and_prepare(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Valida e transforma os dados do CSV."""
        missing_columns = cls.REQUIRED_COLUMNS - set(df.columns.str.lower().str.strip())
        if missing_columns:
            raise ValueError(f"Colunas ausentes: {missing_columns}")

        df.columns = df.columns.str.lower().str.strip()
        df = df[df["year"].str.isnumeric()]
        df["year"] = df["year"].astype(int)
        df["winner"] = df["winner"].str.lower().str.strip().eq("yes")

        df["producers"] = df["producers"].apply(lambda x: cls._split_values(x))
        df["studios"] = df["studios"].apply(lambda x: cls._split_values(x))

        return df

    @classmethod
    def _split_values(cls, value: str) -> List[str]:
        """Divide valores separados por delimitadores comuns."""
        pattern = r"\s*" + r"\s*|\s*".join(map(re.escape, cls.SEPARATORS)) + r"\s*"
        return [v.strip() for v in re.split(pattern, value) if v.strip()]

    @classmethod
    def _save_to_database(
        cls, db: Session, movies_data: List[CSVImportRequest]
    ) -> None:
        """Salva os filmes no banco de dados e contabiliza
        os ignorados por duplicação."""
        cls.ignored_count = 0  # Contador de filmes ignorados

        for movie_data in movies_data:
            try:
                # Tenta criar o filme, se já existir a exceção é capturada
                movie = MovieRepository.create(
                    db, movie_data.title, movie_data.year, movie_data.winner
                )

                # Criar produtores e associar ao filme
                producers = ProducerRepository.create_multiple(db, movie_data.producers)
                movie.producers.extend(producers)
                db.commit()  # Salva no banco

                # Criar estúdios e associar ao filme
                studios = StudioRepository.create_multiple(db, movie_data.studios)
                movie.studios.extend(studios)
                db.commit()  # Salva no banco

            except IntegrityError:
                db.rollback()  # Desfaz a tentativa de inserção
                cls.ignored_count += 1  # Incrementa o contador
                logger.warning(
                    f"Filme '{movie_data.title}' ({movie_data.year}) "
                    "já existente. Ignorado."
                )

        cls.total_inserted = len(movies_data) - cls.ignored_count
        logger.success(
            f"{cls.total_inserted} filmes inseridos, "
            "{cls.ignored_count} ignorados por duplicação."
        )
