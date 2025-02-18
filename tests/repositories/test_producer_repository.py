from sqlalchemy.orm import Session
from app.models.producer import Producer
from app.repositories.producer_repository import ProducerRepository


class TestProducerRepository:
    """
    Testes unitários para a repository de produtores.
    """

    def test_create_producer(self, db_session: Session) -> None:
        """
        Testa a criação de um novo produtor.
        """
        producer = ProducerRepository.create(db_session, "Steven Spielberg")

        assert producer is not None
        assert producer.name == "Steven Spielberg"
        assert isinstance(producer, Producer)

    def test_create_existing_producer(self, db_session: Session) -> None:
        """
        Testa a criação de um produtor que já existe no banco de dados.
        """
        first_producer = ProducerRepository.create(db_session, "Quentin Tarantino")
        # Deve retornar o mesmo
        second_producer = ProducerRepository.create(db_session, "Quentin Tarantino")

        assert first_producer.id == second_producer.id  # Deve ser o mesmo objeto
        assert first_producer.name == "Quentin Tarantino"

    def test_get_by_id(self, db_session: Session) -> None:
        """
        Testa a busca de um produtor pelo ID.
        """
        producer = ProducerRepository.create(db_session, "Christopher Nolan")
        fetched_producer = ProducerRepository.get_by_id(db_session, int(producer.id))

        assert fetched_producer is not None
        assert fetched_producer.id == producer.id
        assert fetched_producer.name == "Christopher Nolan"

    def test_get_by_id_not_found(self, db_session: Session) -> None:
        """
        Testa a busca de um produtor por ID inexistente.
        """
        producer = ProducerRepository.get_by_id(db_session, 9999)  # ID que não existe
        assert producer is None

    def test_get_by_name(self, db_session: Session) -> None:
        """
        Testa a busca de um produtor pelo nome.
        """
        ProducerRepository.create(db_session, "Martin Scorsese")
        fetched_producer = ProducerRepository.get_by_name(db_session, "Martin Scorsese")

        assert fetched_producer is not None
        assert fetched_producer.name == "Martin Scorsese"

    def test_get_by_name_not_found(self, db_session: Session) -> None:
        """
        Testa a busca de um produtor por nome inexistente.
        """
        producer = ProducerRepository.get_by_name(db_session, "Unknown Producer")
        assert producer is None

    def test_create_multiple(
        self, db_session: Session, sample_producers: list[str]
    ) -> None:
        """
        Testa a criação de múltiplos produtores.
        """
        producers = ProducerRepository.create_multiple(db_session, sample_producers)

        assert len(producers) == len(sample_producers)
        assert all(isinstance(p, Producer) for p in producers)

        # Testando se a segunda chamada não cria duplicatas
        producers_again = ProducerRepository.create_multiple(
            db_session, sample_producers
        )

        assert len(producers_again) == len(producers)
        assert all(p.id in [p.id for p in producers] for p in producers_again)

    def test_get_all(self, db_session: Session, sample_producers: list[str]) -> None:
        """
        Testa a obtenção de todos os produtores cadastrados.
        """
        for name in sample_producers:
            ProducerRepository.create(db_session, name)

        all_producers = ProducerRepository.get_all(db_session)

        assert len(all_producers) == len(sample_producers)
        assert all(isinstance(p, Producer) for p in all_producers)

    def test_delete_producer(self, db_session: Session) -> None:
        """
        Testa a remoção de um produtor pelo ID.
        """
        producer = ProducerRepository.create(db_session, "George Lucas")
        assert ProducerRepository.delete(db_session, int(producer.id)) is True

        # Tentar buscar o produtor removido
        deleted_producer = ProducerRepository.get_by_id(db_session, int(producer.id))
        assert deleted_producer is None

    def test_delete_producer_not_found(self, db_session: Session) -> None:
        """
        Testa a remoção de um produtor inexistente.
        """
        assert ProducerRepository.delete(db_session, 9999) is False
