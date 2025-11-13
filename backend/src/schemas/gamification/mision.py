"""Schemas Pydantic para el sistema de misiones."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.enums.gamification.mision_enums import (
    DificultadMision,
    EstadoMision,
    FrecuenciaMision,
    TipoMision,
)


# ==================== Schemas de Mision ====================
class MisionBase(BaseModel):
    """Base schema para Misión."""

    nombre: str = Field(max_length=150, description="Nombre de la misión")
    descripcion: str = Field(description="Descripción detallada de la misión")
    icono: str | None = Field(None, max_length=50, description="Emoji o icono")
    tipo: TipoMision = Field(description="Tipo de misión")
    frecuencia: FrecuenciaMision = Field(
        default=FrecuenciaMision.DIARIA, description="Frecuencia de la misión"
    )
    dificultad: DificultadMision = Field(
        default=DificultadMision.NORMAL, description="Nivel de dificultad"
    )
    objetivo: int = Field(gt=0, description="Cantidad a completar")
    unidad: str | None = Field(None, max_length=50, description="Unidad de medida")
    puntos_recompensa: int = Field(ge=0, default=0, description="Puntos a ganar")
    experiencia_recompensa: int = Field(
        ge=0, default=0, description="Experiencia a ganar"
    )
    recompensas_extra: dict | None = Field(
        None, description="Recompensas adicionales (JSON)"
    )
    es_activa: bool = Field(default=True, description="Si la misión está activa")
    requisitos: dict | None = Field(None, description="Requisitos previos (JSON)")
    orden_visualizacion: int = Field(default=0, description="Orden de visualización")


class MisionCreate(MisionBase):
    """Schema para crear una misión."""

    pass


class MisionUpdate(BaseModel):
    """Schema para actualizar una misión."""

    nombre: str | None = Field(None, max_length=150)
    descripcion: str | None = None
    icono: str | None = None
    tipo: TipoMision | None = None
    frecuencia: FrecuenciaMision | None = None
    dificultad: DificultadMision | None = None
    objetivo: int | None = Field(None, gt=0)
    unidad: str | None = None
    puntos_recompensa: int | None = Field(None, ge=0)
    experiencia_recompensa: int | None = Field(None, ge=0)
    recompensas_extra: dict | None = None
    es_activa: bool | None = None
    requisitos: dict | None = None
    orden_visualizacion: int | None = None


class MisionResponse(MisionBase):
    """Schema para respuesta de misión."""

    mision_id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# ==================== Schemas de MisionUsuario ====================
class MisionUsuarioBase(BaseModel):
    """Base schema para MisionUsuario."""

    estado: EstadoMision = Field(
        default=EstadoMision.DISPONIBLE, description="Estado de la misión"
    )
    progreso_actual: int = Field(ge=0, default=0, description="Progreso actual")


class MisionUsuarioCreate(MisionUsuarioBase):
    """Schema para asignar una misión a un usuario."""

    usuario_id: UUID
    mision_id: UUID
    fecha_expiracion: datetime | None = Field(
        None, description="Fecha de expiración"
    )


class MisionUsuarioUpdate(BaseModel):
    """Schema para actualizar progreso de misión."""

    progreso_actual: int | None = Field(None, ge=0)
    estado: EstadoMision | None = None
    metadata_progreso: dict | None = None


class MisionUsuarioResponse(MisionUsuarioBase):
    """Schema para respuesta de misión de usuario."""

    mision_usuario_id: UUID
    usuario_id: UUID
    mision_id: UUID
    fecha_asignacion: datetime
    fecha_inicio: datetime | None = None
    fecha_completada: datetime | None = None
    fecha_reclamada: datetime | None = None
    fecha_expiracion: datetime | None = None
    metadata_progreso: dict | None = None
    fecha_actualizacion: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class MisionUsuarioConDetalle(MisionUsuarioResponse):
    """Schema con detalles completos de la misión."""

    mision: MisionResponse

    class Config:
        """Pydantic config."""

        from_attributes = True


# ==================== Schemas de Requests ====================
class ActualizarProgresoRequest(BaseModel):
    """Request para actualizar progreso de una misión."""

    incremento: int = Field(gt=0, description="Cantidad a incrementar")
    metadata: dict | None = Field(None, description="Metadatos adicionales")


class ReclamarRecompensaRequest(BaseModel):
    """Request para reclamar recompensa de misión completada."""

    pass  # No necesita campos adicionales


class MisionesDisponiblesResponse(BaseModel):
    """Response con misiones disponibles agrupadas."""

    diarias: list[MisionUsuarioConDetalle]
    semanales: list[MisionUsuarioConDetalle]
    mensuales: list[MisionUsuarioConDetalle]
    unicas: list[MisionUsuarioConDetalle]
    total_disponibles: int
    total_completadas_hoy: int


class EstadisticasMisionesResponse(BaseModel):
    """Estadísticas de misiones del usuario."""

    total_completadas: int
    total_en_progreso: int
    racha_actual: int  # Días consecutivos completando misiones diarias
    racha_maxima: int
    puntos_ganados_misiones: int
    misiones_por_tipo: dict[str, int]
    misiones_por_dificultad: dict[str, int]
