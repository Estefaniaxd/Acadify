import uuid
from datetime import date
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from src.enums.docente_enums import TipoVinculacionDocente


class DocenteBase(BaseModel):
    area_conocimiento: str
    fecha_vinculacion: date
    tipo_vinculacion: TipoVinculacionDocente = TipoVinculacionDocente.planta
    titulo_academico: Optional[str] = None
    horas_semanales: Optional[int] = None


class DocenteCreate(DocenteBase):
    docente_id: uuid.UUID


class DocenteRead(DocenteBase):
    docente_id: uuid.UUID

    class Config:
        from_attributes = True
