from sqlalchemy.orm import Session
from app.models.studio import Studio
from app.repositories.studio_repository import StudioRepository
from typing import List, cast


class TestStudioRepository:
    """Testes unitários para a repository de estúdios."""

    def test_create_studio(self, db_session: Session) -> None:
        """Testa a criação de um novo estúdio."""
        studio = StudioRepository.create(db_session, "Warner Bros")

        assert studio is not None
        assert studio.name == "Warner Bros"
        assert isinstance(studio, Studio)

    def test_create_existing_studio(self, db_session: Session) -> None:
        """Testa a criação de um estúdio que já existe no banco de dados."""
        first_studio = StudioRepository.create(db_session, "Universal Pictures")
        assert first_studio is not None

        # Deve retornar o mesmo estúdio
        second_studio = StudioRepository.create(db_session, "Universal Pictures")
        assert second_studio is not None

        assert first_studio.id == second_studio.id
        assert first_studio.name == "Universal Pictures"

    def test_get_by_id(self, db_session: Session) -> None:
        """Testa a busca de um estúdio pelo ID."""
        studio = StudioRepository.create(db_session, "Paramount Pictures")
        assert studio is not None

        fetched_studio = StudioRepository.get_by_id(db_session, cast(int, studio.id))
        assert fetched_studio is not None
        assert fetched_studio.id == studio.id
        assert fetched_studio.name == "Paramount Pictures"

    def test_get_by_id_not_found(self, db_session: Session) -> None:
        """Testa a busca de um estúdio por ID inexistente."""
        studio = StudioRepository.get_by_id(db_session, 9999)
        assert studio is None

    def test_get_by_name(self, db_session: Session) -> None:
        """Testa a busca de um estúdio pelo nome."""
        StudioRepository.create(db_session, "Sony Pictures")
        fetched_studio = StudioRepository.get_by_name(db_session, "Sony Pictures")

        assert fetched_studio is not None
        assert fetched_studio.name == "Sony Pictures"

    def test_get_by_name_not_found(self, db_session: Session) -> None:
        """Testa a busca de um estúdio por nome inexistente."""
        studio = StudioRepository.get_by_name(db_session, "Unknown Studio")
        assert studio is None

    def test_get_all(self, db_session: Session) -> None:
        """Testa a obtenção de todos os estúdios cadastrados."""
        StudioRepository.create(db_session, "Pixar")
        StudioRepository.create(db_session, "20th Century Fox")

        all_studios: List[Studio] = StudioRepository.get_all(db_session)

        assert len(all_studios) == 2
        assert all(isinstance(s, Studio) for s in all_studios)

    def test_delete_studio(self, db_session: Session) -> None:
        """Testa a remoção de um estúdio pelo ID."""
        studio = StudioRepository.create(db_session, "DreamWorks")
        assert studio is not None

        assert StudioRepository.delete(db_session, cast(int, studio.id)) is True

        # Tentar buscar o estúdio removido
        deleted_studio = StudioRepository.get_by_id(db_session, cast(int, studio.id))
        assert deleted_studio is None

    def test_delete_studio_not_found(self, db_session: Session) -> None:
        """Testa a remoção de um estúdio inexistente."""
        assert StudioRepository.delete(db_session, 9999) is False
