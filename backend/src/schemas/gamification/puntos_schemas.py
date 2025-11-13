"""
Schemas de validación para el módulo de Puntos.

Este módulo define los modelos Pydantic para:
- Respuestas de información de puntos
- Niveles y progreso
- Rankings y posiciones
- Historial de puntos
- Insignias básicas

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
Version: 1.0.0
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from .common import BaseResponse, PaginationParams


# =============================================================================
# INFORMACIÓN DE NIVELES
# =============================================================================

class NivelInfo(BaseModel):
    """
    Información detallada del nivel actual del usuario.
    
    Attributes:
        nivel_actual: Nombre del nivel (ej: "Oro II")
        puntos_minimos_nivel: Puntos mínimos para este nivel
        puntos_siguiente_nivel: Puntos necesarios para siguiente nivel (None si es máximo)
        progreso_porcentaje: Porcentaje de progreso hacia siguiente nivel (0-100)
        puntos_para_siguiente: Puntos que faltan para subir de nivel
    
    Example:
        >>> nivel = NivelInfo(
        ...     nivel_actual="Plata III",
        ...     puntos_minimos_nivel=1200,
        ...     puntos_siguiente_nivel=2000,
        ...     progreso_porcentaje=62.5,
        ...     puntos_para_siguiente=500
        ... )
    """
    nivel_actual: str = Field(
        ...,
        description="Nombre del nivel actual",
        example="Oro II"
    )
    puntos_minimos_nivel: int = Field(
        ...,
        ge=0,
        description="Puntos mínimos requeridos para este nivel"
    )
    puntos_siguiente_nivel: Optional[int] = Field(
        None,
        ge=0,
        description="Puntos necesarios para el siguiente nivel (None si es nivel máximo)"
    )
    progreso_porcentaje: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Porcentaje de progreso hacia el siguiente nivel"
    )
    puntos_para_siguiente: int = Field(
        ...,
        ge=0,
        description="Puntos que faltan para alcanzar el siguiente nivel"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "nivel_actual": "Plata III",
                "puntos_minimos_nivel": 1200,
                "puntos_siguiente_nivel": 2000,
                "progreso_porcentaje": 62.5,
                "puntos_para_siguiente": 500
            }
        }


# =============================================================================
# INSIGNIAS
# =============================================================================

class InsigniaBasica(BaseModel):
    """
    Información básica de una insignia obtenida.
    
    Attributes:
        insignia_id: UUID de la insignia
        nombre: Nombre de la insignia
        descripcion: Descripción de cómo se obtiene
        imagen_url: URL de la imagen de la insignia
        tipo: Tipo de insignia (logro, milestone, especial)
    
    Example:
        >>> insignia = InsigniaBasica(
        ...     insignia_id="123e4567-e89b-12d3-a456-426614174000",
        ...     nombre="Estudiante Dedicado",
        ...     descripcion="Alcanzaste 500 puntos",
        ...     imagen_url="/assets/insignias/estudiante_dedicado.png",
        ...     tipo="logro"
        ... )
    """
    insignia_id: str = Field(
        ...,
        description="UUID de la insignia"
    )
    nombre: str = Field(
        ...,
        max_length=100,
        description="Nombre de la insignia"
    )
    descripcion: str = Field(
        ...,
        max_length=500,
        description="Descripción de cómo se obtiene la insignia"
    )
    imagen_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL de la imagen de la insignia"
    )
    tipo: str = Field(
        ...,
        description="Tipo de insignia"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "insignia_id": "123e4567-e89b-12d3-a456-426614174000",
                "nombre": "Estudiante Dedicado",
                "descripcion": "Alcanzaste 500 puntos totales",
                "imagen_url": "/assets/insignias/estudiante_dedicado.png",
                "tipo": "logro"
            }
        }


# =============================================================================
# HISTORIAL DE PUNTOS
# =============================================================================

class HistorialPuntoItem(BaseModel):
    """
    Item individual del historial de puntos.
    
    Attributes:
        cambio: Cantidad de puntos (positivo = ganado, negativo = gastado)
        motivo: Razón del cambio de puntos
        fecha: Timestamp del cambio
    
    Example:
        >>> item = HistorialPuntoItem(
        ...     cambio=70,
        ...     motivo="Tarea Python - Ejercicio 1",
        ...     fecha=datetime.now()
        ... )
    """
    cambio: int = Field(
        ...,
        description="Cantidad de puntos (positivo = ganado, negativo = gastado)"
    )
    motivo: str = Field(
        ...,
        max_length=500,
        description="Razón del cambio de puntos"
    )
    fecha: datetime = Field(
        ...,
        description="Fecha y hora del cambio"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "cambio": 70,
                "motivo": "Tarea Python - Ejercicio 1",
                "fecha": "2025-11-02T14:30:00Z"
            }
        }


# =============================================================================
# RESPUESTA COMPLETA DE PUNTOS
# =============================================================================

class PuntosCompletoResponse(BaseModel):
    """
    Respuesta completa con toda la información de puntos del usuario.
    
    Incluye puntos acumulados, nivel actual con progreso, historial reciente
    y todas las insignias obtenidas.
    
    Attributes:
        puntos_acumulados: Total de puntos del usuario
        nivel: Nombre del nivel actual (string corto)
        nivel_info: Información detallada del nivel
        historial_reciente: Últimos 10 movimientos de puntos
        insignias: Lista de insignias obtenidas
    
    Example:
        >>> response = PuntosCompletoResponse(
        ...     puntos_acumulados=1250,
        ...     nivel="Plata III",
        ...     nivel_info=NivelInfo(...),
        ...     historial_reciente=[...],
        ...     insignias=[...]
        ... )
    """
    puntos_acumulados: int = Field(
        ...,
        ge=0,
        description="Total de puntos acumulados del usuario"
    )
    nivel: str = Field(
        ...,
        description="Nombre del nivel actual (string corto)"
    )
    nivel_info: NivelInfo = Field(
        ...,
        description="Información detallada del nivel y progreso"
    )
    historial_reciente: List[HistorialPuntoItem] = Field(
        default=[],
        description="Últimos 10 movimientos de puntos"
    )
    insignias: List[InsigniaBasica] = Field(
        default=[],
        description="Lista de insignias obtenidas por el usuario"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "puntos_acumulados": 1250,
                "nivel": "Plata III",
                "nivel_info": {
                    "nivel_actual": "Plata III",
                    "puntos_minimos_nivel": 1200,
                    "puntos_siguiente_nivel": 2000,
                    "progreso_porcentaje": 62.5,
                    "puntos_para_siguiente": 500
                },
                "historial_reciente": [
                    {
                        "cambio": 70,
                        "motivo": "Tarea Python - Ejercicio 1",
                        "fecha": "2025-11-02T14:30:00Z"
                    },
                    {
                        "cambio": -300,
                        "motivo": "Compra: Marco Dorado",
                        "fecha": "2025-11-02T10:15:00Z"
                    }
                ],
                "insignias": [
                    {
                        "insignia_id": "123e4567-e89b-12d3-a456-426614174000",
                        "nombre": "Estudiante Dedicado",
                        "descripcion": "Alcanzaste 500 puntos",
                        "imagen_url": "/assets/insignias/estudiante_dedicado.png",
                        "tipo": "logro"
                    }
                ]
            }
        }


# =============================================================================
# RANKING
# =============================================================================

class RankingUsuarioItem(BaseModel):
    """
    Item individual en el ranking de usuarios.
    
    Attributes:
        posicion: Posición en el ranking (1 = primero)
        usuario_id: UUID del usuario
        nombre_completo: Nombre completo del usuario (opcional por privacidad)
        puntos: Puntos acumulados del usuario
        nivel: Nivel actual del usuario
    
    Example:
        >>> item = RankingUsuarioItem(
        ...     posicion=5,
        ...     usuario_id="123e4567-e89b-12d3-a456-426614174000",
        ...     nombre_completo="Juan Pérez",
        ...     puntos=2500,
        ...     nivel="Oro I"
        ... )
    """
    posicion: int = Field(
        ...,
        ge=1,
        description="Posición en el ranking (1 = primero)"
    )
    usuario_id: str = Field(
        ...,
        description="UUID del usuario"
    )
    nombre_completo: Optional[str] = Field(
        None,
        description="Nombre completo del usuario (puede ser None por privacidad)"
    )
    puntos: int = Field(
        ...,
        ge=0,
        description="Puntos acumulados del usuario"
    )
    nivel: str = Field(
        ...,
        description="Nivel actual del usuario"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "posicion": 5,
                "usuario_id": "123e4567-e89b-12d3-a456-426614174000",
                "nombre_completo": "Juan Pérez",
                "puntos": 2500,
                "nivel": "Oro I"
            }
        }


class RankingResponse(BaseModel):
    """
    Respuesta completa del ranking con paginación.
    
    Attributes:
        success: Indica si la operación fue exitosa
        data: Lista de usuarios en el ranking
        total: Total de usuarios en el ranking
        limit: Cantidad de resultados por página
        offset: Offset actual de la paginación
    
    Example:
        >>> response = RankingResponse(
        ...     success=True,
        ...     data=[...],
        ...     total=150,
        ...     limit=10,
        ...     offset=0
        ... )
    """
    success: bool = Field(
        default=True,
        description="Indica si la operación fue exitosa"
    )
    data: List[RankingUsuarioItem] = Field(
        ...,
        description="Lista de usuarios en el ranking"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total de usuarios en el ranking completo"
    )
    limit: int = Field(
        ...,
        ge=1,
        le=200,
        description="Cantidad de resultados por página"
    )
    offset: int = Field(
        ...,
        ge=0,
        description="Offset actual de la paginación"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [
                    {
                        "posicion": 1,
                        "usuario_id": "123e4567-e89b-12d3-a456-426614174000",
                        "nombre_completo": "María García",
                        "puntos": 5000,
                        "nivel": "Platino I"
                    },
                    {
                        "posicion": 2,
                        "usuario_id": "223e4567-e89b-12d3-a456-426614174000",
                        "nombre_completo": "Carlos López",
                        "puntos": 4500,
                        "nivel": "Oro III"
                    }
                ],
                "total": 150,
                "limit": 10,
                "offset": 0
            }
        }


# =============================================================================
# POSICIÓN EN RANKING
# =============================================================================

class PosicionRankingResponse(BaseModel):
    """
    Información de la posición del usuario en el ranking.
    
    Attributes:
        posicion: Posición actual en el ranking (None si no tiene puntos)
        puntos: Puntos acumulados del usuario
        nivel: Nivel actual del usuario
        puntos_hasta_anterior: Puntos que faltan para alcanzar al usuario anterior
        puntos_hasta_siguiente: Ventaja de puntos sobre el usuario siguiente
        total_usuarios: Total de usuarios en el ranking
    
    Example:
        >>> response = PosicionRankingResponse(
        ...     posicion=25,
        ...     puntos=1500,
        ...     nivel="Plata III",
        ...     puntos_hasta_anterior=200,
        ...     puntos_hasta_siguiente=150,
        ...     total_usuarios=200
        ... )
    """
    posicion: Optional[int] = Field(
        None,
        ge=1,
        description="Posición en el ranking (None si no tiene puntos)"
    )
    puntos: int = Field(
        ...,
        ge=0,
        description="Puntos acumulados del usuario"
    )
    nivel: str = Field(
        ...,
        description="Nivel actual del usuario"
    )
    puntos_hasta_anterior: Optional[int] = Field(
        None,
        ge=0,
        description="Puntos que faltan para alcanzar al usuario en la posición anterior"
    )
    puntos_hasta_siguiente: Optional[int] = Field(
        None,
        ge=0,
        description="Ventaja de puntos sobre el usuario en la posición siguiente"
    )
    total_usuarios: int = Field(
        ...,
        ge=0,
        description="Total de usuarios en el ranking"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "posicion": 25,
                "puntos": 1500,
                "nivel": "Plata III",
                "puntos_hasta_anterior": 200,
                "puntos_hasta_siguiente": 150,
                "total_usuarios": 200
            }
        }


# =============================================================================
# OTORGAMIENTO DE PUNTOS (ADMIN)
# =============================================================================

class OtorgarPuntosRequest(BaseModel):
    """
    Request para otorgar puntos a un usuario (solo admin).
    
    Attributes:
        usuario_id: UUID del usuario que recibirá los puntos
        puntos: Cantidad de puntos a otorgar (puede ser negativo para penalización)
        motivo: Razón por la cual se otorgan/quitan los puntos
    
    Example:
        >>> request = OtorgarPuntosRequest(
        ...     usuario_id="123e4567-e89b-12d3-a456-426614174000",
        ...     puntos=100,
        ...     motivo="Corrección manual - error en sistema"
        ... )
    """
    usuario_id: UUID = Field(
        ...,
        description="UUID del usuario que recibirá los puntos"
    )
    puntos: int = Field(
        ...,
        description="Cantidad de puntos (positivo = otorgar, negativo = quitar)"
    )
    motivo: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Razón del otorgamiento/penalización"
    )
    
    @validator('puntos')
    def puntos_no_cero(cls, v):
        if v == 0:
            raise ValueError('Los puntos deben ser diferentes de cero')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "usuario_id": "123e4567-e89b-12d3-a456-426614174000",
                "puntos": 100,
                "motivo": "Corrección manual - error en sistema"
            }
        }


class OtorgarPuntosResponse(BaseResponse):
    """
    Respuesta al otorgar puntos a un usuario.
    
    Attributes:
        puntos_otorgados: Cantidad de puntos otorgados
        puntos_anteriores: Puntos antes del otorgamiento
        puntos_acumulados: Puntos totales después del otorgamiento
        nuevas_insignias: Lista de insignias desbloqueadas (si aplica)
        nivel_actual: Nivel después del otorgamiento
    
    Example:
        >>> response = OtorgarPuntosResponse(
        ...     success=True,
        ...     message="Puntos otorgados exitosamente",
        ...     puntos_otorgados=100,
        ...     puntos_anteriores=900,
        ...     puntos_acumulados=1000,
        ...     nuevas_insignias=[...],
        ...     nivel_actual="Plata I"
        ... )
    """
    puntos_otorgados: int = Field(
        ...,
        description="Cantidad de puntos otorgados"
    )
    puntos_anteriores: int = Field(
        ...,
        ge=0,
        description="Puntos antes del otorgamiento"
    )
    puntos_acumulados: int = Field(
        ...,
        ge=0,
        description="Puntos totales después del otorgamiento"
    )
    nuevas_insignias: List[InsigniaBasica] = Field(
        default=[],
        description="Insignias desbloqueadas con este otorgamiento"
    )
    nivel_actual: str = Field(
        ...,
        description="Nivel del usuario después del otorgamiento"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "100 puntos otorgados exitosamente",
                "puntos_otorgados": 100,
                "puntos_anteriores": 900,
                "puntos_acumulados": 1000,
                "nuevas_insignias": [
                    {
                        "insignia_id": "123e4567-e89b-12d3-a456-426614174000",
                        "nombre": "Explorador del Conocimiento",
                        "descripcion": "Alcanzaste 1000 puntos",
                        "imagen_url": "/assets/insignias/explorador.png",
                        "tipo": "logro"
                    }
                ],
                "nivel_actual": "Plata I"
            }
        }
