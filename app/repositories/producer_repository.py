from sqlalchemy.orm import Session
from app.models.producer import Producer
from typing import List, Optional
from sqlalchemy.exc import IntegrityError, NoResultFound
from loguru import logger


class ProducerRepository:
    """
    Repository responsável por operações no banco de dados relacionadas aos produtores.
    """

    @staticmethod
    def create(db: Session, name: str) -> Producer:
        """
        Cria um novo produtor no banco de dados.

        :param db: Sessão do banco de dados.
        :param name: Nome do produtor.
        :return: Objeto Producer.
        """
        producer = Producer(name=name)
        db.add(producer)
        try:
            db.commit()
            db.refresh(producer)
            logger.info(f"Novo produtor cadastrado: {name}")
            return producer  # Sempre retorna um Producer válido
        except IntegrityError:
            db.rollback()
            existing_producer = db.query(Producer).filter(Producer.name == name).first()
            if existing_producer is not None:
                logger.warning(
                    f"Produtor '{name}' já existe, retornando instância existente."
                )
                return existing_producer  # Retorna um Producer existente

            logger.error(f"Erro inesperado ao inserir produtor '{name}'.")
            raise ValueError(
                f"Erro ao recuperar produtor '{name}' após IntegrityError."
            )

    @staticmethod
    def get_by_id(db: Session, producer_id: int) -> Optional[Producer]:
        """
        Busca um produtor pelo ID.

        :param db: Sessão do banco de dados.
        :param producer_id: ID do produtor.
        :return: Objeto Producer se encontrado, caso contrário, None.
        """
        try:
            return db.query(Producer).filter(Producer.id == producer_id).one()
        except NoResultFound:
            logger.warning(f"Produtor com ID {producer_id} não encontrado.")
            return None

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Producer]:
        """
        Busca um produtor pelo nome.

        :param db: Sessão do banco de dados.
        :param name: Nome do produtor.
        :return: Objeto Producer se encontrado, caso contrário, None.
        """
        return db.query(Producer).filter(Producer.name == name).first()

    @staticmethod
    def get_all(db: Session) -> List[Producer]:
        """
        Retorna todos os produtores cadastrados no banco.

        :param db: Sessão do banco de dados.
        :return: Lista de objetos Producer.
        """
        return db.query(Producer).all()

    @classmethod
    def create_multiple(cls, db: Session, producer_names: List[str]) -> List[Producer]:
        """
        Busca ou cria múltiplos produtores de uma só vez.

        :param db: Sessão do banco de dados.
        :param producer_names: Lista de nomes dos produtores.
        :return: Lista de objetos Producer.
        """
        producers = []

        for name in set(producer_names):  # Remove duplicados da lista de entrada
            try:
                producer = cls.create(db, name)
                producers.append(producer)
            except Exception as e:
                logger.error(f"Erro ao processar produtor '{name}': {e}")

        return producers

    @staticmethod
    def delete(db: Session, producer_id: int) -> bool:
        """
        Remove um produtor do banco de dados.

        :param db: Sessão do banco de dados.
        :param producer_id: ID do produtor a ser removido.
        :return: True se o produtor foi removido, False se não foi encontrado.
        """
        producer = db.query(Producer).filter(Producer.id == producer_id).first()
        if producer:
            db.delete(producer)
            db.commit()
            logger.info(f"Produtor '{producer.name}' removido com sucesso.")
            return True

        logger.warning(
            f"Tentativa de remover produtor com ID {producer_id}, mas ele não existe."
        )
        return False
