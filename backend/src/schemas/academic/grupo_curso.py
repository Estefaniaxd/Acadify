from pydantic import BaseModel
from uuid import UUID
from datetime import date


class GrupoCursoBase(BaseModel):
    grupo_id: UUID
    curso_id: UUID
    docente_id: UUID
    fecha_asignacion: date | None = None


class GrupoCursoCreate(GrupoCursoBase):
    pass


class GrupoCursoUpdate(BaseModel):
    docente_id: UUID | None = None
    fecha_asignacion: date | None = None


class GrupoCursoResponse(GrupoCursoBase):
    grupo_curso_id: UUID

    class Config:
        from_attributes = True
