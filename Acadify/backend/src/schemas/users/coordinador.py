from uuid import UUID
from datetime import date
from pydantic import BaseModel


class CoordinadorBase(BaseModel):
    horario_atencion: str | None = None
    fecha_inicio_carrera: date


class CoordinadorCreate(CoordinadorBase):
    pass


class CoordinadorUpdate(CoordinadorBase):
    horario_atencion: str | None = None
    fecha_inicio_carrera: date | None = None


class CoordinadorInDBBase(CoordinadorBase):
    coordinador_id: UUID

    class Config:
        from_attributes = True


class Coordinador(CoordinadorInDBBase):
    pass
