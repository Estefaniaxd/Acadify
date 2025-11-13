"""Módulo de modelos para el sistema de evaluaciones.

Versión 2.0: Sincronizado con BD (2025-11-04)
- Sistema NUEVO: Evaluacion, PreguntaEvaluacion, IntentoEvaluacion
- Tablas reales: evaluaciones, preguntas_evaluacion, intentos_evaluacion

Principios SOLID aplicados:
- Single Responsibility: Cada modelo una responsabilidad clara
- Open/Closed: Extensible mediante herencia
- Liskov Substitution: Interfaces consistentes
- Interface Segregation: Propiedades y métodos cohesivos
- Dependency Inversion: Relaciones mediante ORM
"""

from .evaluacion_expandida import Evaluacion, PreguntaEvaluacion

# Importar enums y configuraciones necesarias de examen.py
from .examen import (
    BancoPregunta,
    ConfiguracionEvaluaciones,
    DificultadPregunta,
    EstadisticaExamen,
    EstadoExamen,
    EstadoIntento,
    EventoAntiTrampa,
    TipoEvento,
    TipoExamen,
    TipoPregunta,
)
# NOTA: Modelos deprecated de examen.py - usar Evaluacion en su lugar
# Temporalmente exportados para compatibilidad con servicios legacy
from .examen import Examen, IntentoExamen, PreguntaExamen
from .intento_respuesta_gamificacion import IntentoEvaluacion, RespuestaEstudiante
from .evento_audio import EventoAudio


__all__ = [
    "BancoPregunta",
    "ConfiguracionEvaluaciones",
    "DificultadPregunta",
    "EstadisticaExamen",
    "EstadoExamen",
    "EstadoIntento",
    "Evaluacion",
    "EventoAntiTrampa",
    "EventoAudio",
    "Examen",  # Deprecated pero necesario para servicios legacy
    "IntentoEvaluacion",
    "IntentoExamen",  # Deprecated pero necesario para servicios legacy
    "PreguntaEvaluacion",
    "PreguntaExamen",  # Deprecated pero necesario para servicios legacy
    "RespuestaEstudiante",
    "TipoEvento",
    "TipoExamen",
    "TipoPregunta",
]
