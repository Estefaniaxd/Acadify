from pydantic import BaseModel
from uuid import UUID
from src.enums.classes.asistencia_enums import EstadoAsistencia


class AsistenciaBase(BaseModel):
    clase_id: UUID
    estudiante_id: UUID
    estado: EstadoAsistencia


class AsistenciaCreate(AsistenciaBase):
    pass


class AsistenciaUpdate(BaseModel):
    estado: EstadoAsistencia | None = None


class AsistenciaInDBBase(AsistenciaBase):
    asistencia_id: UUID

    class Config:
        from_attributes = True


class Asistencia(AsistenciaInDBBase):
    pass
