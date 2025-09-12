from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from src.enums.academic.grupo_enums import JornadaGrupo


class GrupoBase(BaseModel):
    programa_id: UUID
    docente_tutor_id: Optional[UUID] = None
    nombre: str
    jornada: Optional[JornadaGrupo] = None


class GrupoCreate(GrupoBase):
    pass


class GrupoUpdate(BaseModel):
    docente_tutor_id: Optional[UUID] = None
    nombre: Optional[str] = None
    jornada: Optional[JornadaGrupo] = None


class GrupoResponse(GrupoBase):
    grupo_id: UUID

    class Config:
        orm_mode = True
