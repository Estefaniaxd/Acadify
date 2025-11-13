"""
Schemas Pydantic para IA y Gamificación.

Estos schemas definen la estructura de datos para:
- Entregas de tareas con IA
- Retroalimentación de IA
- Puntos y gamificación
- Validaciones automáticas

Author: GitHub Copilot & Team
Date: 31 octubre 2025
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, ConfigDict
from datetime import datetime
from uuid import UUID


# ==================== ENTREGAS CON IA ====================

class ArchivoMetadata(BaseModel):
    """Metadata de archivo adjunto."""
    
    nombre: str = Field(..., description="Nombre del archivo")
    mime_type: str = Field(..., description="Tipo MIME (ej: application/pdf)")
    tamaño_bytes: int = Field(..., gt=0, description="Tamaño en bytes")
    url: Optional[str] = Field(None, description="URL del archivo almacenado")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "tarea_python.py",
                "mime_type": "text/x-python",
                "tamaño_bytes": 2048,
                "url": "https://storage.example.com/archivos/abc123.py"
            }
        }
    )


class EntregarTareaRequest(BaseModel):
    """Request para entregar una tarea con análisis de IA."""
    
    contenido_texto: Optional[str] = Field(
        None,
        max_length=50000,
        description="Contenido texto de la entrega (si no hay archivo)"
    )
    archivo_metadata: Optional[ArchivoMetadata] = Field(
        None,
        description="Metadata del archivo adjunto"
    )
    
    @validator('contenido_texto')
    def validar_contenido_no_vacio(cls, v):
        """Valida que el contenido no esté vacío si se proporciona."""
        if v is not None and not v.strip():
            raise ValueError("El contenido no puede estar vacío")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "contenido_texto": "def calcular_promedio(lista):\n    return sum(lista) / len(lista)",
                "archivo_metadata": {
                    "nombre": "tarea.py",
                    "mime_type": "text/x-python",
                    "tamaño_bytes": 1024
                }
            }
        }
    )


# ==================== RETROALIMENTACIÓN DE IA ====================

class SugerenciaEspecifica(BaseModel):
    """Una sugerencia específica de mejora."""
    
    ubicacion: str = Field(..., description="Ubicación del problema (línea, sección)")
    problema: str = Field(..., description="Descripción del problema")
    sugerencia: str = Field(..., description="Cómo mejorarlo")
    ejemplo: Optional[str] = Field(None, description="Código o texto de ejemplo")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ubicacion": "Línea 2",
                "problema": "No valida lista vacía",
                "sugerencia": "Agregar validación antes de dividir",
                "ejemplo": "if not lista:\n    raise ValueError('Lista vacía')"
            }
        }
    )


class CriterioRubrica(BaseModel):
    """Evaluación de un criterio de la rúbrica."""
    
    puntos: float = Field(..., ge=0, le=5, description="Puntos obtenidos (0-5)")
    comentario: str = Field(..., description="Comentario sobre el criterio")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "puntos": 4.5,
                "comentario": "Excelente funcionalidad, código claro y bien estructurado"
            }
        }
    )


class RetroalimentacionIA(BaseModel):
    """Retroalimentación completa generada por IA."""
    
    analisis_general: str = Field(..., description="Análisis general del trabajo")
    fortalezas: List[str] = Field(..., description="Aspectos positivos encontrados")
    areas_mejora: List[str] = Field(..., description="Áreas que necesitan mejora")
    sugerencias_especificas: List[SugerenciaEspecifica] = Field(
        ...,
        description="Sugerencias detalladas con ubicación"
    )
    nivel_cumplimiento: str = Field(..., description="Porcentaje de cumplimiento")
    cumple_rubrica: Optional[Dict[str, CriterioRubrica]] = Field(
        None,
        description="Evaluación por criterios de rúbrica"
    )
    puntos_clave_missing: List[str] = Field(
        default=[],
        description="Conceptos o puntos clave faltantes"
    )
    calificacion: float = Field(..., ge=0, le=5, description="Calificación IA (0-5)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "analisis_general": "Código funcional y bien estructurado con oportunidades de mejora en validación",
                "fortalezas": [
                    "Uso correcto de funciones built-in",
                    "Nombres descriptivos"
                ],
                "areas_mejora": [
                    "Falta manejo de casos límite",
                    "Sin type hints"
                ],
                "sugerencias_especificas": [
                    {
                        "ubicacion": "Línea 2",
                        "problema": "División por cero si lista vacía",
                        "sugerencia": "Agregar validación",
                        "ejemplo": "if not lista: raise ValueError()"
                    }
                ],
                "nivel_cumplimiento": "85%",
                "cumple_rubrica": {
                    "funcionalidad": {
                        "puntos": 4.5,
                        "comentario": "Funciona correctamente"
                    }
                },
                "puntos_clave_missing": ["Validación de entrada"],
                "calificacion": 4.2
            }
        }
    )


# ==================== PUNTOS Y GAMIFICACIÓN ====================

class PuntosDesglose(BaseModel):
    """Desglose detallado del cálculo de puntos."""
    
    puntos_base: int = Field(..., description="Puntos base de la tarea")
    puntos_bonificacion: int = Field(..., description="Bonus por excelencia")
    penalizacion_tardia: int = Field(..., description="Penalización por entrega tardía")
    penalizacion_intentos: int = Field(..., description="Penalización por intentos extra")
    puntos_totales: int = Field(..., description="Total de puntos otorgados")
    desglose: str = Field(..., description="Explicación textual del cálculo")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "puntos_base": 50,
                "puntos_bonificacion": 20,
                "penalizacion_tardia": 0,
                "penalizacion_intentos": 0,
                "puntos_totales": 70,
                "desglose": "50 (base) + 20 (bonus excelencia)"
            }
        }
    )


class InsigniaInfo(BaseModel):
    """Información de una insignia."""
    
    insignia_id: str = Field(..., description="ID de la insignia")
    nombre: str = Field(..., description="Nombre de la insignia")
    descripcion: Optional[str] = Field(None, description="Descripción")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen")
    fecha_obtencion: Optional[datetime] = Field(None, description="Cuándo se obtuvo")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "insignia_id": "uuid-123",
                "nombre": "Novato",
                "descripcion": "Primera insignia del sistema",
                "imagen_url": "https://cdn.example.com/insignias/novato.png",
                "fecha_obtencion": "2025-10-31T10:30:00Z"
            }
        }
    )


class GamificacionInfo(BaseModel):
    """Información de gamificación del usuario."""
    
    puntos_otorgados: int = Field(..., description="Puntos otorgados en esta acción")
    puntos_acumulados: int = Field(..., description="Total de puntos del usuario")
    nivel_actual: str = Field(..., description="Nivel actual (ej: Bronce II)")
    nuevas_insignias: List[InsigniaInfo] = Field(
        default=[],
        description="Insignias nuevas desbloqueadas"
    )
    progreso_siguiente_nivel: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Porcentaje de progreso al siguiente nivel"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "puntos_otorgados": 70,
                "puntos_acumulados": 170,
                "nivel_actual": "Bronce II",
                "nuevas_insignias": [
                    {
                        "insignia_id": "uuid-123",
                        "nombre": "Novato",
                        "descripcion": "Primera insignia",
                        "imagen_url": "https://cdn.example.com/novato.png"
                    }
                ],
                "progreso_siguiente_nivel": 68.0
            }
        }
    )


# ==================== RESPONSE COMPLETO ====================

class EntregaConIAResponse(BaseModel):
    """Response completo de entrega procesada con IA."""
    
    success: bool = Field(..., description="Si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    data: "EntregaConIAData" = Field(..., description="Datos de la entrega")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Entrega procesada exitosamente con IA",
                "data": {
                    "entrega_id": "uuid-abc-123",
                    "intentos": 1,
                    "es_tardia": False,
                    "retroalimentacion_ia": {
                        "analisis_general": "Excelente trabajo",
                        "fortalezas": ["Código claro", "Bien documentado"],
                        "areas_mejora": ["Validaciones faltantes"],
                        "calificacion": 4.5
                    },
                    "puntos": {
                        "puntos_totales": 70,
                        "desglose": "50 (base) + 20 (bonus)"
                    },
                    "gamificacion": {
                        "puntos_otorgados": 70,
                        "puntos_acumulados": 170,
                        "nivel_actual": "Bronce II"
                    }
                }
            }
        }
    )


class EntregaConIAData(BaseModel):
    """Datos de una entrega procesada con IA."""
    
    entrega_id: str = Field(..., description="ID de la entrega")
    intentos: int = Field(..., description="Número de intentos")
    es_tardia: bool = Field(..., description="Si fue entregada tarde")
    fecha_entrega: Optional[datetime] = Field(None, description="Fecha de entrega")
    retroalimentacion_ia: RetroalimentacionIA = Field(..., description="Retroalimentación de IA")
    puntos: PuntosDesglose = Field(..., description="Desglose de puntos")
    gamificacion: GamificacionInfo = Field(..., description="Info de gamificación")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entrega_id": "uuid-abc-123",
                "intentos": 1,
                "es_tardia": False,
                "fecha_entrega": "2025-10-31T10:30:00Z",
                "retroalimentacion_ia": {
                    "calificacion": 4.5
                },
                "puntos": {
                    "puntos_totales": 70
                },
                "gamificacion": {
                    "puntos_otorgados": 70,
                    "nivel_actual": "Bronce II"
                }
            }
        }
    )


# ==================== PUNTOS USUARIO ====================

class HistorialPuntoItem(BaseModel):
    """Un item del historial de puntos."""
    
    cambio: int = Field(..., description="Cambio de puntos (+ o -)")
    motivo: str = Field(..., description="Motivo del cambio")
    fecha: datetime = Field(..., description="Fecha del cambio")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cambio": 70,
                "motivo": "Tarea: Introducción a Python",
                "fecha": "2025-10-31T10:30:00Z"
            }
        }
    )


class NivelInfo(BaseModel):
    """Información detallada del nivel actual."""
    
    nivel_actual: str = Field(..., description="Nivel actual (ej: Bronce II)")
    puntos_minimos_nivel: int = Field(..., description="Puntos mínimos del nivel")
    puntos_siguiente_nivel: Optional[int] = Field(
        None,
        description="Puntos para siguiente nivel"
    )
    progreso_porcentaje: float = Field(..., ge=0, le=100, description="Progreso %")
    puntos_para_siguiente: int = Field(..., description="Puntos faltantes")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nivel_actual": "Bronce II",
                "puntos_minimos_nivel": 100,
                "puntos_siguiente_nivel": 250,
                "progreso_porcentaje": 46.7,
                "puntos_para_siguiente": 80
            }
        }
    )


class PuntosUsuarioResponse(BaseModel):
    """Response con información completa de puntos de un usuario."""
    
    success: bool = Field(..., description="Si la operación fue exitosa")
    data: "PuntosUsuarioData" = Field(..., description="Datos de puntos")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": {
                    "puntos_acumulados": 170,
                    "nivel": "Bronce II",
                    "nivel_info": {
                        "nivel_actual": "Bronce II",
                        "progreso_porcentaje": 46.7
                    },
                    "historial_reciente": [
                        {
                            "cambio": 70,
                            "motivo": "Tarea: Introducción a Python",
                            "fecha": "2025-10-31T10:30:00Z"
                        }
                    ],
                    "insignias": []
                }
            }
        }
    )


class PuntosUsuarioData(BaseModel):
    """Datos completos de puntos de un usuario."""
    
    puntos_acumulados: int = Field(..., description="Total de puntos")
    nivel: str = Field(..., description="Nivel actual")
    nivel_info: NivelInfo = Field(..., description="Información detallada del nivel")
    historial_reciente: List[HistorialPuntoItem] = Field(
        ...,
        description="Últimos 10 cambios de puntos"
    )
    insignias: List[InsigniaInfo] = Field(..., description="Insignias obtenidas")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "puntos_acumulados": 170,
                "nivel": "Bronce II",
                "nivel_info": {
                    "nivel_actual": "Bronce II",
                    "progreso_porcentaje": 46.7
                },
                "historial_reciente": [],
                "insignias": []
            }
        }
    )


# ==================== RANKING ====================

class UsuarioRankingItem(BaseModel):
    """Un usuario en el ranking."""
    
    posicion: int = Field(..., ge=1, description="Posición en el ranking")
    usuario_id: str = Field(..., description="ID del usuario")
    nombre_completo: Optional[str] = Field(None, description="Nombre completo")
    puntos: int = Field(..., description="Puntos totales")
    nivel: str = Field(..., description="Nivel actual")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "posicion": 1,
                "usuario_id": "uuid-123",
                "nombre_completo": "Juan Pérez",
                "puntos": 5420,
                "nivel": "Platino I"
            }
        }
    )


class RankingResponse(BaseModel):
    """Response con el ranking de usuarios."""
    
    success: bool = Field(..., description="Si la operación fue exitosa")
    data: List[UsuarioRankingItem] = Field(..., description="Lista del ranking")
    total: int = Field(..., description="Total de usuarios en el ranking")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": [
                    {
                        "posicion": 1,
                        "usuario_id": "uuid-1",
                        "nombre_completo": "Juan Pérez",
                        "puntos": 5420,
                        "nivel": "Platino I"
                    },
                    {
                        "posicion": 2,
                        "usuario_id": "uuid-2",
                        "nombre_completo": "María García",
                        "puntos": 3890,
                        "nivel": "Oro II"
                    }
                ],
                "total": 2
            }
        }
    )


# Actualizar forward references
EntregaConIAResponse.model_rebuild()
PuntosUsuarioResponse.model_rebuild()
