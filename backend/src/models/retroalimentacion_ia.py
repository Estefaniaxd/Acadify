"""
📚 Retroalimentación IA - Helper para trabajar con retroalimentaciones

IMPORTANTE: La BD ya tiene la columna retroalimentacion_ia en entregas_tareas (JSONB)
Este módulo proporciona helper functions para trabajar con esa estructura

Estructura de retroalimentacion_ia (JSONB):
{
    "retroalimentacion_texto": "Análisis detallado...",
    "fortalezas": ["Fortaleza 1", "Fortaleza 2"],
    "areas_mejora": ["Área 1", "Área 2"],
    "recursos_recomendados": ["Link 1", "Link 2"],
    "calificacion_sugerida": 8.5,
    "razonamiento_calificacion": "Justificación...",
    "modelo_usado": "gemini-2.5-flash",
    "nivel_profundidad": "completo",
    "tokens_usados": 1245,
    "confianza": 0.95,
    "metadata": {
        "tiempo_procesamiento": 3.2,
        "version_api": "1.0",
        "job_id": "uuid-aqui",
        "timestamp": "2025-11-16T10:30:00Z"
    }
}
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class RetroalimentacionIASchema(BaseModel):
    """Schema para validar retroalimentación IA generada por Gemini."""
    
    retroalimentacion_texto: str = Field(..., description="Retroalimentación completa")
    fortalezas: List[str] = Field(default_factory=list, description="Puntos fuertes")
    areas_mejora: List[str] = Field(default_factory=list, description="Áreas a mejorar")
    recursos_recomendados: List[str] = Field(
        default_factory=list, 
        description="URLs o recursos recomendados"
    )
    
    # Sugerencias
    calificacion_sugerida: Optional[float] = Field(None, description="Calificación 0-10")
    razonamiento_calificacion: Optional[str] = Field(None, description="Justificación")
    
    # Metadata
    modelo_usado: str = Field("gemini-2.5-flash", description="Modelo IA usado")
    nivel_profundidad: str = Field("completo", description="Nivel: básico, medio, completo")
    tokens_usados: int = Field(default=0, description="Tokens consumidos")
    confianza: float = Field(default=0.0, description="Confianza 0-1")
    
    # Metadata adicional
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Información adicional (timestamps, etc)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "retroalimentacion_texto": "El trabajo demuestra...",
                "fortalezas": ["Buena estructura", "Ejemplos claros"],
                "areas_mejora": ["Profundidad en análisis", "Citas bibliográficas"],
                "recursos_recomendados": ["https://example.com/articulo"],
                "calificacion_sugerida": 8.5,
                "modelo_usado": "gemini-2.5-flash",
                "tokens_usados": 1245
            }
        }


class RetroalimentacionIAResponse(BaseModel):
    """Response cuando se obtiene retroalimentación de una entrega."""
    
    entrega_id: str
    tarea_id: str
    retroalimentacion: Optional[RetroalimentacionIASchema] = None
    fecha_generacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Helper functions
def crear_retroalimentacion_dict(
    retroalimentacion_texto: str,
    fortalezas: List[str],
    areas_mejora: List[str],
    calificacion_sugerida: Optional[float] = None,
    modelo_usado: str = "gemini-2.5-flash",
    nivel_profundidad: str = "completo",
    tokens_usados: int = 0,
    recursos_recomendados: Optional[List[str]] = None,
    confianza: float = 0.95,
    job_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Crea un dict de retroalimentación IA para guardar en JSONB.
    
    Args:
        retroalimentacion_texto: Análisis principal
        fortalezas: Lista de puntos fuertes
        areas_mejora: Lista de áreas a mejorar
        calificacion_sugerida: Nota de 0-10
        modelo_usado: Modelo IA utilizado
        nivel_profundidad: Nivel de análisis
        tokens_usados: Tokens consumidos en API
        recursos_recomendados: URLs de recursos
        confianza: Confianza del modelo (0-1)
        job_id: ID del job si es bulk
    
    Returns:
        Dict listo para guardar en retroalimentacion_ia (JSONB)
    """
    return {
        "retroalimentacion_texto": retroalimentacion_texto,
        "fortalezas": fortalezas,
        "areas_mejora": areas_mejora,
        "recursos_recomendados": recursos_recomendados or [],
        "calificacion_sugerida": calificacion_sugerida,
        "razonamiento_calificacion": None,
        "modelo_usado": modelo_usado,
        "nivel_profundidad": nivel_profundidad,
        "tokens_usados": tokens_usados,
        "confianza": confianza,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "job_id": job_id,
            "version_api": "1.0"
        }
    }


def parsear_retroalimentacion(
    data: Optional[Dict[str, Any]]
) -> Optional[RetroalimentacionIASchema]:
    """
    Parsea datos JSONB de retroalimentacion_ia en Schema.
    
    Args:
        data: Datos JSONB de la columna retroalimentacion_ia
    
    Returns:
        RetroalimentacionIASchema validado o None
    """
    if not data:
        return None
    
    try:
        return RetroalimentacionIASchema(**data)
    except Exception as e:
        print(f"Error parseando retroalimentación: {e}")
        return None
