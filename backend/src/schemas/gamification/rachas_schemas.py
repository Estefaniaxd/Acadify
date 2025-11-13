"""
Schemas de validación para el módulo de Rachas (Streaks).

Este módulo define los modelos Pydantic para:
- Sistema de rachas diarias (estilo Duolingo)
- Verificación de actividad
- Sistema de congelación
- Recompensas por milestones
- Recuperación de rachas
- Estadísticas y logros

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
Version: 1.0.0
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime, date
from enum import Enum

from .common import BaseResponse


# =============================================================================
# ENUMS
# =============================================================================

class TipoRacha(str, Enum):
    """Tipos de rachas disponibles."""
    DIARIA = "diaria"
    SEMANAL = "semanal"
    MENSUAL = "mensual"
    PERSONALIZADA = "personalizada"


class EstadoRacha(str, Enum):
    """Estados de una racha."""
    ACTIVA = "activa"
    CONGELADA = "congelada"
    ROTA = "rota"
    RECUPERABLE = "recuperable"


# =============================================================================
# RACHA ACTUAL
# =============================================================================

class RachaActual(BaseModel):
    """
    Información de la racha actual del usuario.
    
    Attributes:
        racha_id: UUID de la racha
        dias_actuales: Días consecutivos actuales
        dias_maximos: Récord personal de días
        tipo_racha: Tipo de racha
        estado: Estado actual
        ultima_actividad: Última fecha con actividad
        proxima_verificacion: Próxima fecha requerida
        esta_en_riesgo: Si está en riesgo de perderse
        esta_congelada: Si tiene protección activa
        congelaciones_disponibles: Protecciones restantes
        puede_recuperar: Si puede recuperar racha
    """
    racha_id: str = Field(..., description="UUID de la racha")
    dias_actuales: int = Field(..., ge=0, description="Días consecutivos actuales")
    dias_maximos: int = Field(..., ge=0, description="Récord personal")
    tipo_racha: TipoRacha = Field(..., description="Tipo de racha")
    estado: EstadoRacha = Field(..., description="Estado actual")
    ultima_actividad: date = Field(..., description="Última actividad")
    proxima_verificacion: date = Field(..., description="Próxima verificación")
    esta_en_riesgo: bool = Field(..., description="En riesgo de perderse")
    esta_congelada: bool = Field(..., description="Con protección activa")
    congelaciones_disponibles: int = Field(..., ge=0, description="Protecciones restantes")
    puede_recuperar: bool = Field(..., description="Puede recuperar")
    
    class Config:
        json_encoders = {date: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "racha_id": "123e4567-e89b-12d3-a456-426614174000",
                "dias_actuales": 15,
                "dias_maximos": 45,
                "tipo_racha": "diaria",
                "estado": "activa",
                "ultima_actividad": "2025-11-02",
                "proxima_verificacion": "2025-11-03",
                "esta_en_riesgo": False,
                "esta_congelada": False,
                "congelaciones_disponibles": 3,
                "puede_recuperar": False
            }
        }


class ObtenerRachaResponse(BaseModel):
    """
    Respuesta con información completa de la racha.
    
    Attributes:
        racha: Información de la racha
        mensaje_motivacional: Mensaje de ánimo
        proximo_milestone: Próximo hito a alcanzar
    """
    racha: RachaActual = Field(..., description="Info de la racha")
    mensaje_motivacional: str = Field(..., description="Mensaje motivacional")
    proximo_milestone: Optional[dict] = Field(None, description="Próximo hito")
    
    class Config:
        json_schema_extra = {
            "example": {
                "racha": {
                    "dias_actuales": 15,
                    "dias_maximos": 45,
                    "estado": "activa"
                },
                "mensaje_motivacional": "¡Vas genial! Ya llevas 15 días seguidos 🔥",
                "proximo_milestone": {
                    "dias": 30,
                    "recompensa": "Racha de 30 Días",
                    "puntos": 500,
                    "faltan": 15
                }
            }
        }


# =============================================================================
# VERIFICACIÓN
# =============================================================================

class VerificarRachaRequest(BaseModel):
    """
    Request para verificar actividad diaria.
    
    Attributes:
        actividad_completada: Descripción de la actividad
        puntos_ganados: Puntos ganados en el día
    """
    actividad_completada: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Descripción de la actividad"
    )
    puntos_ganados: int = Field(..., ge=0, description="Puntos ganados hoy")
    
    class Config:
        json_schema_extra = {
            "example": {
                "actividad_completada": "Completé 3 tareas y 1 examen",
                "puntos_ganados": 350
            }
        }


class VerificarRachaResponse(BaseResponse):
    """
    Respuesta al verificar la racha.
    
    Attributes:
        racha_actual: Días consecutivos ahora
        es_nuevo_record: Si superó su récord
        milestone_alcanzado: Si alcanzó un hito
        recompensa: Recompensa obtenida (si aplica)
        mensaje_motivacional: Mensaje de ánimo
    """
    racha_actual: int = Field(..., ge=0, description="Días consecutivos")
    es_nuevo_record: bool = Field(..., description="Nuevo récord personal")
    milestone_alcanzado: bool = Field(..., description="Alcanzó hito")
    recompensa: Optional[dict] = Field(None, description="Recompensa obtenida")
    mensaje_motivacional: str = Field(..., description="Mensaje motivacional")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "¡Racha verificada! 🔥",
                "racha_actual": 30,
                "es_nuevo_record": False,
                "milestone_alcanzado": True,
                "recompensa": {
                    "nombre": "Racha de 30 Días",
                    "puntos": 500,
                    "etiqueta": "Constante Dedicado"
                },
                "mensaje_motivacional": "¡30 días seguidos! Eres imparable 🚀"
            }
        }


# =============================================================================
# CONGELACIÓN
# =============================================================================

class CongelarRachaRequest(BaseModel):
    """
    Request para usar protección de racha.
    
    Attributes:
        dias_proteccion: Días de protección (1-7)
        usar_item: Si usar item del inventario
    """
    dias_proteccion: int = Field(
        ...,
        ge=1,
        le=7,
        description="Días de protección"
    )
    usar_item: bool = Field(
        default=False,
        description="Usar item del inventario"
    )
    
    @validator('dias_proteccion')
    def validar_dias(cls, v):
        if v < 1 or v > 7:
            raise ValueError('Protección debe ser entre 1 y 7 días')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "dias_proteccion": 3,
                "usar_item": True
            }
        }


class CongelarRachaResponse(BaseResponse):
    """
    Respuesta al congelar la racha.
    
    Attributes:
        dias_protegidos: Días de protección aplicados
        fecha_fin_proteccion: Hasta cuándo está protegida
        congelaciones_restantes: Protecciones que quedan
        metodo: Cómo se aplicó (item/compra)
    """
    dias_protegidos: int = Field(..., ge=1, le=7, description="Días protegidos")
    fecha_fin_proteccion: date = Field(..., description="Fin de protección")
    congelaciones_restantes: int = Field(..., ge=0, description="Restantes")
    metodo: str = Field(..., description="Método usado")
    
    class Config:
        json_encoders = {date: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "¡Racha congelada por 3 días! ❄️",
                "dias_protegidos": 3,
                "fecha_fin_proteccion": "2025-11-05",
                "congelaciones_restantes": 2,
                "metodo": "item_inventario"
            }
        }


# =============================================================================
# RECUPERACIÓN
# =============================================================================

class RecuperarRachaRequest(BaseModel):
    """Request para recuperar racha (sin body, verificación automática)."""
    pass


class RecuperarRachaResponse(BaseResponse):
    """
    Respuesta al recuperar la racha.
    
    Attributes:
        racha_recuperada: Días recuperados
        puntos_gastados: Puntos utilizados
        puntos_restantes: Puntos que quedan
    """
    racha_recuperada: int = Field(..., ge=0, description="Días recuperados")
    puntos_gastados: int = Field(..., ge=0, description="Puntos gastados")
    puntos_restantes: int = Field(..., ge=0, description="Puntos restantes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "¡Racha de 25 días recuperada! 💪",
                "racha_recuperada": 25,
                "puntos_gastados": 500,
                "puntos_restantes": 1500
            }
        }


# =============================================================================
# MILESTONES
# =============================================================================

class MilestoneRacha(BaseModel):
    """
    Milestone de racha con recompensa.
    
    Attributes:
        milestone_dias: Días requeridos
        nombre: Nombre del milestone
        descripcion: Descripción
        puntos_otorgados: Puntos de recompensa
        etiqueta: Etiqueta otorgada (opcional)
        alcanzado: Si el usuario lo alcanzó
        fecha_alcanzado: Cuándo lo alcanzó
    """
    milestone_dias: int = Field(..., ge=1, description="Días requeridos")
    nombre: str = Field(..., description="Nombre del milestone")
    descripcion: Optional[str] = Field(None, description="Descripción")
    puntos_otorgados: int = Field(..., ge=0, description="Puntos de recompensa")
    etiqueta: Optional[str] = Field(None, description="Etiqueta otorgada")
    alcanzado: bool = Field(..., description="Si fue alcanzado")
    fecha_alcanzado: Optional[datetime] = Field(None, description="Fecha alcanzado")
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "milestone_dias": 30,
                "nombre": "Racha de 30 Días",
                "descripcion": "Mantén tu racha por 30 días consecutivos",
                "puntos_otorgados": 500,
                "etiqueta": "Constante Dedicado",
                "alcanzado": True,
                "fecha_alcanzado": "2025-10-15T18:30:00Z"
            }
        }


class MilestonesResponse(BaseModel):
    """
    Respuesta con todos los milestones.
    
    Attributes:
        milestones: Lista de milestones
        total_alcanzados: Cantidad alcanzada
        proximo_milestone: Próximo hito
    """
    milestones: List[MilestoneRacha] = Field(..., description="Lista de milestones")
    total_alcanzados: int = Field(..., ge=0, description="Total alcanzados")
    proximo_milestone: Optional[MilestoneRacha] = Field(None, description="Próximo hito")
    
    class Config:
        json_schema_extra = {
            "example": {
                "milestones": [
                    {
                        "milestone_dias": 7,
                        "nombre": "Primera Semana",
                        "puntos_otorgados": 100,
                        "alcanzado": True
                    },
                    {
                        "milestone_dias": 30,
                        "nombre": "Racha de 30 Días",
                        "puntos_otorgados": 500,
                        "alcanzado": False
                    }
                ],
                "total_alcanzados": 3,
                "proximo_milestone": {
                    "milestone_dias": 30,
                    "nombre": "Racha de 30 Días",
                    "puntos_otorgados": 500
                }
            }
        }


# =============================================================================
# HISTORIAL
# =============================================================================

class HistorialRachaItem(BaseModel):
    """
    Entrada del historial de rachas.
    
    Attributes:
        fecha: Fecha del evento
        tipo_evento: Tipo de evento
        dias_racha: Días de racha en ese momento
        descripcion: Descripción del evento
        recompensa: Recompensa obtenida (si aplica)
    """
    fecha: datetime = Field(..., description="Fecha del evento")
    tipo_evento: str = Field(..., description="Tipo de evento")
    dias_racha: int = Field(..., ge=0, description="Días de racha")
    descripcion: str = Field(..., description="Descripción")
    recompensa: Optional[dict] = Field(None, description="Recompensa")
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "fecha": "2025-11-02T16:30:00Z",
                "tipo_evento": "verificacion",
                "dias_racha": 15,
                "descripcion": "Verificaste tu actividad del día",
                "recompensa": None
            }
        }


class HistorialRachaResponse(BaseModel):
    """
    Respuesta con historial de la racha.
    
    Attributes:
        historial: Lista de eventos
        total_eventos: Total de eventos
    """
    historial: List[HistorialRachaItem] = Field(..., description="Eventos")
    total_eventos: int = Field(..., ge=0, description="Total de eventos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "historial": [
                    {
                        "fecha": "2025-11-02T16:30:00Z",
                        "tipo_evento": "verificacion",
                        "dias_racha": 15,
                        "descripcion": "Verificaste tu actividad"
                    },
                    {
                        "fecha": "2025-10-20T10:00:00Z",
                        "tipo_evento": "milestone",
                        "dias_racha": 7,
                        "descripcion": "¡Alcanzaste 7 días!",
                        "recompensa": {"puntos": 100}
                    }
                ],
                "total_eventos": 25
            }
        }


# =============================================================================
# ESTADÍSTICAS
# =============================================================================

class EstadisticasRachaResponse(BaseModel):
    """
    Estadísticas completas de rachas del usuario.
    
    Attributes:
        racha_actual: Días consecutivos actuales
        racha_maxima: Récord personal
        total_dias_activos: Total de días con actividad
        milestones_alcanzados: Hitos completados
        puntos_ganados_rachas: Puntos totales por rachas
        veces_recuperada: Veces que recuperó racha
        veces_congelada: Veces que usó protección
        promedio_dias_racha: Promedio de días por racha
    """
    racha_actual: int = Field(..., ge=0, description="Racha actual")
    racha_maxima: int = Field(..., ge=0, description="Récord personal")
    total_dias_activos: int = Field(..., ge=0, description="Total días activos")
    milestones_alcanzados: int = Field(..., ge=0, description="Hitos alcanzados")
    puntos_ganados_rachas: int = Field(..., ge=0, description="Puntos por rachas")
    veces_recuperada: int = Field(..., ge=0, description="Recuperaciones")
    veces_congelada: int = Field(..., ge=0, description="Congelaciones")
    promedio_dias_racha: float = Field(..., ge=0, description="Promedio días")
    
    class Config:
        json_schema_extra = {
            "example": {
                "racha_actual": 15,
                "racha_maxima": 45,
                "total_dias_activos": 120,
                "milestones_alcanzados": 5,
                "puntos_ganados_rachas": 2500,
                "veces_recuperada": 2,
                "veces_congelada": 5,
                "promedio_dias_racha": 18.5
            }
        }


# =============================================================================
# RANKING DE RACHAS
# =============================================================================

class RankingRachaItem(BaseModel):
    """
    Item del ranking de rachas.
    
    Attributes:
        posicion: Posición en el ranking
        usuario_id: UUID del usuario
        nombre_completo: Nombre del usuario
        dias_racha: Días consecutivos
        racha_maxima: Récord del usuario
    """
    posicion: int = Field(..., ge=1, description="Posición")
    usuario_id: str = Field(..., description="UUID usuario")
    nombre_completo: Optional[str] = Field(None, description="Nombre")
    dias_racha: int = Field(..., ge=0, description="Días racha")
    racha_maxima: int = Field(..., ge=0, description="Récord")
    
    class Config:
        json_schema_extra = {
            "example": {
                "posicion": 1,
                "usuario_id": "223e4567-e89b-12d3-a456-426614174000",
                "nombre_completo": "Ana García",
                "dias_racha": 87,
                "racha_maxima": 120
            }
        }


class RankingRachasResponse(BaseModel):
    """
    Respuesta con ranking de rachas.
    
    Attributes:
        ranking: Lista ordenada de usuarios
        total: Total de usuarios en ranking
        mi_posicion: Posición del usuario actual
    """
    ranking: List[RankingRachaItem] = Field(..., description="Ranking")
    total: int = Field(..., ge=0, description="Total usuarios")
    mi_posicion: Optional[int] = Field(None, ge=1, description="Mi posición")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ranking": [
                    {
                        "posicion": 1,
                        "nombre_completo": "Ana García",
                        "dias_racha": 87
                    },
                    {
                        "posicion": 2,
                        "nombre_completo": "Carlos López",
                        "dias_racha": 65
                    }
                ],
                "total": 150,
                "mi_posicion": 15
            }
        }
