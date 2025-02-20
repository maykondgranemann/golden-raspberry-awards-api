from sqlalchemy.orm import Session
from app.schemas.producer import ProducerCreate, ProducerResponse, ProducerListResponse
from app.services.producer_service import ProducerService
from fastapi import HTTPException


class ProducerHandler:
    """Camada intermediária para validar e processar requisições da
    API antes de chamar a service."""

    @staticmethod
    def create_producer(db: Session, producer_data: ProducerCreate) -> ProducerResponse:
        """Cria um novo produtor, validando os dados antes de chamar a service."""
        if not producer_data.name.strip():
            raise HTTPException(status_code=400, detail="Producer name cannot be empty")

        return ProducerService.create_producer(db, producer_data)

    @staticmethod
    def get_producer_by_id(db: Session, producer_id: int) -> ProducerResponse:
        """Obtém um produtor pelo ID, garantindo que ele exista antes de retornar."""
        producer = ProducerService.get_producer_by_id(db, producer_id)
        if not producer:
            raise HTTPException(status_code=404, detail="Producer not found")
        return producer

    @staticmethod
    def get_producer_by_name(db: Session, name: str) -> ProducerResponse:
        """Obtém um produtor pelo nome, garantindo que ele exista antes de retornar."""
        producer = ProducerService.get_producer_by_name(db, name)
        if not producer:
            raise HTTPException(status_code=404, detail="Producer not found")
        return producer

    @staticmethod
    def get_all_producers(db: Session) -> ProducerListResponse:
        """Obtém todos os produtores cadastrados."""
        return ProducerService.get_all_producers(db)

    @staticmethod
    def delete_producer(db: Session, producer_id: int) -> None:
        """Deleta um produtor pelo ID, retornando erro se não existir."""
        deleted = ProducerService.delete_producer(db, producer_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Producer not found")
