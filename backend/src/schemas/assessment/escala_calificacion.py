import uuid
from pydantic import BaseModel
from typing import Optional
from src.enums.assessment.escala_calificacion_eunms import TipoEscalafonEnum

class EscalaCalificacionBase(BaseModel):
    nombre: str
    tipo: TipoEscalafonEnum
    min_valor: Optional[float] = None
    max_valor: Optional[float] = None

class EscalaCalificacionCreate(EscalaCalificacionBase):
    institucion_id: uuid.UUID

class EscalaCalificacionUpdate(EscalaCalificacionBase):
    pass

class EscalaCalificacionInDBBase(EscalaCalificacionBase):
    escala_id: uuid.UUID
    institucion_id: uuid.UUID

    class Config:
        from_attributes = True

class EscalaCalificacion(EscalaCalificacionInDBBase):
    pass

class EscalaCalificacionInDB(EscalaCalificacionInDBBase):
    pass