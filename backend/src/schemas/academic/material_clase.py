from pydantic import BaseModel
from uuid import UUID


class MaterialClaseBase(BaseModel):
    pass


class MaterialClaseCreate(MaterialClaseBase):
    clase_id: UUID | None = None


class MaterialClaseUpdate(BaseModel):
    pass


class MaterialClaseInDBBase(MaterialClaseBase):
    material_clase_id: UUID
    clase_id: UUID | None = None

    class Config:
        from_attributes = True


class MaterialClase(MaterialClaseInDBBase):
    pass
