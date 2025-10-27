from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class TareaBase(BaseModel):
    titulo: str
    descripcion: str | None = None
    fecha_limite: datetime
    archivo_adjunto: str | None = None
    permite_entregas_tardias: bool


class TareaCreate(TareaBase):
    docente_id: UUID | None = None
    clase_id: UUID


class TareaUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    fecha_limite: datetime | None = None
    archivo_adjunto: str | None = None
    permite_entregas_tardias: bool | None = None
    docente_id: UUID | None = None


class TareaInDBBase(TareaBase):
    tarea_id: UUID
    fecha_asignacion: datetime

    class Config:
        from_attributes = True


class Tarea(TareaInDBBase):
    pass
