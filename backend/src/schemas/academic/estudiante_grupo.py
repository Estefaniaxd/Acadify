from pydantic import BaseModel
from uuid import UUID
from datetime import date


class EstudianteGrupoBase(BaseModel):
    grupo_id: UUID
    estudiante_id: UUID
    fecha_vinculacion: date


class EstudianteGrupoCreate(EstudianteGrupoBase):
    pass


class EstudianteGrupoUpdate(BaseModel):
    fecha_vinculacion: date


class EstudianteGrupoInDBBase(EstudianteGrupoBase):
    class Config:
        from_attributes = True


class EstudianteGrupo(EstudianteGrupoInDBBase):
    pass
