from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound
from app.models.movie import Movie
from typing import List, Optional
from loguru import logger


class MovieRepository:
    """
    Repository responsável por operações no banco de dados relacionadas a filmes.
    """

    @staticmethod
    def create(db: Session, title: str, year: int, winner: bool) -> Movie:
        """
         Cria um novo filme e o salva no banco de dados.

        Args:
            db (Session): Sessão do banco de dados.
            title (str): Título do filme.
            year (int): Ano de lançamento do filme.
            winner (bool): Indica se o filme foi vencedor do prêmio.

        Returns:
            Movie: Objeto Movie criado ou existente.
        """
        movie = Movie(title=title, year=year, winner=winner)
        db.add(movie)
        try:
            db.commit()
            db.refresh(movie)
            logger.info(f"Novo filme cadastrado: {title} ({year}) - {winner}")
            return movie
        except IntegrityError:
            db.rollback()
            existing_movie = db.query(Movie).filter(Movie.title == title).first()
            if existing_movie:
                logger.warning(
                    f"Filme '{title}' já existe, retornando instância existente."
                )
                return existing_movie
            else:
                logger.error(f"Erro inesperado ao inserir filme '{title}'.")
                raise ValueError(
                    f"Erro ao criar ou recuperar o filme: {title} ({year})"
                )

    @staticmethod
    def get_by_id(db: Session, movie_id: int) -> Optional[Movie]:
        """
        Obtém um filme pelo ID.

        Args:
            db (Session): Sessão do banco de dados.
            movie_id (int): ID do filme.

        Returns:
            Optional[Movie]: O filme encontrado ou None se não existir.
        """
        try:
            return db.query(Movie).filter(Movie.id == movie_id).one()
        except NoResultFound:
            logger.warning(f"Filme com ID {movie_id} não encontrado.")
            return None

    @staticmethod
    def get_by_title(db: Session, title: str) -> Optional[Movie]:
        """
        Busca um filme pelo título.

        :param db: Sessão do banco de dados.
        :param title: Título do filme.
        :return: Objeto Movie se encontrado, caso contrário, None.
        """
        return db.query(Movie).filter(Movie.title == title).first()

    @staticmethod
    def get_all(db: Session, expand: List[str] = []) -> List[Movie]:
        """
        Retorna todos os filmes do banco, podendo opcionalmente carregar
        produtores e estúdios.

        :param db: Sessão do banco de dados.
        :param expand: Lista de expansões desejadas, ex: ["producers", "studios"]
        :return: Lista de objetos Movie.
        """
        query = db.query(Movie)

        if "producers" in expand:
            query = query.options(joinedload(Movie.producers))
        if "studios" in expand:
            query = query.options(joinedload(Movie.studios))

        return query.all()

    @staticmethod
    def delete(db: Session, movie_id: int) -> bool:
        """
        Remove um filme do banco de dados.

        :param db: Sessão do banco de dados.
        :param movie_id: ID do filme a ser removido.
        :return: True se o filme foi removido, False se não foi encontrado.
        """
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if movie:
            db.delete(movie)
            db.commit()
            logger.info(f"Filme '{movie.title}' removido com sucesso.")
            return True

        logger.warning(
            f"Tentativa de remover filme com ID {movie_id}, mas ele não existe."
        )
        return False

    @staticmethod
    def get_winning_movies(db: Session) -> List[Movie]:
        """
        Retorna todos os filmes vencedores e
        inclui os produtores e estúdios associados.

        :param db: Sessão do banco de dados.
        :return: Lista de filmes vencedores.
        """
        return (
            db.query(Movie)
            .filter(Movie.winner.is_(True))
            .options(joinedload(Movie.producers), joinedload(Movie.studios))
            .order_by(Movie.year)
            .all()
        )
