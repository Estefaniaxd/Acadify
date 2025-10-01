"""
Archivo de inicialización para los servicios de evaluaciones
"""

from .calificador import calificador_automatico, CalificadorAutomatico
from .anti_trampa import detector_anti_trampa, DetectorAntiTrampa
from .estadisticas import servicio_estadisticas, ServicioEstadisticas
from .integracion import servicio_integracion, ServicioIntegracionExamenes

__all__ = [
    "calificador_automatico",
    "CalificadorAutomatico",
    "detector_anti_trampa",
    "DetectorAntiTrampa",
    "servicio_estadisticas",
    "ServicioEstadisticas",
    "servicio_integracion",
    "ServicioIntegracionExamenes"
]