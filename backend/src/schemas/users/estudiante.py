from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date
from ...enums.users.estudiante_enums import EtapaFormativaEstudiante
from typing import Annotated
from decimal import Decimal


class EstudianteBase(BaseModel):
    fecha_ingreso: date
    creditos_aprobados: int | None = None
    etapa_formativa: EtapaFormativaEstudiante = EtapaFormativaEstudiante.i
    promedio_acumulado: Annotated[Decimal, Field(ge=0, le=9.99)] | None = None


class EstudianteCreate(EstudianteBase):
    programa_id: UUID | None = None


class EstudianteUpdate(BaseModel):
    fecha_ingreso: date | None = None
    creditos_aprobados: int | None = None
    etapa_formativa: EtapaFormativaEstudiante | None = None
    promedio_acumulado: Annotated[Decimal, Field(ge=0, le=9.99)] | None = None


class EstudianteInDBBase(EstudianteBase):
    estudiante_id: UUID
    programa_id: UUID | None = None

    class Config:
        from_attributes = True


class Estudiante(EstudianteInDBBase):
    pass
