from pydantic import BaseModel
from uuid import UUID
from datetime import date


class CursoDocenteBase(BaseModel):
    curso_id: UUID
    docente_id: UUID
    fecha_asignada: date | None = None


class CursoDocenteCreate(CursoDocenteBase):
    pass


class CursoDocenteUpdate(BaseModel):
    fecha_asignada: date | None = None


class CursoDocenteResponse(CursoDocenteBase):
    class Config:
        from_attributes = True
