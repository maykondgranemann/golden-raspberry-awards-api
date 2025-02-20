from sqlalchemy.orm import Session
from app.models.studio import Studio


class TestStudioModel:
    """Testes para a model Studio."""

    def test_create_studio(self, db_session: Session) -> None:
        """Testa a criação de um novo estúdio no banco de dados."""
        studio = Studio(name="Warner Bros")
        db_session.add(studio)
        db_session.commit()

        fetched_studio = db_session.query(Studio).filter_by(name="Warner Bros").first()
        assert fetched_studio is not None
        assert fetched_studio.name == "Warner Bros"

    def test_create_duplicate_studio(self, db_session: Session) -> None:
        """Testa a tentativa de criação de um estúdio duplicado."""
        studio1 = Studio(name="Universal Pictures")
        db_session.add(studio1)
        db_session.commit()

        studio2 = Studio(name="Universal Pictures")
        db_session.add(studio2)
        try:
            db_session.commit()
            assert False, "Deve ser lançado uma exceção de unicidade"
        except Exception:
            db_session.rollback()

    def test_get_studio_by_id(self, db_session: Session) -> None:
        """Testa a recuperação de um estúdio pelo ID."""
        studio = Studio(name="Paramount Pictures")
        db_session.add(studio)
        db_session.commit()

        fetched_studio = db_session.get(Studio, studio.id)
        assert fetched_studio is not None
        assert fetched_studio.id == studio.id
        assert fetched_studio.name == "Paramount Pictures"

    def test_get_studio_not_found(self, db_session: Session) -> None:
        """Testa a recuperação de um estúdio inexistente."""
        studio = db_session.get(Studio, 9999)  # ID que não existe
        assert studio is None

    def test_delete_studio(self, db_session: Session) -> None:
        """Testa a remoção de um estúdio."""
        studio = Studio(name="Sony Pictures")
        db_session.add(studio)
        db_session.commit()

        db_session.delete(studio)
        db_session.commit()

        deleted_studio = db_session.get(Studio, studio.id)
        assert deleted_studio is None
