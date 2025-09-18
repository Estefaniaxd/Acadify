from pydantic import BaseModel
from uuid import UUID
from datetime import date
from ...enums.users.coordinador_enums import EstadoCoordinador


class InstitucionCoordinadorBase(BaseModel):
    fecha_asignacion: date
    estado: EstadoCoordinador = EstadoCoordinador.activo


class InstitucionCoordinadorCreate(InstitucionCoordinadorBase):
    institucion_id: UUID
    coordinador_id: UUID


class InstitucionCoordinadorUpdate(BaseModel):
    fecha_asignacion: date | None = None
    estado: EstadoCoordinador | None = None


class InstitucionCoordinadorInDBBase(InstitucionCoordinadorBase):
    institucion_id: UUID
    coordinador_id: UUID

    class Config:
        from_attributes = True


class InstitucionCoordinador(InstitucionCoordinadorInDBBase):
    pass
