from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound
from app.models.movie import Movie
from typing import List, Optional
from loguru import logger


class MovieRepository:
    """
    Repository responsável por operações no banco de dados relacionadas a filmes.
    """

    @staticmethod
    def create(db: Session, title: str, year: int) -> Optional[Movie]:
        """
        Cria um novo filme no banco de dados.

        :param db: Sessão do banco de dados.
        :param title: Título do filme.
        :param year: Ano de lançamento do filme.
        :return: Objeto Movie criado ou encontrado.
        """
        movie: Optional[Movie] = Movie(title=title, year=year)
        db.add(movie)
        try:
            db.commit()
            db.refresh(movie)
            logger.info(f"Novo filme cadastrado: {title} ({year})")
        except IntegrityError:
            db.rollback()
            movie = db.query(Movie).filter(Movie.title == title).first()
            if movie:
                logger.warning(
                    f"Filme '{title}' já existe, retornando instância existente."
                )
            else:
                logger.error(f"Erro inesperado ao inserir filme '{title}'.")
                raise  # Relança a exceção se o filme não for encontrado

        return movie

    @staticmethod
    def get_by_id(db: Session, movie_id: int) -> Optional[Movie]:
        """
        Busca um filme pelo ID.

        :param db: Sessão do banco de dados.
        :param movie_id: ID do filme.
        :return: Objeto Movie se encontrado, caso contrário, None.
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
    def get_all(db: Session) -> List[Movie]:
        """
        Retorna todos os filmes cadastrados no banco.

        :param db: Sessão do banco de dados.
        :return: Lista de objetos Movie.
        """
        return db.query(Movie).all()

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
