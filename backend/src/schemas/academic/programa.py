from pydantic import BaseModel
from uuid import UUID
from ...enums.academic.programa_enums import NivelPrograma, TipoPrograma


class ProgramaBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    nivel: NivelPrograma
    tipo: TipoPrograma


class ProgramaCreate(ProgramaBase):
    institucion_id: UUID


class ProgramaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    nivel: NivelPrograma | None = None
    tipo: TipoPrograma | None = None


class ProgramaInDBBase(ProgramaBase):
    programa_id: UUID
    institucion_id: UUID

    class Config:
        from_attributes = True


class Programa(ProgramaInDBBase):
    pass
