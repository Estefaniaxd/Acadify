from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date
from src.enums.academic.curso_enums import ModalidadCurso


class CursoBase(BaseModel):
    institucion_id: UUID
    coordinador_id: Optional[UUID] = None
    programa_id: UUID
    nombre: str
    descripcion: Optional[str] = None
    modalidad: ModalidadCurso
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class CursoCreate(CursoBase):
    pass


class CursoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    modalidad: Optional[ModalidadCurso] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class CursoResponse(CursoBase):
    curso_id: UUID

    class Config:
        orm_mode = True
