from pydantic import BaseModel
import uuid
from datetime import date
from typing import Optional
from src.enums.users.estudiante_enums import EtapaFormativaEstudiante


class EstudianteBase(BaseModel):
    programa_id: uuid.UUID
    fecha_ingreso: date
    creditos_aprobados: int | None = None
    etapa_formativa: Optional[EtapaFormativaEstudiante] = None
    promedio_acumulado: float | None = None


class EstudianteCreate(EstudianteBase):
    estudiante_id: uuid.UUID


class EstudianteUpdate(BaseModel):
    programa_id: uuid.UUID | None = None
    fecha_ingreso: date | None = None
    creditos_aprobados: int | None = None
    etapa_formativa: EtapaFormativaEstudiante | None = None
    promedio_acumulado: float | None = None


class EstudianteOut(EstudianteBase):
    estudiante_id: uuid.UUID

    class Config:
        orm_mode = True
