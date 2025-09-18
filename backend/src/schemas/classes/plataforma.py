# src/schemas/academic/plataforma.py
from pydantic import BaseModel
from uuid import UUID
from ...enums.academic import TipoIntegracionPlataforma


class PlataformaBase(BaseModel):
    nombre: str
    url_base: str
    tipo_integracion: TipoIntegracionPlataforma
    requiere_cuenta: bool
    es_gratuita: bool | None = None


class PlataformaCreate(PlataformaBase):
    pass


class PlataformaUpdate(BaseModel):
    nombre: str | None = None
    url_base: str | None = None
    tipo_integracion: TipoIntegracionPlataforma | None = None
    requiere_cuenta: bool | None = None
    es_gratuita: bool | None = None


class PlataformaInDBBase(PlataformaBase):
    plataforma_id: UUID

    class Config:
        from_attributes = True


class Plataforma(PlataformaInDBBase):
    pass
