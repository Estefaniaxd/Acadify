from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional
from src.enums.users.coordinador_enums import EstadoCoordinador


class InstitucionCoordinadorBase(BaseModel):
    institucion_id: UUID
    coordinador_id: UUID
    fecha_asignacion: date
    estado: Optional[EstadoCoordinador] = None


class InstitucionCoordinadorCreate(InstitucionCoordinadorBase):
    pass


class InstitucionCoordinadorUpdate(BaseModel):
    fecha_asignacion: date | None = None
    estado: EstadoCoordinador | None = None


class InstitucionCoordinadorOut(InstitucionCoordinadorBase):
    institucion_coordinador_id: UUID

    class Config:
        from_attributes = True
