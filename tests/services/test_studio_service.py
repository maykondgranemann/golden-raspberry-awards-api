from sqlalchemy.orm import Session
from app.services.studio_service import StudioService
from app.schemas.studio import StudioCreate, StudioResponse
from typing import Optional


class TestStudioService:
    """Testes unitários para a service de estúdios."""

    def test_create_studio(self, db_session: Session) -> None:
        """Testa a criação de um estúdio via service."""
        studio_data = StudioCreate(name="Warner Bros.")
        studio: StudioResponse = StudioService.create_studio(db_session, studio_data)

        assert isinstance(studio, StudioResponse)
        assert studio.name == "Warner Bros."
        assert isinstance(studio.id, int)

    def test_get_studio_by_id(self, db_session: Session) -> None:
        """Testa a busca de um estúdio pelo ID."""
        studio_data = StudioCreate(name="Universal Pictures")
        studio: StudioResponse = StudioService.create_studio(db_session, studio_data)

        fetched_studio: Optional[StudioResponse] = StudioService.get_studio_by_id(
            db_session, int(studio.id)
        )

        assert fetched_studio is not None
        assert fetched_studio.id == studio.id
        assert fetched_studio.name == studio.name

    def test_get_studio_by_id_not_found(self, db_session: Session) -> None:
        """Testa a busca de um estúdio por um ID inexistente."""
        studio: Optional[StudioResponse] = StudioService.get_studio_by_id(
            db_session, 9999
        )
        assert studio is None

    def test_get_studio_by_name(self, db_session: Session) -> None:
        """Testa a busca de um estúdio pelo nome."""
        studio_data = StudioCreate(name="Paramount Pictures")
        StudioService.create_studio(db_session, studio_data)

        fetched_studio: Optional[StudioResponse] = StudioService.get_studio_by_name(
            db_session, "Paramount Pictures"
        )

        assert fetched_studio is not None
        assert fetched_studio.name == "Paramount Pictures"

    def test_get_studio_by_name_not_found(self, db_session: Session) -> None:
        """Testa a busca de um estúdio por um nome inexistente."""
        studio: Optional[StudioResponse] = StudioService.get_studio_by_name(
            db_session, "Unknown Studio"
        )
        assert studio is None

    def test_get_all_studios(self, db_session: Session) -> None:
        """Testa a obtenção de todos os estúdios cadastrados."""
        StudioService.create_studio(db_session, StudioCreate(name="Disney"))
        StudioService.create_studio(db_session, StudioCreate(name="20th Century Fox"))

        all_studios = StudioService.get_all_studios(db_session)

        assert len(all_studios.studios) == 2
        assert all(isinstance(s, StudioResponse) for s in all_studios.studios)

    def test_delete_studio(self, db_session: Session) -> None:
        """Testa a remoção de um estúdio pelo ID."""
        studio_data = StudioCreate(name="Columbia Pictures")
        studio: StudioResponse = StudioService.create_studio(db_session, studio_data)

        assert StudioService.delete_studio(db_session, int(studio.id)) is True

        # Tentar buscar o estúdio removido
        deleted_studio = StudioService.get_studio_by_id(db_session, int(studio.id))
        assert deleted_studio is None

    def test_delete_studio_not_found(self, db_session: Session) -> None:
        """Testa a remoção de um estúdio inexistente."""
        assert StudioService.delete_studio(db_session, 9999) is False
