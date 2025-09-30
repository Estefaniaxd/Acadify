from pydantic import BaseModel
from uuid import UUID
from datetime import date
from ...enums.academic.curso_enums import ModalidadCurso


class CursoBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    modalidad: ModalidadCurso
    fecha_inicio: date | None = None
    fecha_fin: date | None = None


class CursoCreate(CursoBase):
    institucion_id: UUID
    coordinador_id: UUID | None = None
    programa_id: UUID | None = None


class CursoUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    modalidad: ModalidadCurso | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None


class CursoInDBBase(CursoBase):
    curso_id: UUID
    institucion_id: UUID
    coordinador_id: UUID | None = None
    programa_id: UUID | None = None

    class Config:
        from_attributes = True


class Curso(CursoInDBBase):
    pass
