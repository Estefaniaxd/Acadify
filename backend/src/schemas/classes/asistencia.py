from pydantic import BaseModel
from uuid import UUID
from ...enums.classes.asistencia_enums import EstadoAsistencia


class AsistenciaBase(BaseModel):
    estado: EstadoAsistencia


class AsistenciaCreate(AsistenciaBase):
    clase_id: UUID
    estudiante_id: UUID


class AsistenciaUpdate(BaseModel):
    estado: EstadoAsistencia | None = None


class AsistenciaInDBBase(AsistenciaBase):
    asistencia_id: UUID
    clase_id: UUID
    estudiante_id: UUID

    class Config:
        from_attributes = True


class Asistencia(AsistenciaInDBBase):
    pass
