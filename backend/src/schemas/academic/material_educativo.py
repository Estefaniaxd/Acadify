from pydantic import BaseModel
from uuid import UUID
from ...enums.academic.material_educativo_enums import TipoMaterialEducativo


class MaterialEducativoBase(BaseModel):
    titulo: str
    descripcion: str | None = None
    tipo_material: TipoMaterialEducativo
    url_archivo: str
    formato_archivo: str


class MaterialEducativoCreate(MaterialEducativoBase):
    pass


class MaterialEducativoUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    tipo_material: TipoMaterialEducativo | None = None
    url_archivo: str | None = None
    formato_archivo: str | None = None


class MaterialEducativoInDBBase(MaterialEducativoBase):
    material_id: UUID

    class Config:
        from_attributes = True


class MaterialEducativo(MaterialEducativoInDBBase):
    pass
