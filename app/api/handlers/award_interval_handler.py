from fastapi import HTTPException
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

        :return: AwardIntervalResponse contendo os produtores com
        maior e menor intervalo.
        """
        try:
            return AwardIntervalService.calculate_award_intervals_cached(db)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao processar os dados: {str(e)}"
            )

    @staticmethod
    def invalidate_cache() -> dict:
        """
        Invalida manualmente o cache dos cálculos de prêmios.

        :return: Mensagem confirmando a invalidação do cache.
        """
        AwardIntervalService.invalidate_cache()
        return {"message": "Cache invalidado com sucesso"}
