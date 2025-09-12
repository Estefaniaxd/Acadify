from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date


class GrupoCursoBase(BaseModel):
    grupo_id: UUID
    curso_id: UUID
    docente_id: UUID
    fecha_asignacion: Optional[date] = None


class GrupoCursoCreate(GrupoCursoBase):
    pass


class GrupoCursoUpdate(BaseModel):
    docente_id: Optional[UUID] = None
    fecha_asignacion: Optional[date] = None


class GrupoCursoResponse(GrupoCursoBase):
    grupo_curso_id: UUID

    class Config:
        from_attribute = True
