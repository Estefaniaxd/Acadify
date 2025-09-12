# src/schemas/academic/plataforma.py
from pydantic import BaseModel
from uuid import UUID
from src.enums.academic import TipoIntegracionPlataforma


class PlataformaBase(BaseModel):
    nombre: str
    url_base: str
    tipo_integracion: TipoIntegracionPlataforma
    requiere_cuenta: bool
    es_gratuita: bool | None = None


class PlataformaCreate(PlataformaBase):
    """Schema para crear plataforma"""

    pass


class PlataformaUpdate(BaseModel):
    """Schema para actualizar plataforma"""

    nombre: str | None = None
    url_base: str | None = None
    tipo_integracion: TipoIntegracionPlataforma | None = None
    requiere_cuenta: bool | None = None
    es_gratuita: bool | None = None


class PlataformaRead(PlataformaBase):
    """Schema de lectura de plataforma"""

    plataforma_id: UUID

    class Config:
        from_attributes = True
