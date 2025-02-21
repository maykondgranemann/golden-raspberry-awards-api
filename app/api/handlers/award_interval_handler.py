from sqlalchemy.orm import Session
from app.services.award_interval_service import AwardIntervalService
from app.schemas.award_interval import AwardIntervalResponse


class AwardIntervalHandler:
    """
    Handler para processar a lógica de obtenção dos
    intervalos de prêmios dos produtores.
    """

    @staticmethod
    def get_award_intervals(db: Session) -> AwardIntervalResponse:
        """
        Obtém os produtores com maior e menor intervalo entre prêmios consecutivos.

        :param db: Sessão do banco de dados.
        :return: AwardIntervalResponse contendo os
        produtores com maior e menor intervalo.
        """
        return AwardIntervalService.calculate_award_intervals(db)
