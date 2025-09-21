from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from src.enums.academic.institucion_enums import (
    TipoInstitucion,
    NivelEducativoInstitucion, 
    SectorInstitucion,
    EstadoInstitucion
)

class InstitucionCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150, description="Nombre de la institución")
    sigla: Optional[str] = Field(None, max_length=20, description="Sigla de la institución")
    lema: Optional[str] = Field(None, max_length=255, description="Lema de la institución")
    tipo_institucion: TipoInstitucion = Field(..., description="Tipo de institución")
    usa_programas: bool = Field(..., description="Si la institución usa programas académicos")
    nivel_educativo: NivelEducativoInstitucion = Field(..., description="Nivel educativo de la institución")
    sector: SectorInstitucion = Field(..., description="Sector de la institución (público/privado)")
    direccion: Optional[str] = Field(None, max_length=255, description="Dirección de la institución")
    ciudad: Optional[str] = Field(None, max_length=100, description="Ciudad donde se ubica")
    pais: str = Field(..., max_length=100, description="País donde se ubica")
    correo_institucional: EmailStr = Field(..., description="Correo electrónico institucional")
    telefono: str = Field(..., max_length=30, description="Teléfono de contacto")
    nit: Optional[str] = Field(None, max_length=20, description="NIT o número de identificación tributaria")

class InstitucionResponse(BaseModel):
    institucion_id: UUID
    nombre: str
    sigla: Optional[str]
    lema: Optional[str]
    tipo_institucion: TipoInstitucion
    usa_programas: bool
    nivel_educativo: NivelEducativoInstitucion
    sector: SectorInstitucion
    direccion: Optional[str]
    ciudad: Optional[str]
    pais: str
    correo_institucional: EmailStr
    telefono: str
    nit: Optional[str]
    estado: EstadoInstitucion
    fecha_creacion: Optional[datetime]
    fecha_activacion: Optional[datetime]

    model_config = {
        "from_attributes": True
    }
