from sqlalchemy.orm import Session
from app.schemas.studio import StudioCreate, StudioResponse, StudioListResponse
from app.services.studio_service import StudioService
from fastapi import HTTPException


class StudioHandler:
    """Camada intermediária para validar e processar requisições da API
    antes de chamar a service."""

    @staticmethod
    def create_studio(db: Session, studio_data: StudioCreate) -> StudioResponse:
        """Cria um novo estúdio, validando os dados antes de chamar a service."""
        if not studio_data.name.strip():
            raise HTTPException(status_code=400, detail="Studio name cannot be empty")

        return StudioService.create_studio(db, studio_data)

    @staticmethod
    def get_studio_by_id(db: Session, studio_id: int) -> StudioResponse:
        """Obtém um estúdio pelo ID, garantindo que ele exista antes de retornar."""
        studio = StudioService.get_studio_by_id(db, studio_id)
        if not studio:
            raise HTTPException(status_code=404, detail="Studio not found")
        return studio

    @staticmethod
    def get_studio_by_name(db: Session, name: str) -> StudioResponse:
        """Obtém um estúdio pelo nome, garantindo que ele exista antes de retornar."""
        studio = StudioService.get_studio_by_name(db, name)
        if not studio:
            raise HTTPException(status_code=404, detail="Studio not found")
        return studio

    @staticmethod
    def get_all_studios(db: Session) -> StudioListResponse:
        """Obtém todos os estúdios cadastrados."""
        return StudioService.get_all_studios(db)

    @staticmethod
    def delete_studio(db: Session, studio_id: int) -> None:
        """Deleta um estúdio pelo ID, retornando erro se não existir."""
        deleted = StudioService.delete_studio(db, studio_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Studio not found")
