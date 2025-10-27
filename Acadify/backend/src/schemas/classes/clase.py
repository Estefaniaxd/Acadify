from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, timedelta


class ClaseBase(BaseModel):
    titulo: str
    descripcion: str | None = None
    duracion: timedelta
    link_videollamada: str


class ClaseCreate(ClaseBase):
    grupo_curso_id: UUID
    plataforma_id: UUID | None = None


class ClaseUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    hora_inicio: datetime | None = None
    duracion: timedelta | None = None
    link_videollamada: str | None = None


class ClaseInDBBase(ClaseBase):
    clase_id: UUID
    grupo_curso_id: UUID
    plataforma_id: UUID | None = None
    hora_inicio: datetime

    class Config:
        from_attributes = True


class Clase(ClaseInDBBase):
    pass
