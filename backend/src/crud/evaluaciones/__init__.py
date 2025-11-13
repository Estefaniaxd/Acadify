"""CRUD operations para el sistema de evaluaciones.

NOTA: Módulos legacy comentados - en proceso de migración a Evaluacion
- crud_examen_LEGACY.py.bak (usar Evaluacion en su lugar)
- crud_pregunta_LEGACY.py.bak (usar PreguntaEvaluacion en su lugar)
- crud_intento_LEGACY.py.bak (usar IntentoEvaluacion en su lugar)
- crud_respuesta_LEGACY.py.bak (usa models legacy IntentoExamen, PreguntaExamen)
"""

# from .crud_examen import examen  # LEGACY - comentado
# from .crud_pregunta import pregunta_examen  # LEGACY - comentado
from .crud_banco_pregunta import banco_pregunta


# from .crud_intento import intento_examen  # LEGACY - comentado
# from .crud_respuesta import respuesta_estudiante  # LEGACY - comentado

__all__ = [
    # "examen",  # LEGACY
    # "pregunta_examen",  # LEGACY
    "banco_pregunta",
    # "intento_examen",  # LEGACY
    # "respuesta_estudiante"  # LEGACY
]
