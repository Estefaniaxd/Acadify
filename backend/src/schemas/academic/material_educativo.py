from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from src.enums.academic.material_educativo_enums import TipoMaterialEducativo


class MaterialEducativoBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    tipo_material: TipoMaterialEducativo
    url_archivo: str
    formato_archivo: str


class MaterialEducativoCreate(MaterialEducativoBase):
    pass


class MaterialEducativoUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_material: Optional[TipoMaterialEducativo] = None
    url_archivo: Optional[str] = None
    formato_archivo: Optional[str] = None


class MaterialEducativoResponse(MaterialEducativoBase):
    material_id: UUID

    class Config:
        orm_mode = True
