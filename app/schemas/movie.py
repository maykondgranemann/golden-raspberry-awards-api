from pydantic import BaseModel, ConfigDict
from typing import List


class MovieBase(BaseModel):
    """Schema base para filmes."""

    title: str
    year: int


class MovieCreate(MovieBase):
    """Schema para criação de filmes."""

    pass


class MovieResponse(MovieBase):
    """Schema de resposta para filmes."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class MovieListResponse(BaseModel):
    """Schema para resposta de lista de filmes."""

    movies: List[MovieResponse]
