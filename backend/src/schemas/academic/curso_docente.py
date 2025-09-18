from pydantic import BaseModel
from uuid import UUID
from datetime import date


class CursoDocenteBase(BaseModel):
    fecha_asignada: date | None = None


class CursoDocenteCreate(CursoDocenteBase):
    curso_id: UUID
    docente_id: UUID

class CursoDocenteUpdate(BaseModel):
    fecha_asignacion: date | None = None


class CursoDocenteInDBBase(CursoDocenteBase):
    curso_id: UUID
    docente_id: UUID
    
    class Config:
        from_attributes = True

class CursoDocente(CursoDocenteInDBBase):
    pass