"""
Schemas para el sistema de etiquetas de perfil.

Define los schemas de validación para:
- Etiquetas de perfil
- Etiquetas del usuario
- Evolución de etiquetas
- Equipamiento
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from src.enums.gamification import (
    CategoriaEtiqueta, RarezaEtiqueta, TipoRequisito, MetodoAdquisicion
)


# =============================================================================
# ETIQUETA PERFIL SCHEMAS
# =============================================================================

class EtiquetaPerfilBase(BaseModel):
    """Schema base para etiqueta de perfil."""
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    categoria: CategoriaEtiqueta
    rareza: RarezaEtiqueta
    icono_url: Optional[str] = Field(None, max_length=500)
    color_hex: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    animacion_url: Optional[str] = Field(None, max_length=500)
    precio_puntos: Optional[int] = Field(None, ge=0)
    es_comprable: bool = Field(default=True)
    requisito_logro: Optional[Dict[str, Any]] = None


class EtiquetaPerfilCreate(EtiquetaPerfilBase):
    """Schema para crear etiqueta."""
    etiqueta_evolucion_id: Optional[UUID] = None
    requisito_evolucion: Optional[Dict[str, Any]] = None


class EtiquetaPerfilUpdate(BaseModel):
    """Schema para actualizar etiqueta."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio_puntos: Optional[int] = Field(None, ge=0)
    es_activa: Optional[bool] = None
    icono_url: Optional[str] = Field(None, max_length=500)
    color_hex: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')


class EtiquetaPerfilResponse(EtiquetaPerfilBase):
    """Schema de respuesta para etiqueta."""
    etiqueta_id: UUID
    etiqueta_evolucion_id: Optional[UUID]
    requisito_evolucion: Optional[Dict[str, Any]]
    es_activa: bool
    orden: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    # Propiedades computadas
    puede_evolucionar: bool
    nivel_rareza_numerico: int

    class Config:
        from_attributes = True


class EtiquetaPerfilDetalle(EtiquetaPerfilResponse):
    """Schema detallado con información adicional."""
    usuarios_con_etiqueta: int = 0
    etiqueta_evolucion_nombre: Optional[str] = None


# =============================================================================
# USUARIO ETIQUETA SCHEMAS
# =============================================================================

class ComprarEtiquetaRequest(BaseModel):
    """Request para comprar una etiqueta."""
    etiqueta_id: UUID


class EquiparEtiquetasRequest(BaseModel):
    """Request para equipar etiquetas (máximo 5)."""
    etiquetas: List[UUID] = Field(..., min_length=0, max_length=5)
    
    @field_validator('etiquetas')
    @classmethod
    def validar_etiquetas_unicas(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('No se pueden equipar etiquetas duplicadas')
        return v


class EvolucionarEtiquetaRequest(BaseModel):
    """Request para evolucionar una etiqueta."""
    usuario_etiqueta_id: UUID


class UsuarioEtiquetaResponse(BaseModel):
    """Schema de respuesta para etiqueta del usuario."""
    usuario_etiqueta_id: UUID
    usuario_id: UUID
    etiqueta_id: UUID
    fecha_obtencion: datetime
    metodo_obtencion: MetodoAdquisicion
    precio_pagado: Optional[int]
    esta_equipada: bool
    orden_visualizacion: Optional[int]
    progreso_evolucion: Optional[Dict[str, Any]]
    veces_equipada: int
    
    # Información de la etiqueta
    etiqueta_nombre: str
    etiqueta_descripcion: Optional[str]
    etiqueta_categoria: CategoriaEtiqueta
    etiqueta_rareza: RarezaEtiqueta
    etiqueta_icono_url: Optional[str]
    etiqueta_color_hex: Optional[str]
    etiqueta_animacion_url: Optional[str]
    
    # Propiedades
    puede_evolucionar: bool
    progreso_evolucion_porcentaje: float = 0.0

    class Config:
        from_attributes = True


class UsuarioEtiquetaDetalle(UsuarioEtiquetaResponse):
    """Schema detallado con información de evolución."""
    etiqueta_evolucion_id: Optional[UUID] = None
    etiqueta_evolucion_nombre: Optional[str] = None
    requisito_evolucion: Optional[Dict[str, Any]] = None
    puede_evolucionar_ahora: bool = False


# =============================================================================
# RESPONSE SCHEMAS COMPUESTOS
# =============================================================================

class CatalogoEtiquetasResponse(BaseModel):
    """Response para catálogo de etiquetas."""
    etiquetas: List[EtiquetaPerfilResponse]
    total: int
    pagina: int
    items_por_pagina: int
    total_paginas: int


class MisEtiquetasResponse(BaseModel):
    """Response para etiquetas del usuario."""
    etiquetas: List[UsuarioEtiquetaDetalle]
    total_etiquetas: int
    etiquetas_equipadas: int
    etiquetas_por_rareza: Dict[str, int]
    etiquetas_por_categoria: Dict[str, int]


class ProgresoEvolucionResponse(BaseModel):
    """Response para progreso de evolución."""
    usuario_etiqueta_id: UUID
    etiqueta_actual_id: UUID
    etiqueta_actual_nombre: str
    etiqueta_evolucion_id: Optional[UUID]
    etiqueta_evolucion_nombre: Optional[str]
    puede_evolucionar: bool
    requisitos: List[Dict[str, Any]]
    progreso_general: float
    requisitos_completados: int
    requisitos_totales: int


class EvolucionResponse(BaseModel):
    """Response después de evolucionar."""
    success: bool
    message: str
    etiqueta_anterior: EtiquetaPerfilResponse
    etiqueta_nueva: EtiquetaPerfilResponse
    usuario_etiqueta: UsuarioEtiquetaResponse


class CompraEtiquetaResponse(BaseModel):
    """Response después de comprar etiqueta."""
    success: bool
    message: str
    usuario_etiqueta: UsuarioEtiquetaResponse
    puntos_restantes: int


class EquipamientoResponse(BaseModel):
    """Response después de equipar etiquetas."""
    success: bool
    message: str
    etiquetas_equipadas: List[UsuarioEtiquetaResponse]
    total_equipadas: int
