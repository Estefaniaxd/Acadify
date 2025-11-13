"""Archivo de inicialización para los servicios de evaluaciones."""

from .anti_trampa import DetectorAntiTrampa, detector_anti_trampa
from .calificador import CalificadorAutomatico, calificador_automatico
from .estadisticas import ServicioEstadisticas, servicio_estadisticas
from .integracion import ServicioIntegracionExamenes, servicio_integracion


__all__ = [
    "CalificadorAutomatico",
    "DetectorAntiTrampa",
    "ServicioEstadisticas",
    "ServicioIntegracionExamenes",
    "calificador_automatico",
    "detector_anti_trampa",
    "servicio_estadisticas",
    "servicio_integracion",
]
