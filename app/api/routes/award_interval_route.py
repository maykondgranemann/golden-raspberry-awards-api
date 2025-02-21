from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.handlers import AwardIntervalHandler
from app.schemas.award_interval import AwardIntervalResponse

router = APIRouter(prefix="/awards", tags=["Awards"])


@router.get("/intervals", response_model=AwardIntervalResponse)
def get_award_intervals(db: Session = Depends(get_db)) -> AwardIntervalResponse:
    """
    Endpoint para obter os produtores com maior e
    menor intervalo entre prêmios consecutivos.

    :param db: Sessão do banco de dados (injeção de dependência).
    :return: AwardIntervalResponse contendo os produtores com maior e menor intervalo.
    """
    return AwardIntervalHandler.get_award_intervals(db)


@router.post("/invalidate-cache")
def invalidate_award_cache() -> dict:
    """
    Endpoint para invalidar manualmente o cache dos cálculos de prêmios.
    """
    return AwardIntervalHandler.invalidate_cache()
