from pydantic import BaseModel
from uuid import UUID


class MaterialClaseBase(BaseModel):
    material_clase_id: UUID
    clase_id: UUID | None = None


class MaterialClaseCreate(MaterialClaseBase):
    pass


class MaterialClaseUpdate(BaseModel):
    clase_id: UUID | None = None


class MaterialClaseResponse(MaterialClaseBase):
    class Config:
        from_attributes = True
