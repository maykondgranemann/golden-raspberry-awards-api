from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.studio import StudioCreate, StudioResponse, StudioListResponse
from app.api.handlers.studio_handler import StudioHandler

router = APIRouter(prefix="/studios", tags=["Studios"])


@router.post("/", response_model=StudioResponse, status_code=201)
def create_studio(
    studio_data: StudioCreate, db: Session = Depends(get_db)
) -> StudioResponse:
    """Cria um novo estúdio."""
    return StudioHandler.create_studio(db, studio_data)


@router.get("/{studio_id}", response_model=StudioResponse)
def get_studio_by_id(studio_id: int, db: Session = Depends(get_db)) -> StudioResponse:
    """Obtém um estúdio pelo ID."""
    return StudioHandler.get_studio_by_id(db, studio_id)


@router.get("/name/{name}", response_model=StudioResponse)
def get_studio_by_name(name: str, db: Session = Depends(get_db)) -> StudioResponse:
    """Obtém um estúdio pelo nome."""
    return StudioHandler.get_studio_by_name(db, name)


@router.get("/", response_model=StudioListResponse)
def get_all_studios(db: Session = Depends(get_db)) -> StudioListResponse:
    """Obtém todos os estúdios cadastrados."""
    return StudioHandler.get_all_studios(db)


@router.delete("/{studio_id}", status_code=204)
def delete_studio(studio_id: int, db: Session = Depends(get_db)) -> None:
    """Deleta um estúdio pelo ID."""
    return StudioHandler.delete_studio(db, studio_id)
