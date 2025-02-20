from sqlalchemy.orm import Session
from app.repositories.studio_repository import StudioRepository
from app.schemas.studio import StudioCreate, StudioResponse, StudioListResponse
from typing import Optional, cast


class StudioService:
    """Camada de serviço para Studios, aplicando regras de negócio."""

    @staticmethod
    def create_studio(db: Session, studio_data: StudioCreate) -> StudioResponse:
        """Cria um novo estúdio e retorna os dados formatados."""
        studio = StudioRepository.create(db, studio_data.name)
        if studio is None:
            raise ValueError("Erro: Erro ao criar o Estúdio.")

        return StudioResponse(id=cast(int, studio.id), name=str(studio.name))

    @staticmethod
    def get_studio_by_id(db: Session, studio_id: int) -> Optional[StudioResponse]:
        """Obtém um estúdio pelo ID, retornando no formato correto."""
        studio = StudioRepository.get_by_id(db, int(studio_id))
        if studio:
            return StudioResponse(id=cast(int, studio.id), name=str(studio.name))
        return None

    @staticmethod
    def get_studio_by_name(db: Session, name: str) -> Optional[StudioResponse]:
        """Obtém um estúdio pelo nome."""
        studio = StudioRepository.get_by_name(db, name)
        if studio:
            return StudioResponse(id=cast(int, studio.id), name=str(studio.name))
        return None

    @staticmethod
    def get_all_studios(db: Session) -> StudioListResponse:
        """Obtém todos os estúdios cadastrados no banco."""
        studios = StudioRepository.get_all(db)
        return StudioListResponse(
            studios=[
                StudioResponse(id=cast(int, s.id), name=str(s.name)) for s in studios
            ]
        )

    @staticmethod
    def delete_studio(db: Session, studio_id: int) -> bool:
        """Deleta um estúdio pelo ID."""
        return StudioRepository.delete(db, int(studio_id))
