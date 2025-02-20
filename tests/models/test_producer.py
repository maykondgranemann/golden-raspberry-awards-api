import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.producer import Producer


class TestProducerModel:
    """Testes para o modelo Producer"""

    def test_create_producer(self, db_session: Session) -> None:
        """Testa a criação de um novo produtor"""
        producer = Producer(name="Steven Spielberg")
        db_session.add(producer)
        db_session.commit()
        db_session.refresh(producer)

        assert producer.id is not None
        assert producer.name == "Steven Spielberg"

    def test_create_duplicate_producer(self, db_session: Session) -> None:
        """Testa a tentativa de criar um produtor duplicado"""
        producer1 = Producer(name="Christopher Nolan")
        db_session.add(producer1)
        db_session.commit()

        producer2 = Producer(name="Christopher Nolan")
        db_session.add(producer2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_get_producer_by_id(self, db_session: Session) -> None:
        """Testa a busca de um produtor pelo ID"""
        producer = Producer(name="Quentin Tarantino")
        db_session.add(producer)
        db_session.commit()
        db_session.refresh(producer)

        fetched_producer = db_session.get(Producer, producer.id)
        assert fetched_producer is not None
        assert fetched_producer.id == producer.id
        assert fetched_producer.name == "Quentin Tarantino"

    def test_get_producer_by_id_not_found(self, db_session: Session) -> None:
        """Testa a busca por ID inexistente"""
        producer = db_session.get(Producer, 9999)
        assert producer is None

    def test_get_producer_by_name(self, db_session: Session) -> None:
        """Testa a busca de um produtor pelo nome"""
        producer = Producer(name="Martin Scorsese")
        db_session.add(producer)
        db_session.commit()
        db_session.refresh(producer)

        fetched_producer = (
            db_session.query(Producer).filter_by(name="Martin Scorsese").first()
        )
        assert fetched_producer is not None
        assert fetched_producer.name == "Martin Scorsese"

    def test_get_producer_by_name_not_found(self, db_session: Session) -> None:
        """Testa a busca por nome inexistente"""
        fetched_producer = (
            db_session.query(Producer).filter_by(name="Unknown Producer").first()
        )
        assert fetched_producer is None

    def test_get_all_producers(self, db_session: Session) -> None:
        """Testa a listagem de todos os produtores"""
        db_session.add_all(
            [
                Producer(name="John Doe"),
                Producer(name="Jane Doe"),
                Producer(name="Alice Smith"),
            ]
        )
        db_session.commit()

        producers = db_session.query(Producer).all()
        assert len(producers) == 3
        assert {p.name for p in producers} == {"John Doe", "Jane Doe", "Alice Smith"}

    def test_delete_producer(self, db_session: Session) -> None:
        """Testa a remoção de um produtor"""
        producer = Producer(name="Ridley Scott")
        db_session.add(producer)
        db_session.commit()
        db_session.refresh(producer)

        db_session.delete(producer)
        db_session.commit()

        deleted_producer = db_session.get(Producer, producer.id)
        assert deleted_producer is None
