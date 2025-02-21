from functools import lru_cache
from sqlalchemy.orm import Session
from app.schemas.award_interval import AwardInterval, AwardIntervalResponse
from app.repositories.movie_repository import MovieRepository
from collections import defaultdict
from typing import List, Dict, cast
from app.db.database import get_db


class AwardIntervalService:
    """
    Serviço para calcular os produtores com maior e menor intervalo entre prêmios.
    """

    @staticmethod
    def get_producer_win_years(db: Session) -> Dict[str, List[int]]:
        """
        Obtém os anos de vitória de cada produtor.

        :param db: Sessão do banco de dados.
        :return: Dicionário onde a chave é o nome do produtor
        e o valor é a lista de anos que ele venceu.
        """
        movies = MovieRepository.get_winning_movies(db)

        producer_wins: Dict[str, List[int]] = defaultdict(list)

        for movie in movies:
            for producer in movie.producers:
                print(producer.name, movie.year)
                producer_wins[cast(str, producer.name)].append(cast(int, movie.year))

        return producer_wins

    @staticmethod
    def calculate_intervals(producer_wins: Dict[str, List[int]]) -> List[AwardInterval]:
        """
        Calcula os intervalos entre prêmios consecutivos para produtores.

        :param producer_wins: Dicionário com produtores como chave e
        lista de anos que venceram como valores.
        :return: Lista de AwardInterval contendo os intervalos entre
        prêmios consecutivos.
        """
        intervals: List[AwardInterval] = []

        # Filtrar apenas os produtores que têm mais de um prêmio
        filtered_producers = {
            producer: years
            for producer, years in producer_wins.items()
            if len(years) > 1
        }

        for producer, years in filtered_producers.items():
            intervals.extend(
                AwardInterval(
                    producer=producer,
                    interval=years[i + 1] - years[i],
                    previousWin=years[i],
                    followingWin=years[i + 1],
                )
                for i in range(len(years) - 1)
            )

        return intervals

    @staticmethod
    def get_min_interval(intervals: List[AwardInterval]) -> List[AwardInterval]:
        """
        Obtém o menor intervalo entre prêmios consecutivos.

        :param intervals: Lista de AwardInterval.
        :return: Lista de AwardInterval com os menores intervalos.
        """
        if not intervals:
            return []

        min_interval_value = min(item.interval for item in intervals)
        return [item for item in intervals if item.interval == min_interval_value]

    @staticmethod
    def get_max_interval(intervals: List[AwardInterval]) -> List[AwardInterval]:
        """
        Obtém o maior intervalo entre prêmios consecutivos.

        :param intervals: Lista de AwardInterval.
        :return: Lista de AwardInterval com os maiores intervalos.
        """
        if not intervals:
            return []

        max_interval_value = max(entry.interval for entry in intervals)
        return [entry for entry in intervals if entry.interval == max_interval_value]

    @staticmethod
    def calculate_award_intervals(db: Session) -> AwardIntervalResponse:
        """
        Calcula os intervalos de prêmios consecutivos para produtores.

        :param db: Sessão do banco de dados.
        :return: AwardIntervalResponse contendo os produtores com maior
        e menor intervalo entre prêmios.
        """
        producer_wins = AwardIntervalService.get_producer_win_years(db)
        intervals = AwardIntervalService.calculate_intervals(producer_wins)

        return AwardIntervalResponse(
            min=AwardIntervalService.get_min_interval(intervals),
            max=AwardIntervalService.get_max_interval(intervals),
        )

    @staticmethod
    @lru_cache(maxsize=1)
    def calculate_award_intervals_cached(db: Session) -> AwardIntervalResponse:
        """
        Calcula os intervalos de prêmios consecutivos e armazena o resultado em cache.
        """
        return AwardIntervalService.calculate_award_intervals(db)

    @staticmethod
    def invalidate_cache() -> None:
        """
        Invalida o cache armazenado.
        """
        AwardIntervalService.calculate_award_intervals_cached.cache_clear()
