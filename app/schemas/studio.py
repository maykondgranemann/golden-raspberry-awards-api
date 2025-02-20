from pydantic import BaseModel, ConfigDict


class StudioBase(BaseModel):
    """Define os campos básicos do estúdio."""

    name: str


class StudioCreate(StudioBase):
    """Schema usado para criação de um estúdio."""

    pass


class StudioResponse(StudioBase):
    """Schema de resposta ao buscar um estúdio."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class StudioListResponse(BaseModel):
    """Schema para listar múltiplos estúdios."""

    studios: list[StudioResponse]
