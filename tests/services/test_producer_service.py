from sqlalchemy.orm import Session
from app.models.producer import Producer
from app.services.producer_service import ProducerService


class TestProducerService:
    """Testes unitários para a service de produtores."""

    def test_create_producer(self, db_session: Session) -> None:
        """Testa a criação de um produtor via service."""
        producer = ProducerService.create_producer(db_session, "Steven Spielberg")

        assert producer is not None
        assert producer.name == "Steven Spielberg"
        assert isinstance(producer, Producer)

    def test_get_producer_by_id(self, db_session: Session) -> None:
        """Testa a busca de um produtor pelo ID."""
        producer = ProducerService.create_producer(db_session, "Christopher Nolan")
        fetched_producer = ProducerService.get_producer_by_id(
            db_session, int(producer.id)
        )

        assert fetched_producer is not None
        assert fetched_producer.id == producer.id

    def test_get_producer_by_id_not_found(self, db_session: Session) -> None:
        """Testa a busca de um produtor por ID inexistente."""
        producer = ProducerService.get_producer_by_id(db_session, 9999)
        assert producer is None

    def test_get_producer_by_name(self, db_session: Session) -> None:
        """Testa a busca de um produtor pelo nome."""
        ProducerService.create_producer(db_session, "Martin Scorsese")
        fetched_producer = ProducerService.get_producer_by_name(
            db_session, "Martin Scorsese"
        )

        assert fetched_producer is not None
        assert fetched_producer.name == "Martin Scorsese"

    def test_get_producer_by_name_not_found(self, db_session: Session) -> None:
        """Testa a busca de um produtor por nome inexistente."""
        producer = ProducerService.get_producer_by_name(db_session, "Unknown Producer")
        assert producer is None

    def test_get_all_producers(self, db_session: Session) -> None:
        """Testa a obtenção de todos os produtores."""
        ProducerService.create_producer(db_session, "Tarantino")
        ProducerService.create_producer(db_session, "Scorsese")

        all_producers = ProducerService.get_all_producers(db_session)
        assert len(all_producers) == 2

    def test_delete_producer(self, db_session: Session) -> None:
        """Testa a remoção de um produtor pelo ID."""
        producer = ProducerService.create_producer(db_session, "George Lucas")
        assert ProducerService.delete_producer(db_session, int(producer.id)) is True

        # Tentar buscar o produtor removido
        deleted_producer = ProducerService.get_producer_by_id(
            db_session, int(producer.id)
        )
        assert deleted_producer is None

    def test_delete_producer_not_found(self, db_session: Session) -> None:
        """Testa a remoção de um produtor inexistente."""
        assert ProducerService.delete_producer(db_session, 9999) is False
