from pydantic import BaseModel
from uuid import UUID


class MaterialCursoBase(BaseModel):
    material_curso_id: UUID
    curso_id: UUID | None = None


class MaterialCursoCreate(MaterialCursoBase):
    pass


class MaterialCursoUpdate(BaseModel):
    curso_id: UUID | None = None


class MaterialCursoResponse(MaterialCursoBase):
    class Config:
        from_attributes = True
