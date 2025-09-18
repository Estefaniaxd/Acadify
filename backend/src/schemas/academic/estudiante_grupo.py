from pydantic import BaseModel
from uuid import UUID
from datetime import date


class EstudianteGrupoBase(BaseModel):
    fecha_vinculacion: date


class EstudianteGrupoCreate(EstudianteGrupoBase):
    grupo_id: UUID
    estudiante_id: UUID


class EstudianteGrupoUpdate(BaseModel):
    fecha_vinculacion: date | None = None


class EstudianteGrupoInDBBase(EstudianteGrupoBase):
    grupo_id: UUID
    estudiante_id: UUID

    class Config:
        from_attributes = True


class EstudianteGrupo(EstudianteGrupoInDBBase):
    pass
