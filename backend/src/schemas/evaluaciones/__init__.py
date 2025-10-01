"""
Schemas Pydantic para el sistema de evaluaciones
"""

from .examen import (
    # Schemas de Examen
    ExamenBase,
    ExamenCreate,
    ExamenUpdate,
    ExamenResponse,
    ExamenCompleto,
    ExamenParaEstudiante,
    
    # Schemas de Pregunta
    PreguntaExamenBase,
    PreguntaExamenCreate,
    PreguntaExamenUpdate,
    PreguntaExamenResponse,
    PreguntaParaEstudiante,
    
    # Schemas de Banco de Preguntas
    BancoPreguntaBase,
    BancoPreguntaCreate,
    BancoPreguntaUpdate,
    BancoPreguntaResponse,
    
    # Schemas de Intento
    IntentoExamenBase,
    IntentoExamenCreate,
    IntentoExamenUpdate,
    IntentoExamenResponse,
    
    # Schemas de Respuesta
    RespuestaEstudianteBase,
    RespuestaEstudianteCreate,
    RespuestaEstudianteUpdate,
    RespuestaEstudianteResponse,
    
    # Schemas de Configuración y Estadísticas
    ConfiguracionEvaluacionesResponse,
    EstadisticaExamenResponse,
    
    # Schemas Combinados
    ResultadoExamen,
    FiltrosBancoPreguntas
)

__all__ = [
    # Schemas de Examen
    "ExamenBase",
    "ExamenCreate", 
    "ExamenUpdate",
    "ExamenResponse",
    "ExamenCompleto",
    "ExamenParaEstudiante",
    
    # Schemas de Pregunta
    "PreguntaExamenBase",
    "PreguntaExamenCreate",
    "PreguntaExamenUpdate", 
    "PreguntaExamenResponse",
    "PreguntaParaEstudiante",
    
    # Schemas de Banco de Preguntas
    "BancoPreguntaBase",
    "BancoPreguntaCreate",
    "BancoPreguntaUpdate",
    "BancoPreguntaResponse",
    
    # Schemas de Intento
    "IntentoExamenBase",
    "IntentoExamenCreate",
    "IntentoExamenUpdate",
    "IntentoExamenResponse",
    
    # Schemas de Respuesta
    "RespuestaEstudianteBase",
    "RespuestaEstudianteCreate",
    "RespuestaEstudianteUpdate",
    "RespuestaEstudianteResponse",
    
    # Schemas de Configuración y Estadísticas
    "ConfiguracionEvaluacionesResponse",
    "EstadisticaExamenResponse",
    
    # Schemas Combinados
    "ResultadoExamen",
    "FiltrosBancoPreguntas"
]