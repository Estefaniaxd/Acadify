from pydantic import BaseModel
from uuid import UUID
from datetime import date
from src.enums.academic.curso_enums import ModalidadCurso


class CursoBase(BaseModel):
    institucion_id: UUID
    coordinador_id: UUID | None = None
    programa_id: UUID
    nombre: str
    descripcion: str | None = None
    modalidad: ModalidadCurso
    fecha_inicio: date | None = None
    fecha_fin: date | None = None


class CursoCreate(CursoBase):
    pass


class CursoUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    modalidad: ModalidadCurso | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None


class CursoResponse(CursoBase):
    curso_id: UUID

    class Config:
        from_attributes = True
