from pydantic import BaseModel
from uuid import UUID
from datetime import date


class GrupoCursoBase(BaseModel):
    fecha_asignacion: date | None = None


class GrupoCursoCreate(GrupoCursoBase):
    grupo_id: UUID
    curso_id: UUID
    docente_id: UUID


class GrupoCursoUpdate(BaseModel):
    fecha_asignacion: date | None = None


class GrupoCursoInDBBase(GrupoCursoBase):
    grupo_curso_id: UUID
    grupo_id: UUID
    curso_id: UUID
    docente_id: UUID

    class Config:
        from_attributes = True


class GrupoCurso(GrupoCursoBase):
    pass
