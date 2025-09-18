from pydantic import BaseModel
from uuid import UUID


class MaterialCursoBase(BaseModel):
    pass


class MaterialCursoCreate(MaterialCursoBase):
    curso_id: UUID | None = None


class MaterialCursoUpdate(BaseModel):
    pass


class MaterialCursoInDBBase(MaterialCursoBase):
    material_curso_id: UUID
    curso_id: UUID | None = None

    class Config:
        from_attributes = True


class MaterialCurso(MaterialCursoInDBBase):
    pass
