from pydantic import BaseModel
from typing import List


class CSVImportRequest(BaseModel):
    """Schema para representar um filme importado do CSV."""

    title: str
    year: int
    winner: bool
    producers: List[str]
    studios: List[str]


class CSVImportResponse(BaseModel):
    """Schema para representar a resposta da importação do CSV."""

    message: str
    imported_movies: int
    ignored_movies: int
