"""
Schemas para el sistema de rachas.

Define los schemas de validación para:
- Racha de usuario
- Historial de racha
- Recompensas de racha
- Milestones
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field

from src.enums.gamification import (
    TipoEventoRacha, TipoMilestone, TipoActividadRacha
)


# =============================================================================
# RACHA USUARIO SCHEMAS
# =============================================================================

class RachaUsuarioResponse(BaseModel):
    """Schema de respuesta para racha del usuario."""
    usuario_id: UUID
    racha_actual: int
    mejor_racha: int
    fecha_ultimo_dia: Optional[date]
    racha_congelada_hasta: Optional[date]
    recuperaciones_disponibles: int
    notificacion_enviada: bool
    ultima_recompensa_dia: int
    
    # Propiedades computadas
    esta_protegida: bool
    puede_recuperar: bool
    dia_ciclo_semanal: int
    dias_proteccion_restantes: int = 0
    
    # Información adicional
    puntos_hoy: int = 0
    milestone_proximo: Optional[int] = None
    dias_hasta_milestone: Optional[int] = None

    class Config:
        from_attributes = True


class VerificarRachaRequest(BaseModel):
    """Request para verificar racha diaria."""
    tipo_actividad: TipoActividadRacha = TipoActividadRacha.TAREA_COMPLETADA
    actividad_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class RecuperarRachaRequest(BaseModel):
    """Request para recuperar racha perdida."""
    confirmar: bool = True


class ActivarCongeladorRequest(BaseModel):
    """Request para activar congelador de racha."""
    dias: int = Field(..., ge=1, le=7)


# =============================================================================
# HISTORIAL RACHA SCHEMAS
# =============================================================================

class HistorialRachaResponse(BaseModel):
    """Schema de respuesta para evento de racha."""
    historial_id: UUID
    usuario_id: UUID
    fecha: date
    timestamp: datetime
    racha_anterior: int
    racha_nueva: int
    tipo_evento: TipoEventoRacha
    puntos_otorgados: int
    descripcion: Optional[str]
    metadata_json: Optional[Dict[str, Any]]
    
    # Propiedades computadas
    cambio_racha: int
    fue_incremento: bool
    fue_perdida: bool
    fue_milestone: bool

    class Config:
        from_attributes = True


class HistorialRachaDetalle(HistorialRachaResponse):
    """Schema detallado con información adicional."""
    milestone_alcanzado: Optional[int] = None
    insignia_otorgada: Optional[str] = None


# =============================================================================
# RECOMPENSA RACHA SCHEMAS
# =============================================================================

class RecompensaRachaBase(BaseModel):
    """Schema base para recompensa de racha."""
    dias_requeridos: int = Field(..., ge=1)
    puntos_recompensa: int = Field(..., ge=0)
    tipo_milestone: TipoMilestone
    mensaje_motivacional: Optional[str] = Field(None, max_length=500)
    es_repetible: bool = Field(default=False)


class RecompensaRachaCreate(RecompensaRachaBase):
    """Schema para crear recompensa."""
    insignia_id: Optional[UUID] = None


class RecompensaRachaUpdate(BaseModel):
    """Schema para actualizar recompensa."""
    puntos_recompensa: Optional[int] = Field(None, ge=0)
    mensaje_motivacional: Optional[str] = Field(None, max_length=500)
    es_activa: Optional[bool] = None


class RecompensaRachaResponse(RecompensaRachaBase):
    """Schema de respuesta para recompensa."""
    recompensa_racha_id: UUID
    insignia_id: Optional[UUID]
    es_activa: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    # Propiedades computadas
    tiene_insignia: bool
    
    # Información adicional
    insignia_nombre: Optional[str] = None
    insignia_descripcion: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# RESPONSE SCHEMAS COMPUESTOS
# =============================================================================

class EstadisticasRachaResponse(BaseModel):
    """Estadísticas completas de racha."""
    racha: RachaUsuarioResponse
    total_dias_activos: int
    total_recuperaciones_usadas: int
    total_congeladores_usados: int
    milestones_completados: int
    milestones_disponibles: int
    total_puntos_ganados: int
    promedio_puntos_dia: float
    record_personal: int
    record_personal_fecha: Optional[date]


class MilestonesResponse(BaseModel):
    """Response para milestones disponibles."""
    milestones: List[RecompensaRachaResponse]
    milestones_completados: List[int]
    proximo_milestone: Optional[RecompensaRachaResponse]
    dias_hasta_proximo: Optional[int]


class VerificarRachaResponse(BaseModel):
    """Response después de verificar racha."""
    success: bool
    message: str
    racha: RachaUsuarioResponse
    evento: HistorialRachaResponse
    puntos_ganados: int
    milestone_alcanzado: Optional[RecompensaRachaResponse]
    insignia_obtenida: Optional[str] = None


class RecuperarRachaResponse(BaseModel):
    """Response después de recuperar racha."""
    success: bool
    message: str
    racha: RachaUsuarioResponse
    evento: HistorialRachaResponse
    recuperaciones_restantes: int


class ActivarCongeladorResponse(BaseModel):
    """Response después de activar congelador."""
    success: bool
    message: str
    racha: RachaUsuarioResponse
    protegida_hasta: date
    dias_proteccion: int


class HistorialRachaListResponse(BaseModel):
    """Response para lista de historial."""
    eventos: List[HistorialRachaDetalle]
    total: int
    pagina: int
    items_por_pagina: int
    total_paginas: int
