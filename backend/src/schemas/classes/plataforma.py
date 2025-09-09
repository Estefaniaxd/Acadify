# src/schemas/academic/plataforma.py
from pydantic import BaseModel
from uuid import UUID
from src.enums.academic import TipoIntegracionPlataforma
from typing import Optional


class PlataformaBase(BaseModel):
    nombre: str
    url_base: str
    tipo_integracion: TipoIntegracionPlataforma
    requiere_cuenta: bool
    es_gratuita: Optional[bool] = None


class PlataformaCreate(PlataformaBase):
    """Schema para crear plataforma"""
    pass


class PlataformaUpdate(BaseModel):
    """Schema para actualizar plataforma"""
    nombre: Optional[str] = None
    url_base: Optional[str] = None
    tipo_integracion: Optional[TipoIntegracionPlataforma] = None
    requiere_cuenta: Optional[bool] = None
    es_gratuita: Optional[bool] = None


class PlataformaRead(PlataformaBase):
    """Schema de lectura de plataforma"""
    plataforma_id: UUID

    class Config:
        from_attributes = True
