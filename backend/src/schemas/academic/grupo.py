from pydantic import BaseModel
from uuid import UUID
from src.enums.academic.grupo_enums import JornadaGrupo


class GrupoBase(BaseModel):
    programa_id: UUID
    docente_tutor_id: UUID | None = None
    nombre: str
    jornada: JornadaGrupo | None = None


class GrupoCreate(GrupoBase):
    pass


class GrupoUpdate(BaseModel):
    docente_tutor_id: UUID | None = None
    nombre: str | None = None
    jornada: JornadaGrupo | None = None


class GrupoResponse(GrupoBase):
    grupo_id: UUID

    class Config:
        from_attributes = True
