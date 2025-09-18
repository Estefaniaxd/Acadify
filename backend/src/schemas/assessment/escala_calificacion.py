from uuid import UUID
from pydantic import BaseModel, Field
from typing import Annotated
from decimal import Decimal
from ...enums.assessment.escala_calificacion_eunms import TipoEscalafonEnum


class EscalaCalificacionBase(BaseModel):
    nombre: str
    tipo: TipoEscalafonEnum
    min_valor: Annotated[
        Decimal,
        Field(
            max_digits=5,
            decimal_places=2,
            description="Valor mínimo con hasta 5 dígitos y 2 decimales",
        ),
    ]
    max_valor: Annotated[
        Decimal,
        Field(
            max_digits=5,
            decimal_places=2,
            description="Valor máximo con hasta 5 dígitos y 2 decimales",
        ),
    ]


class EscalaCalificacionCreate(EscalaCalificacionBase):
    institucion_id: UUID


class EscalaCalificacionUpdate(BaseModel):
    nombre: str | None = None
    tipo: TipoEscalafonEnum | None = None
    min_valor: (
        Annotated[
            Decimal,
            Field(
                max_digits=5,
                decimal_places=2,
                description="Valor mínimo con hasta 5 dígitos y 2 decimales",
            ),
        ]
        | None
    ) = None
    max_valor: (
        Annotated[
            Decimal,
            Field(
                max_digits=5,
                decimal_places=2,
                description="Valor máximo con hasta 5 dígitos y 2 decimales",
            ),
        ]
        | None
    ) = None


class EscalaCalificacionInDBBase(EscalaCalificacionBase):
    escala_id: UUID
    institucion_id: UUID

    class Config:
        from_attributes = True


class EscalaCalificacion(EscalaCalificacionInDBBase):
    pass
