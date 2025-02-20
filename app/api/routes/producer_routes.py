from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.producer import ProducerCreate, ProducerResponse, ProducerListResponse
from app.api.handlers.producer_handler import ProducerHandler

router = APIRouter(prefix="/producers", tags=["Producers"])


@router.post("/", response_model=ProducerResponse, status_code=201)
def create_producer(
    producer_data: ProducerCreate, db: Session = Depends(get_db)
) -> ProducerResponse:
    """Cria um novo produtor."""
    return ProducerHandler.create_producer(db, producer_data)


@router.get("/{producer_id}", response_model=ProducerResponse)
def get_producer_by_id(
    producer_id: int, db: Session = Depends(get_db)
) -> ProducerResponse:
    """Obtém um produtor pelo ID."""
    return ProducerHandler.get_producer_by_id(db, producer_id)


@router.get("/name/{name}", response_model=ProducerResponse)
def get_producer_by_name(name: str, db: Session = Depends(get_db)) -> ProducerResponse:
    """Obtém um produtor pelo nome."""
    return ProducerHandler.get_producer_by_name(db, name)


@router.get("/", response_model=ProducerListResponse)
def get_all_producers(db: Session = Depends(get_db)) -> ProducerListResponse:
    """Obtém todos os produtores cadastrados."""
    return ProducerHandler.get_all_producers(db)


@router.delete("/{producer_id}", status_code=204)
def delete_producer(producer_id: int, db: Session = Depends(get_db)) -> None:
    """Deleta um produtor pelo ID."""
    return ProducerHandler.delete_producer(db, producer_id)
