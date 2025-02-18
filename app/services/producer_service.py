from sqlalchemy.orm import Session
from app.models.producer import Producer
from app.repositories.producer_repository import ProducerRepository
from typing import List, Optional


class ProducerService:
    """Camada de serviço para Producers, aplicando regras de negócio."""

    @staticmethod
    def create_producer(db: Session, name: str) -> Producer:
        """Cria um novo produtor (ou retorna existente)."""
        return ProducerRepository.create(db, name)

    @staticmethod
    def get_producer_by_id(db: Session, producer_id: int) -> Optional[Producer]:
        """Obtém um produtor pelo ID."""
        return ProducerRepository.get_by_id(db, producer_id)

    @staticmethod
    def get_producer_by_name(db: Session, name: str) -> Optional[Producer]:
        """Obtém um produtor pelo nome."""
        return ProducerRepository.get_by_name(db, name)

    @staticmethod
    def get_all_producers(db: Session) -> List[Producer]:
        """Obtém todos os produtores cadastrados."""
        return ProducerRepository.get_all(db)

    @staticmethod
    def delete_producer(db: Session, producer_id: int) -> bool:
        """Deleta um produtor pelo ID."""
        return ProducerRepository.delete(db, producer_id)
