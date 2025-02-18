from sqlalchemy.orm import Session
from app.services.producer_service import ProducerService
from app.schemas.producer import ProducerCreate, ProducerResponse
from typing import Optional


class TestProducerService:
    """Testes unitários para a service de produtores."""

    def test_create_producer(self, db_session: Session) -> None:
        """Testa a criação de um produtor via service."""
        producer_data = ProducerCreate(name="Steven Spielberg")
        producer: ProducerResponse = ProducerService.create_producer(
            db_session, producer_data
        )

        assert isinstance(producer, ProducerResponse)
        assert producer.name == "Steven Spielberg"
        assert isinstance(producer.id, int)

    def test_get_producer_by_id(self, db_session: Session) -> None:
        """Testa a busca de um produtor pelo ID."""
        producer_data = ProducerCreate(name="Christopher Nolan")
        producer: ProducerResponse = ProducerService.create_producer(
            db_session, producer_data
        )

        fetched_producer: Optional[
            ProducerResponse
        ] = ProducerService.get_producer_by_id(db_session, int(producer.id))

        assert fetched_producer is not None
        assert fetched_producer.id == producer.id
        assert fetched_producer.name == producer.name

    def test_get_producer_by_id_not_found(self, db_session: Session) -> None:
        """Testa a busca de um produtor por um ID inexistente."""
        producer: Optional[ProducerResponse] = ProducerService.get_producer_by_id(
            db_session, 9999
        )
        assert producer is None

    def test_get_producer_by_name(self, db_session: Session) -> None:
        """Testa a busca de um produtor pelo nome."""
        producer_data = ProducerCreate(name="Martin Scorsese")
        ProducerService.create_producer(db_session, producer_data)

        fetched_producer: Optional[
            ProducerResponse
        ] = ProducerService.get_producer_by_name(db_session, "Martin Scorsese")

        assert fetched_producer is not None
        assert fetched_producer.name == "Martin Scorsese"

    def test_get_producer_by_name_not_found(self, db_session: Session) -> None:
        """Testa a busca de um produtor por um nome inexistente."""
        producer: Optional[ProducerResponse] = ProducerService.get_producer_by_name(
            db_session, "Unknown Producer"
        )
        assert producer is None

    def test_get_all_producers(self, db_session: Session) -> None:
        """Testa a obtenção de todos os produtores cadastrados."""
        ProducerService.create_producer(db_session, ProducerCreate(name="Tarantino"))
        ProducerService.create_producer(db_session, ProducerCreate(name="Scorsese"))

        all_producers = ProducerService.get_all_producers(db_session)

        assert len(all_producers.producers) == 2
        assert all(isinstance(p, ProducerResponse) for p in all_producers.producers)

    def test_delete_producer(self, db_session: Session) -> None:
        """Testa a remoção de um produtor pelo ID."""
        producer_data = ProducerCreate(name="George Lucas")
        producer: ProducerResponse = ProducerService.create_producer(
            db_session, producer_data
        )

        assert ProducerService.delete_producer(db_session, int(producer.id)) is True

        # Tentar buscar o produtor removido
        deleted_producer = ProducerService.get_producer_by_id(
            db_session, int(producer.id)
        )
        assert deleted_producer is None

    def test_delete_producer_not_found(self, db_session: Session) -> None:
        """Testa a remoção de um produtor inexistente."""
        assert ProducerService.delete_producer(db_session, 9999) is False
