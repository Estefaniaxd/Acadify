from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date


class CursoDocenteBase(BaseModel):
    curso_id: UUID
    docente_id: UUID
    fecha_asignada: Optional[date] = None


class CursoDocenteCreate(CursoDocenteBase):
    pass


class CursoDocenteUpdate(BaseModel):
    fecha_asignada: Optional[date] = None


class CursoDocenteResponse(CursoDocenteBase):
    class Config:
        orm_mode = True
