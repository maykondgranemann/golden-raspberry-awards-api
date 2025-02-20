from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional

from app.schemas.producer import ProducerResponse
from app.schemas.studio import StudioResponse


class MovieBase(BaseModel):
    """Schema base para filmes."""

    title: str
    year: int
    winner: bool


class MovieCreate(MovieBase):
    """Schema para criação de filmes."""

    pass


class MovieResponse(MovieBase):
    """Schema de resposta para filmes."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class MovieDetailedResponse(MovieResponse):
    """Schema de resposta detalhado para filmes, incluindo produtores e estúdios."""

    producers: Optional[List[ProducerResponse]] = None
    studios: Optional[List[StudioResponse]] = None


class MovieListResponse(BaseModel):
    movies: List[MovieDetailedResponse]
