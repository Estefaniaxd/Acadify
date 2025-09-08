import uuid
from pydantic import BaseModel, EmailStr
from typing import Optional
from src.enums.academic.institucion_enums import TipoInstitucion, NivelEducativoInstitucion, SectorInstitucion

class InstitucionBase(BaseModel):
    nombre: str
    sigla: Optional[str] = None
    lema: Optional[str] = None
    tipo_institucion: TipoInstitucion
    usa_programas: bool
    nivel_educativo: NivelEducativoInstitucion
    sector: SectorInstitucion
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: str
    correo_institucional: EmailStr
    telefono: str
    nit: Optional[str] = None

class InstitucionCreate(InstitucionBase):
    administrador_id: Optional[uuid.UUID] = None

class InstitucionRead(InstitucionBase):
    institucion_id: uuid.UUID
    administrador_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True
