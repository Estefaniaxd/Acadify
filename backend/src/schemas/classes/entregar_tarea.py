from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Annotated


class EntregarTareaBase(BaseModel):
    archivo: str | None = None
    calificacion: Annotated[
        Decimal,
        Field(
            ge=0,
            le=5,
            description="Calificación con un decimal, entre 0.0 y 5.0",
        ),
    ]
    fecha_revision: datetime | None = None


class EntregarTareaCreate(EntregarTareaBase):
    tarea_id: UUID
    estudiante_id: UUID


class EntregarTareaUpdate(BaseModel):
    archivo: str
    calificacion: (
        Annotated[
            Decimal,
            Field(
                ge=0,
                le=5,
                description="Calificación con un decimal, entre 0.0 y 5.0",
            ),
        ]
        | None
    ) = None
    fecha_revision: datetime | None = None


class EntregarTareaInDBBase(EntregarTareaBase):
    entrega_id: UUID
    tarea_id: UUID
    estudiante_id: UUID
    fecha_envio: datetime

    class Config:
        from_attributes = True


class EntregarTarea(EntregarTareaInDBBase):
    pass
