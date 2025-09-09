from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class MaterialClaseBase(BaseModel):
    material_clase_id: UUID
    clase_id: Optional[UUID] = None


class MaterialClaseCreate(MaterialClaseBase):
    pass


class MaterialClaseUpdate(BaseModel):
    clase_id: Optional[UUID] = None


class MaterialClaseResponse(MaterialClaseBase):
    class Config:
        orm_mode = True
