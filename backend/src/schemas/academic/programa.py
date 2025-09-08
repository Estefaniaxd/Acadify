from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from src.enums.academic.programa_enums import NivelPrograma, TipoPrograma

class ProgramaBase(BaseModel):
    institucion_id: UUID
    nombre: str
    descripcion: str | None = None
    nivel: NivelPrograma
    tipo: TipoPrograma

class ProgramaCreate(ProgramaBase):
    pass

class ProgramaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    nivel: NivelPrograma | None = None
    tipo: TipoPrograma | None = None

class ProgramaOut(ProgramaBase):
    programa_id: UUID

    class Config:
        orm_mode = True
