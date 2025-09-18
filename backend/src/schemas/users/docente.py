from uuid import UUID
from datetime import date
from pydantic import BaseModel
from ...enums.users.docente_enums import TipoVinculacionDocente


class DocenteBase(BaseModel):
    area_conocimiento: str
    fecha_vinculacion: date
    tipo_vinculacion: TipoVinculacionDocente = TipoVinculacionDocente.planta
    titulo_academico: str | None = None
    horas_semanales: int | None = None


class DocenteCreate(DocenteBase):
    pass

class DocenteUpdate(BaseModel):
    area_conocimiento: str | None = None
    fecha_vinculacion: date | None = None
    tipo_vinculacion: TipoVinculacionDocente | None = None
    titulo_academico: str | None = None
    horas_semanales: int | None = None

class DocenteInDBBase(DocenteBase):
    docente_id: UUID
    
    class Config:
        from_attributes = True

class Docente(DocenteInDBBase):
    pass
