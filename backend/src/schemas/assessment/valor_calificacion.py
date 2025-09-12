from uuid import UUID
from pydantic import BaseModel


class ValorCalificacionBase(BaseModel):
    valor: str
    descripcion: str | None = None
    orden: int | None = None


class ValorCalificacionCreate(ValorCalificacionBase):
    escala_id: UUID


class ValorCalificacionUpdate(ValorCalificacionBase):
    pass


class ValorCalificacionInDBBase(ValorCalificacionBase):
    valor_id: UUID
    escala_id: UUID

    class Config:
        from_attributes = True


class ValorCalificacion(ValorCalificacionInDBBase):
    pass


class ValorCalificacionInDB(ValorCalificacionInDBBase):
    pass
