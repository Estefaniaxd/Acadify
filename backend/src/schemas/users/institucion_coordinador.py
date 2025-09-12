from pydantic import BaseModel
import uuid
from datetime import date
from typing import Optional
from src.enums.users.coordinador_enums import EstadoCoordinador

class InstitucionCoordinadorBase(BaseModel):
    institucion_id: uuid.UUID
    coordinador_id: uuid.UUID
    fecha_asignacion: date
    estado: Optional[EstadoCoordinador] = None

class InstitucionCoordinadorCreate(InstitucionCoordinadorBase):
    pass

class InstitucionCoordinadorUpdate(BaseModel):
    fecha_asignacion: date | None = None
    estado: EstadoCoordinador | None = None

class InstitucionCoordinadorOut(InstitucionCoordinadorBase):
    institucion_coordinador_id: uuid.UUID

    class Config:
        orm_mode = True