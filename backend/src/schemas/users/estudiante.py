from pydantic import BaseModel
from uuid import UUID
from datetime import date
from src.enums.users.estudiante_enums import EtapaFormativaEstudiante


class EstudianteBase(BaseModel):
    programa_id: UUID
    fecha_ingreso: date
    creditos_aprobados: int | None = None
    etapa_formativa: EtapaFormativaEstudiante | None = None
    promedio_acumulado: float | None = None


class EstudianteCreate(EstudianteBase):
    estudiante_id: UUID


class EstudianteUpdate(BaseModel):
    programa_id: UUID | None = None
    fecha_ingreso: date | None = None
    creditos_aprobados: int | None = None
    etapa_formativa: EtapaFormativaEstudiante | None = None
    promedio_acumulado: float | None = None


class EstudianteOut(EstudianteBase):
    estudiante_id: UUID

    class Config:
        from_attributes = True
