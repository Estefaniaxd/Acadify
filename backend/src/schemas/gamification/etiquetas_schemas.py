"""
Schemas de validación para el módulo de Etiquetas.

Este módulo define los modelos Pydantic para:
- Catálogo de etiquetas
- Compra de etiquetas
- Equipamiento (máximo 5)
- Sistema de evolución
- Estadísticas de etiquetas

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
Version: 1.0.0
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

from .common import BaseResponse, PaginationParams


# =============================================================================
# ENUMS
# =============================================================================

class CategoriaEtiqueta(str, Enum):
    """Categorías temáticas de etiquetas."""
    # Académicas
    MATEMATICAS = "matematicas"
    CIENCIAS = "ciencias"
    PROGRAMACION = "programacion"
    IDIOMAS = "idiomas"
    LITERATURA = "literatura"
    HISTORIA = "historia"
    ARTE = "arte"
    MUSICA = "musica"
    # Habilidades
    LECTURA = "lectura"
    ESCRITURA = "escritura"
    INVESTIGACION = "investigacion"
    PENSAMIENTO_CRITICO = "pensamiento_critico"
    CREATIVIDAD = "creatividad"
    LIDERAZGO = "liderazgo"
    # Logros
    LOGRO_TAREAS = "logro_tareas"
    LOGRO_EXAMENES = "logro_examenes"
    PARTICIPACION = "participacion"
    COLABORACION = "colaboracion"
    # Especiales
    RACHA = "racha"
    RANKING = "ranking"
    EVENTO = "evento"
    ESPECIAL = "especial"


class RarezaEtiqueta(str, Enum):
    """Niveles de rareza de etiquetas."""
    COMUN = "comun"
    RARO = "raro"
    EPICO = "epico"
    LEGENDARIO = "legendario"


# =============================================================================
# ETIQUETA BASE
# =============================================================================

class EtiquetaBase(BaseModel):
    """
    Información básica de una etiqueta.
    
    Attributes:
        etiqueta_id: UUID de la etiqueta
        nombre: Nombre de la etiqueta
        descripcion: Descripción detallada
        categoria: Categoría temática
        rareza: Nivel de rareza
        icono_url: URL del icono
        color_hex: Color en formato hexadecimal (#RRGGBB)
    """
    etiqueta_id: str = Field(..., description="UUID de la etiqueta")
    nombre: str = Field(..., max_length=100, description="Nombre de la etiqueta")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción")
    categoria: CategoriaEtiqueta = Field(..., description="Categoría temática")
    rareza: RarezaEtiqueta = Field(..., description="Nivel de rareza")
    icono_url: Optional[str] = Field(None, description="URL del icono")
    color_hex: Optional[str] = Field(None, description="Color hexadecimal")
    
    class Config:
        json_schema_extra = {
            "example": {
                "etiqueta_id": "123e4567-e89b-12d3-a456-426614174000",
                "nombre": "Python Master",
                "descripcion": "Completaste 50 tareas de Python",
                "categoria": "programacion",
                "rareza": "epico",
                "icono_url": "/assets/etiquetas/python_master.png",
                "color_hex": "#3776AB"
            }
        }


# =============================================================================
# CATÁLOGO
# =============================================================================

class EtiquetaCatalogo(EtiquetaBase):
    """
    Etiqueta del catálogo con información de compra.
    
    Extends EtiquetaBase con:
        precio_puntos: Costo en puntos (None si no es comprable)
        es_comprable: Si se puede comprar o es solo por logro
        requisito_logro: Requisitos para obtenerla (si no es comprable)
        puede_evolucionar: Si tiene evolución disponible
        etiqueta_evolucion_id: ID de la siguiente evolución
    """
    precio_puntos: Optional[int] = Field(None, ge=0, description="Precio en puntos")
    es_comprable: bool = Field(..., description="Si es comprable")
    requisito_logro: Optional[dict] = Field(None, description="Requisitos para obtener")
    puede_evolucionar: bool = Field(default=False, description="Tiene evolución")
    etiqueta_evolucion_id: Optional[str] = Field(None, description="ID evolución")
    fecha_creacion: Optional[datetime] = Field(None, description="Fecha de creación")
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "etiqueta_id": "123e4567-e89b-12d3-a456-426614174000",
                "nombre": "Python Master",
                "descripcion": "Completaste 50 tareas de Python",
                "categoria": "programacion",
                "rareza": "epico",
                "icono_url": "/assets/etiquetas/python_master.png",
                "color_hex": "#3776AB",
                "precio_puntos": 800,
                "es_comprable": True,
                "requisito_logro": None,
                "puede_evolucionar": True,
                "etiqueta_evolucion_id": "223e4567-e89b-12d3-a456-426614174000",
                "fecha_creacion": "2025-11-02T10:00:00Z"
            }
        }


class CatalogoEtiquetasResponse(BaseModel):
    """
    Respuesta del catálogo de etiquetas con paginación.
    
    Attributes:
        etiquetas: Lista de etiquetas del catálogo
        total: Total de etiquetas que cumplen los filtros
        filtros_aplicados: Resumen de filtros aplicados
    """
    etiquetas: List[EtiquetaCatalogo] = Field(..., description="Lista de etiquetas")
    total: int = Field(..., ge=0, description="Total de etiquetas")
    filtros_aplicados: dict = Field(default={}, description="Filtros aplicados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "etiquetas": [
                    {
                        "etiqueta_id": "123e4567-e89b-12d3-a456-426614174000",
                        "nombre": "Python Master",
                        "categoria": "programacion",
                        "rareza": "epico",
                        "precio_puntos": 800,
                        "es_comprable": True
                    }
                ],
                "total": 45,
                "filtros_aplicados": {
                    "categoria": "programacion",
                    "rareza": "epico"
                }
            }
        }


# =============================================================================
# COMPRA
# =============================================================================

class CompraEtiquetaRequest(BaseModel):
    """Request para comprar una etiqueta (sin body, solo path param)."""
    pass


class CompraEtiquetaResponse(BaseResponse):
    """
    Respuesta al comprar una etiqueta.
    
    Attributes:
        etiqueta: Información de la etiqueta comprada
        puntos_gastados: Puntos que costó
        puntos_restantes: Puntos que quedan
    """
    etiqueta: EtiquetaBase = Field(..., description="Etiqueta comprada")
    puntos_gastados: int = Field(..., ge=0, description="Puntos gastados")
    puntos_restantes: int = Field(..., ge=0, description="Puntos restantes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "¡Etiqueta 'Python Master' adquirida!",
                "etiqueta": {
                    "etiqueta_id": "123e4567-e89b-12d3-a456-426614174000",
                    "nombre": "Python Master",
                    "categoria": "programacion",
                    "rareza": "epico"
                },
                "puntos_gastados": 800,
                "puntos_restantes": 1200
            }
        }


# =============================================================================
# ETIQUETAS DEL USUARIO
# =============================================================================

class UsuarioEtiquetaDetalle(BaseModel):
    """
    Etiqueta en posesión del usuario con detalles de adquisición.
    
    Attributes:
        usuario_etiqueta_id: UUID del registro
        etiqueta: Información completa de la etiqueta
        esta_equipada: Si está visible en el perfil
        orden_visualizacion: Orden en perfil (1-5)
        fecha_obtencion: Cuándo la obtuvo
        metodo_obtencion: Cómo la obtuvo (compra, logro, etc)
        veces_equipada: Contador de veces equipada
        progreso_evolucion: Progreso hacia evolución
    """
    usuario_etiqueta_id: str = Field(..., description="UUID del registro")
    etiqueta: EtiquetaBase = Field(..., description="Info de la etiqueta")
    esta_equipada: bool = Field(..., description="Si está equipada")
    orden_visualizacion: int = Field(..., ge=0, le=5, description="Orden en perfil")
    fecha_obtencion: datetime = Field(..., description="Fecha de obtención")
    metodo_obtencion: str = Field(..., description="Método de obtención")
    veces_equipada: int = Field(..., ge=0, description="Contador de uso")
    progreso_evolucion: Optional[dict] = Field(None, description="Progreso evolución")
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "usuario_etiqueta_id": "323e4567-e89b-12d3-a456-426614174000",
                "etiqueta": {
                    "etiqueta_id": "123e4567-e89b-12d3-a456-426614174000",
                    "nombre": "Python Master",
                    "categoria": "programacion",
                    "rareza": "epico"
                },
                "esta_equipada": True,
                "orden_visualizacion": 1,
                "fecha_obtencion": "2025-10-15T14:30:00Z",
                "metodo_obtencion": "compra",
                "veces_equipada": 15,
                "progreso_evolucion": {
                    "tareas_completadas": 45,
                    "tareas_requeridas": 50
                }
            }
        }


class MisEtiquetasResponse(BaseModel):
    """
    Respuesta con todas las etiquetas del usuario.
    
    Attributes:
        etiquetas: Lista de etiquetas del usuario
        total: Total de etiquetas
        equipadas: Cantidad de etiquetas equipadas
    """
    etiquetas: List[UsuarioEtiquetaDetalle] = Field(..., description="Etiquetas")
    total: int = Field(..., ge=0, description="Total de etiquetas")
    equipadas: int = Field(..., ge=0, le=5, description="Cantidad equipadas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "etiquetas": [
                    {
                        "usuario_etiqueta_id": "323e4567-e89b-12d3-a456-426614174000",
                        "etiqueta": {"nombre": "Python Master", "rareza": "epico"},
                        "esta_equipada": True,
                        "orden_visualizacion": 1
                    }
                ],
                "total": 12,
                "equipadas": 3
            }
        }


# =============================================================================
# EQUIPAMIENTO
# =============================================================================

class EquiparEtiquetasRequest(BaseModel):
    """
    Request para equipar etiquetas (máximo 5).
    
    Attributes:
        etiquetas_ids: Lista de UUIDs ordenados (posición 1-5)
    """
    etiquetas_ids: List[UUID] = Field(
        ...,
        min_items=0,
        max_items=5,
        description="Lista de etiquetas a equipar (orden = visualización)"
    )
    
    @validator('etiquetas_ids')
    def validar_cantidad(cls, v):
        if len(v) > 5:
            raise ValueError('Máximo 5 etiquetas permitidas')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "etiquetas_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "223e4567-e89b-12d3-a456-426614174000",
                    "323e4567-e89b-12d3-a456-426614174000"
                ]
            }
        }


class EtiquetaEquipadaInfo(BaseModel):
    """Info de etiqueta equipada con orden."""
    orden: int = Field(..., ge=1, le=5, description="Orden de visualización")
    nombre: str = Field(..., description="Nombre de la etiqueta")
    rareza: RarezaEtiqueta = Field(..., description="Rareza")
    icono_url: Optional[str] = Field(None, description="URL del icono")


class EquiparEtiquetasResponse(BaseResponse):
    """
    Respuesta al equipar etiquetas.
    
    Attributes:
        etiquetas_equipadas: Cantidad equipada
        orden: Lista con orden de visualización
    """
    etiquetas_equipadas: int = Field(..., ge=0, le=5, description="Cantidad equipada")
    orden: List[EtiquetaEquipadaInfo] = Field(..., description="Orden de etiquetas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "¡3 etiquetas equipadas!",
                "etiquetas_equipadas": 3,
                "orden": [
                    {"orden": 1, "nombre": "Python Master", "rareza": "epico"},
                    {"orden": 2, "nombre": "Racha 30 Días", "rareza": "legendario"},
                    {"orden": 3, "nombre": "Top 10", "rareza": "raro"}
                ]
            }
        }


# =============================================================================
# EVOLUCIÓN
# =============================================================================

class EvolucionDisponibleResponse(BaseModel):
    """
    Información sobre evolución disponible.
    
    Attributes:
        puede_evolucionar: Si tiene evolución disponible
        requisitos_cumplidos: Si cumple los requisitos
        etiqueta_actual: Info de la etiqueta actual
        etiqueta_evolucion: Info de la evolución
        requisitos: Requisitos necesarios
        progreso: Progreso actual del usuario
    """
    puede_evolucionar: bool = Field(..., description="Tiene evolución")
    requisitos_cumplidos: bool = Field(..., description="Cumple requisitos")
    etiqueta_actual: EtiquetaBase = Field(..., description="Etiqueta actual")
    etiqueta_evolucion: Optional[EtiquetaBase] = Field(None, description="Evolución")
    requisitos: dict = Field(default={}, description="Requisitos necesarios")
    progreso: dict = Field(default={}, description="Progreso actual")
    
    class Config:
        json_schema_extra = {
            "example": {
                "puede_evolucionar": True,
                "requisitos_cumplidos": True,
                "etiqueta_actual": {
                    "nombre": "Matemático Novato",
                    "rareza": "comun"
                },
                "etiqueta_evolucion": {
                    "nombre": "Matemático Experto",
                    "rareza": "raro"
                },
                "requisitos": {
                    "tareas_completadas": 20,
                    "puntos_minimos": 500
                },
                "progreso": {
                    "tareas_completadas": {"actual": 25, "requerido": 20},
                    "puntos_minimos": {"actual": 800, "requerido": 500}
                }
            }
        }


class EvolucionResponse(BaseResponse):
    """
    Respuesta al evolucionar una etiqueta.
    
    Attributes:
        etiqueta_anterior: Info de la etiqueta antes de evolucionar
        etiqueta_nueva: Info de la nueva etiqueta evolucionada
    """
    etiqueta_anterior: EtiquetaBase = Field(..., description="Etiqueta anterior")
    etiqueta_nueva: EtiquetaBase = Field(..., description="Etiqueta nueva")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "¡'Matemático Novato' evolucionó a 'Matemático Experto'!",
                "etiqueta_anterior": {
                    "nombre": "Matemático Novato",
                    "rareza": "comun"
                },
                "etiqueta_nueva": {
                    "nombre": "Matemático Experto",
                    "rareza": "raro"
                }
            }
        }


# =============================================================================
# ESTADÍSTICAS
# =============================================================================

class EstadisticasEtiquetasResponse(BaseModel):
    """
    Estadísticas de etiquetas del usuario.
    
    Attributes:
        total_etiquetas: Total de etiquetas del usuario
        etiquetas_equipadas: Cantidad equipadas actualmente
        por_metodo: Distribución por método de obtención
        por_rareza: Distribución por rareza
        por_categoria: Distribución por categoría
    """
    total_etiquetas: int = Field(..., ge=0, description="Total de etiquetas")
    etiquetas_equipadas: int = Field(..., ge=0, le=5, description="Equipadas")
    por_metodo: dict = Field(default={}, description="Por método obtención")
    por_rareza: dict = Field(default={}, description="Por rareza")
    por_categoria: dict = Field(default={}, description="Por categoría")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_etiquetas": 25,
                "etiquetas_equipadas": 5,
                "por_metodo": {
                    "compra": 15,
                    "logro": 8,
                    "evolucion": 2
                },
                "por_rareza": {
                    "comun": 10,
                    "raro": 8,
                    "epico": 5,
                    "legendario": 2
                },
                "por_categoria": {
                    "programacion": 10,
                    "matematicas": 8,
                    "logro_tareas": 7
                }
            }
        }
