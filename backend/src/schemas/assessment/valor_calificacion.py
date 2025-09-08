import uuid
from pydantic import BaseModel
from typing import Optional


class ValorCalificacionBase(BaseModel):
    valor: str
    descripcion: Optional[str] = None
    orden: Optional[int] = None


class ValorCalificacionCreate(ValorCalificacionBase):
    escala_id: uuid.UUID


class ValorCalificacionUpdate(ValorCalificacionBase):
    pass


class ValorCalificacionInDBBase(ValorCalificacionBase):
    valor_id: uuid.UUID
    escala_id: uuid.UUID

    class Config:
        from_attributes = True


class ValorCalificacion(ValorCalificacionInDBBase):
    pass


class ValorCalificacionInDB(ValorCalificacionInDBBase):
    pass