from pydantic import BaseModel
from typing import List


class AwardInterval(BaseModel):
    """Representa um intervalo entre prêmios consecutivos de um produtor."""

    producer: str
    interval: int
    previousWin: int
    followingWin: int


class AwardIntervalResponse(BaseModel):
    """Resposta contendo os produtores com maior e menor intervalo entre prêmios."""

    min: List[AwardInterval]
    max: List[AwardInterval]
