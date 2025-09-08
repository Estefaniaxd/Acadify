from sqlalchemy.dialects.postgresql import UUID
from datetime import date
from pydantic import BaseModel
from typing import Optional


class CoordinadorBase(BaseModel):
    horario_atencion: Optional[str] = None
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
