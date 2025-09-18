from pydantic import BaseModel, EmailStr
from uuid import UUID
from ...enums.academic.institucion_enums import (
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
    administrador_id_creador: UUID | None = None


class InstitucionUpdate(BaseModel):
    nombre: str | None = None
    sigla: str | None = None
    lema: str | None = None
    tipo_institucion: TipoInstitucion | None = None
    usa_programas: bool | None = None
    nivel_educativo: NivelEducativoInstitucion | None = None
    sector: SectorInstitucion | None = None
    direccion: str | None = None
    ciudad: str | None = None
    pais: str | None = None
    correo_institucional: EmailStr | None = None
    telefono: str | None = None
    nit: str | None = None


class InstitucionInDBBase(InstitucionBase):
    institucion_id: UUID
    administrador_id_creador: UUID | None = None

    class Config:
        from_attributes = True


class Institucion(InstitucionInDBBase):
    pass
