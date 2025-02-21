from typing import List, Dict
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from pytest_mock import MockFixture
from app.services.award_interval_service import AwardIntervalService
from app.repositories.movie_repository import MovieRepository
from app.schemas.award_interval import AwardInterval, AwardIntervalResponse


class TestAwardIntervalService:
    """Testes unitários para a AwardIntervalService."""

    def test_get_producer_win_years(
        self,
        db_session: Session,
        mock_winning_movies: List[MagicMock],
        mocker: MockFixture,
    ) -> None:
        """
        Testa se a função get_producer_win_years retorna corretamente
        um dicionário de produtores com os anos que venceram.
        """
        mocker.patch.object(
            MovieRepository, "get_winning_movies", return_value=mock_winning_movies
        )

        producer_wins: Dict[str, List[int]] = (
            AwardIntervalService.get_producer_win_years(db_session)
        )

        # Verificar se os produtores corretos foram capturados
        assert "Producer A" in producer_wins
        assert "Producer B" in producer_wins

        # Verificar os anos corretamente associados
        assert producer_wins["Producer A"] == [2000, 2005, 2010]
        assert producer_wins["Producer B"] == [2018, 2020]

    def test_calculate_intervals(self) -> None:
        """
        Testa se a função calculate_intervals calcula corretamente
        os intervalos entre prêmios consecutivos.
        """
        producer_wins = {
            "Producer A": [2000, 2005, 2010],
            "Producer B": [2018, 2020],
            "Producer C": [2015],  # Deve ser ignorado
        }

        intervals = AwardIntervalService.calculate_intervals(producer_wins)

        expected_intervals = [
            AwardInterval(
                producer="Producer A", interval=5, previousWin=2000, followingWin=2005
            ),
            AwardInterval(
                producer="Producer A", interval=5, previousWin=2005, followingWin=2010
            ),
            AwardInterval(
                producer="Producer B", interval=2, previousWin=2018, followingWin=2020
            ),
        ]

        assert intervals == expected_intervals

    def test_get_min_interval(self) -> None:
        """
        Testa se a função get_min_interval retorna corretamente
        os menores intervalos entre prêmios consecutivos.
        """
        intervals = [
            AwardInterval(
                producer="Producer A", interval=5, previousWin=2000, followingWin=2005
            ),
            AwardInterval(
                producer="Producer A", interval=5, previousWin=2005, followingWin=2010
            ),
            AwardInterval(
                producer="Producer B", interval=2, previousWin=2018, followingWin=2020
            ),
        ]

        min_intervals = AwardIntervalService.get_min_interval(intervals)

        assert len(min_intervals) == 1
        assert min_intervals[0].producer == "Producer B"
        assert min_intervals[0].interval == 2

    def test_get_max_interval(self) -> None:
        """
        Testa se a função get_max_interval retorna corretamente
        os maiores intervalos entre prêmios consecutivos.
        """
        intervals = [
            AwardInterval(
                producer="Producer A", interval=5, previousWin=2000, followingWin=2005
            ),
            AwardInterval(
                producer="Producer A", interval=5, previousWin=2005, followingWin=2010
            ),
            AwardInterval(
                producer="Producer B", interval=2, previousWin=2018, followingWin=2020
            ),
        ]

        max_intervals = AwardIntervalService.get_max_interval(intervals)

        assert len(max_intervals) == 2
        assert all(interval.producer == "Producer A" for interval in max_intervals)
        assert all(interval.interval == 5 for interval in max_intervals)

    def test_calculate_award_intervals(
        self,
        db_session: Session,
        mock_winning_movies: List[MagicMock],
        mocker: MockFixture,
    ) -> None:
        """
        Testa a função principal calculate_award_intervals, garantindo que ela retorne
        os valores corretos para min e max.
        """
        mocker.patch.object(
            MovieRepository, "get_winning_movies", return_value=mock_winning_movies
        )

        response: AwardIntervalResponse = (
            AwardIntervalService.calculate_award_intervals(db_session)
        )

        # Verifica se os valores esperados foram retornados
        assert isinstance(response, AwardIntervalResponse)
        assert len(response.min) == 1
        assert response.min[0].producer == "Producer B"
        assert response.min[0].interval == 2

        assert len(response.max) == 2
        assert all(interval.producer == "Producer A" for interval in response.max)
        assert all(interval.interval == 5 for interval in response.max)

    def test_calculate_award_intervals_cached(self, mocker: MockFixture) -> None:
        """
        Testa se a função calculate_award_intervals_cached armazena e
        reutiliza o cache corretamente.
        """
        mock_response = AwardIntervalResponse(
            min=[
                AwardInterval(
                    producer="Producer B",
                    interval=2,
                    previousWin=2018,
                    followingWin=2020,
                )
            ],
            max=[
                AwardInterval(
                    producer="Producer A",
                    interval=5,
                    previousWin=2000,
                    followingWin=2005,
                )
            ],
        )

        # Mockando a chamada para get_db() para retornar um mock de sessão
        mocker.patch(
            "app.services.award_interval_service.get_db",
            return_value=iter([MagicMock()]),
        )
        mocker.patch.object(
            AwardIntervalService,
            "calculate_award_intervals",
            return_value=mock_response,
        )

        # Primeira chamada, deve calcular e armazenar no cache
        response1 = AwardIntervalService.calculate_award_intervals_cached()
        response2 = (
            AwardIntervalService.calculate_award_intervals_cached()
        )  # Deve vir do cache

        assert response1 is response2  # Deve ser o mesmo objeto na memória
        assert response1.min[0].producer == "Producer B"
        assert response1.max[0].producer == "Producer A"

    def test_invalidate_cache(self, mocker: MockFixture) -> None:
        """
        Testa se a função invalidate_cache limpa corretamente o cache de
        calculate_award_intervals_cached.
        """
        mock_response = AwardIntervalResponse(
            min=[
                AwardInterval(
                    producer="Producer B",
                    interval=2,
                    previousWin=2018,
                    followingWin=2020,
                )
            ],
            max=[
                AwardInterval(
                    producer="Producer A",
                    interval=5,
                    previousWin=2000,
                    followingWin=2005,
                )
            ],
        )

        # Corrigindo o mock de get_db() para gerar um novo iterador sempre que chamado
        mocker.patch(
            "app.services.award_interval_service.get_db", lambda: iter([MagicMock()])
        )
        mocker.patch.object(
            AwardIntervalService,
            "calculate_award_intervals",
            return_value=mock_response,
        )

        # Reset cache para não ter interferência de outros testes
        AwardIntervalService.invalidate_cache()

        # Primeira chamada deve armazenar no cache
        AwardIntervalService.calculate_award_intervals_cached()
        assert (
            AwardIntervalService.calculate_award_intervals_cached.cache_info().hits == 0
        )

        # Chamada subsequente usa cache
        AwardIntervalService.calculate_award_intervals_cached()
        assert (
            AwardIntervalService.calculate_award_intervals_cached.cache_info().hits == 1
        )

        # Limpa o cache para testar uso novamente
        AwardIntervalService.invalidate_cache()

        # Nova chamada deve recalcular e não usar o cache
        AwardIntervalService.calculate_award_intervals_cached()
        assert (
            AwardIntervalService.calculate_award_intervals_cached.cache_info().hits == 0
        )
