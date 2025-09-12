from uuid import UUID
from pydantic import BaseModel
from src.enums.assessment.escala_calificacion_eunms import TipoEscalafonEnum


class EscalaCalificacionBase(BaseModel):
    nombre: str
    tipo: TipoEscalafonEnum
    min_valor: float | None = None
    max_valor: float | None = None


class EscalaCalificacionCreate(EscalaCalificacionBase):
    institucion_id: UUID


class EscalaCalificacionUpdate(EscalaCalificacionBase):
    pass


class EscalaCalificacionInDBBase(EscalaCalificacionBase):
    escala_id: UUID
    institucion_id: UUID

    class Config:
        from_attributes = True


class EscalaCalificacion(EscalaCalificacionInDBBase):
    pass


class EscalaCalificacionInDB(EscalaCalificacionInDBBase):
    pass
