from uuid import UUID
from datetime import date
from pydantic import BaseModel
from src.enums.users.docente_enums import TipoVinculacionDocente


class DocenteBase(BaseModel):
    area_conocimiento: str
    fecha_vinculacion: date
    tipo_vinculacion: TipoVinculacionDocente | None = None
    titulo_academico: str | None = None
    horas_semanales: int | None = None


class DocenteCreate(DocenteBase):
    docente_id: UUID


class DocenteRead(DocenteBase):
    docente_id: UUID

    class Config:
        from_attributes = True
