from sqlalchemy.orm import Session
from app.models.studio import Studio
from typing import List, Optional
from sqlalchemy.exc import IntegrityError, NoResultFound
from loguru import logger


class StudioRepository:
    """
    Repository responsável por operações no banco de dados relacionadas aos estúdios.
    """

    @staticmethod
    def create(db: Session, name: str) -> Studio:
        """
        Cria um novo estúdio no banco de dados.

        :param db: Sessão do banco de dados.
        :param name: Nome do estúdio.
        :return: Objeto Studio.
        """
        studio = Studio(name=name)
        db.add(studio)
        try:
            db.commit()
            db.refresh(studio)
            logger.info(f"Novo estúdio cadastrado: {name}")
            return studio  # Sempre retorna um Studio válido
        except IntegrityError:
            db.rollback()
            existing_studio = db.query(Studio).filter(Studio.name == name).first()
            if existing_studio is not None:
                logger.warning(
                    f"Estúdio '{name}' já existe, retornando instância existente."
                )
                return existing_studio  # Retorna um Studio existente

            logger.error(f"Erro inesperado ao inserir estúdio '{name}'.")
            raise ValueError(f"Erro ao recuperar estúdio '{name}' após IntegrityError.")

    @staticmethod
    def get_by_id(db: Session, studio_id: int) -> Optional[Studio]:
        """
        Busca um estúdio pelo ID.

        :param db: Sessão do banco de dados.
        :param studio_id: ID do estúdio.
        :return: Objeto Studio se encontrado, caso contrário, None.
        """
        try:
            return db.query(Studio).filter(Studio.id == studio_id).one()
        except NoResultFound:
            logger.warning(f"Estúdio com ID {studio_id} não encontrado.")
            return None

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Studio]:
        """
        Busca um estúdio pelo nome.

        :param db: Sessão do banco de dados.
        :param name: Nome do estúdio.
        :return: Objeto Studio se encontrado, caso contrário, None.
        """
        return db.query(Studio).filter(Studio.name == name).first()

    @staticmethod
    def get_all(db: Session) -> List[Studio]:
        """
        Retorna todos os estúdios cadastrados no banco.

        :param db: Sessão do banco de dados.
        :return: Lista de objetos Studio.
        """
        return db.query(Studio).all()

    @classmethod
    def create_multiple(cls, db: Session, studio_names: List[str]) -> List[Studio]:
        """
        Busca ou cria múltiplos estúdios de uma só vez.

        :param db: Sessão do banco de dados.
        :param studio_names: Lista de nomes dos estúdios.
        :return: Lista de objetos Studio.
        """
        studios = []

        for name in set(studio_names):  # Remove duplicados da lista de entrada
            try:
                studio = cls.create(db, name)
                studios.append(studio)
            except Exception as e:
                logger.error(f"Erro ao processar estúdio '{name}': {e}")

        return studios

    @staticmethod
    def delete(db: Session, studio_id: int) -> bool:
        """
        Remove um estúdio do banco de dados.

        :param db: Sessão do banco de dados.
        :param studio_id: ID do estúdio a ser removido.
        :return: True se o estúdio foi removido, False se não foi encontrado.
        """
        studio = db.query(Studio).filter(Studio.id == studio_id).first()
        if studio:
            db.delete(studio)
            db.commit()
            logger.info(f"Estúdio '{studio.name}' removido com sucesso.")
            return True

        logger.warning(
            f"Tentativa de remover estúdio com ID {studio_id}, mas ele não existe."
        )
        return False
