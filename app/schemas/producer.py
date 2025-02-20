from pydantic import BaseModel, ConfigDict


class ProducerBase(BaseModel):
    """Define os campos básicos do produtor."""

    name: str


class ProducerCreate(ProducerBase):
    """Schema usado para criação de um produtor."""

    pass


class ProducerResponse(ProducerBase):
    """Schema de resposta ao buscar um produtor."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class ProducerListResponse(BaseModel):
    """Schema para listar múltiplos produtores."""

    producers: list[ProducerResponse]
