from uuid import UUID
from datetime import date
from pydantic import BaseModel


class CoordinadorBase(BaseModel):
    horario_atencion: str | None = None
    fecha_inicio_carrera: date


class CoordinadorCreate(CoordinadorBase):
    coordinador_id: UUID
    institucion_id: UUID


class CoordinadorUpdate(CoordinadorBase):
    pass


class CoordinadorInDBBase(CoordinadorBase):
    coordinador_id: UUID
    institucion_id: UUID

    class Config:
        from_attributes = True


class Coordinador(CoordinadorInDBBase):
    pass


class CoordinadorInDB(CoordinadorInDBBase):
    pass
