import uuid
from pydantic import BaseModel, EmailStr
from src.enums.academic.institucion_enums import (
    TipoInstitucion,
    NivelEducativoInstitucion,
    SectorInstitucion,
)


class InstitucionBase(BaseModel):
    nombre: str
    sigla: str | None = None
    lema: str | None = None
    tipo_institucion: TipoInstitucion
    usa_programas: bool
    nivel_educativo: NivelEducativoInstitucion
    sector: SectorInstitucion
    direccion: str | None = None
    ciudad: str | None = None
    pais: str
    correo_institucional: EmailStr
    telefono: str
    nit: str | None = None


class InstitucionCreate(InstitucionBase):
    administrador_id: uuid.UUID | None = None


class InstitucionRead(InstitucionBase):
    institucion_id: uuid.UUID
    administrador_id: uuid.UUID | None = None

    class Config:
        from_attributes = True
