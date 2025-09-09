from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TareaBase(BaseModel):
    docente_id: UUID | None = None
    clase_id: UUID
    titulo: str
    descripcion: str | None = None
    fecha_asignacion: datetime | None = None
    fecha_limite: datetime | None = None
    archivo_adjunto: str | None = None
    permite_entregas_tardias: bool

class TareaCreate(TareaBase):
    pass

class TareaUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    fecha_limite: datetime | None = None
    archivo_adjunto: str | None = None
    permite_entregas_tardias: bool | None = None
    docente_id: UUID | None = None

class TareaInDBBase(TareaBase):
    tarea_id: UUID

    class Config:
        from_attributes = True

class Tarea(TareaInDBBase):
    pass
