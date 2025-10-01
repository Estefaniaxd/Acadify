from pydantic import BaseModel
from uuid import UUID
from ...enums.academic.grupo_enums import JornadaGrupo


class GrupoBase(BaseModel):
    nombre: str
    jornada: JornadaGrupo = JornadaGrupo.manana


class GrupoCreate(GrupoBase):
    programa_id: UUID | None = None
    docente_tutor_id: UUID | None = None


class GrupoUpdate(BaseModel):
    nombre: str | None = None
    jornada: JornadaGrupo | None = None


class GrupoInDBBase(GrupoBase):
    grupo_id: UUID
    programa_id: UUID | None = None
    docente_tutor_id: UUID | None = None

    class Config:
        from_attributes = True


class Grupo(GrupoInDBBase):
    pass
