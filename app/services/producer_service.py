from sqlalchemy.orm import Session
from app.repositories.producer_repository import ProducerRepository
from app.schemas.producer import ProducerCreate, ProducerResponse, ProducerListResponse
from typing import Optional, cast


class ProducerService:
    """Camada de serviço para Producers, aplicando regras de negócio."""

    @staticmethod
    def create_producer(db: Session, producer_data: ProducerCreate) -> ProducerResponse:
        """Cria um novo produtor e retorna os dados formatados."""
        producer = ProducerRepository.create(db, producer_data.name)
        if producer is None:
            raise ValueError("Erro: Erro ao criar o Produtor.")

        return ProducerResponse(id=cast(int, producer.id), name=str(producer.name))

    @staticmethod
    def get_producer_by_id(db: Session, producer_id: int) -> Optional[ProducerResponse]:
        """Obtém um produtor pelo ID, retornando no formato correto."""
        producer = ProducerRepository.get_by_id(db, int(producer_id))
        if producer:
            return ProducerResponse(id=cast(int, producer.id), name=str(producer.name))
        return None

    @staticmethod
    def get_producer_by_name(db: Session, name: str) -> Optional[ProducerResponse]:
        """Obtém um produtor pelo nome."""
        producer = ProducerRepository.get_by_name(db, name)
        if producer:
            return ProducerResponse(id=cast(int, producer.id), name=str(producer.name))
        return None

    @staticmethod
    def get_all_producers(db: Session) -> ProducerListResponse:
        """Obtém todos os produtores cadastrados no banco."""
        producers = ProducerRepository.get_all(db)
        return ProducerListResponse(
            producers=[
                ProducerResponse(id=cast(int, p.id), name=str(p.name))
                for p in producers
            ]
        )

    @staticmethod
    def delete_producer(db: Session, producer_id: int) -> bool:
        """Deleta um produtor pelo ID."""
        return ProducerRepository.delete(db, int(producer_id))
