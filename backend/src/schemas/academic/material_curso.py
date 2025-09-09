from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class MaterialCursoBase(BaseModel):
    material_curso_id: UUID
    curso_id: Optional[UUID] = None


class MaterialCursoCreate(MaterialCursoBase):
    pass


class MaterialCursoUpdate(BaseModel):
    curso_id: Optional[UUID] = None


class MaterialCursoResponse(MaterialCursoBase):
    class Config:
        orm_mode = True
