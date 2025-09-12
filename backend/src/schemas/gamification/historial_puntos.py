from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class UsuarioPuntosBase(BaseModel):
    puntos_acumulados: int = Field(ge=0, description="Puntos acumulados del usuario")


class UsuarioPuntosResponse(UsuarioPuntosBase):
    usuario_id: UUID

    class Config:
        from_attributes = True


class HistorialPuntosBase(BaseModel):
    cambio: int = Field(ne=0, description="Cambio en puntos (positivo o negativo)")
    motivo: str | None = Field(None, max_length=500, description="Motivo del cambio")


class HistorialPuntosCreate(HistorialPuntosBase):
    usuario_id: UUID


class HistorialPuntosResponse(HistorialPuntosBase):
    historial_id: UUID
    usuario_id: UUID
    fecha: datetime

    class Config:
        from_attributes = True


class AsignarPuntosRequest(BaseModel):
    usuario_id: UUID
    puntos: int = Field(gt=0, description="Cantidad de puntos a asignar")
    motivo: str | None = Field(
        None, max_length=500, description="Motivo de la asignación"
    )


class DescontarPuntosRequest(BaseModel):
    usuario_id: UUID
    puntos: int = Field(gt=0, description="Cantidad de puntos a descontar")
    motivo: str | None = Field(None, max_length=500, description="Motivo del descuento")


class RankingUsuarioResponse(BaseModel):
    usuario_id: UUID
    nombres: str
    apellidos: str
    puntos_acumulados: int
    posicion: int

    class Config:
        from_attributes = True


class EstadisticasPuntosResponse(BaseModel):
    total_usuarios_con_puntos: int
    promedio_puntos: float
    puntos_maximos: int
    puntos_minimos: int
    total_puntos_distribuidos: int
