from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from src.enums.gamification.recompensa_enums import TipoRecompensa


class RecompensaBase(BaseModel):
    nombre: str = Field(max_length=100, description="Nombre de la recompensa")
    descripcion: str | None = Field(None, description="Descripción de la recompensa")
    costo_puntos: int = Field(ge=0, description="Puntos necesarios para canjear")


class RecompensaCreate(RecompensaBase):
    tipo: TipoRecompensa = Field(
        default=TipoRecompensa.otro, description="Tipo de recompensa"
    )


class RecompensaUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=100)
    descripcion: str | None = None
    costo_puntos: int | None = Field(None, ge=0)
    tipo: TipoRecompensa | None = None


class RecompensaResponse(RecompensaBase):
    recompensa_id: UUID
    tipo: TipoRecompensa

    class Config:
        from_attributes = True


class UsuarioRecompensaBase(BaseModel):
    pass


class UsuarioRecompensaCreate(UsuarioRecompensaBase):
    usuario_id: UUID
    recompensa_id: UUID


class UsuarioRecompensaResponse(UsuarioRecompensaBase):
    usuario_recompensa_id: UUID
    usuario_id: UUID
    recompensa_id: UUID
    fecha_canje: datetime

    # Datos de la recompensa incluidos
    recompensa: RecompensaResponse

    class Config:
        from_attributes = True


class CanjearRecompensaRequest(BaseModel):
    usuario_id: UUID
    recompensa_id: UUID


class RecompensasDisponiblesResponse(BaseModel):
    recompensa: RecompensaResponse
    puede_canjear: bool
    puntos_faltantes: int


class HistorialCanjesUsuarioResponse(BaseModel):
    usuario_id: UUID
    total_canjes: int
    puntos_gastados_total: int
    canjes: list[UsuarioRecompensaResponse]


class RecompensaConEstadisticasResponse(RecompensaResponse):
    total_canjes: int
    puntos_gastados_total: int
