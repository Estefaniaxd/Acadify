from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, timedelta


class ClaseBase(BaseModel):
    grupo_curso_id: UUID
    plataforma_id: UUID | None = None
    titulo: str
    descripcion: str | None = None
    hora_inicio: datetime
    duracion: timedelta
    link_videollamada: str


class ClaseCreate(ClaseBase):
    pass


class ClaseUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    hora_inicio: datetime | None = None
    duracion: timedelta | None = None
    link_videollamada: str | None = None
    plataforma_id: UUID | None = None


class ClaseInDBBase(ClaseBase):
    clase_id: UUID

    class Config:
        from_attributes = True


class Clase(ClaseInDBBase):
    pass
