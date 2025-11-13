"""ENUMs para el sistema de períodos académicos.

Define los tipos y estados de períodos académicos que soporta la plataforma.
"""

import enum


class TipoPeriodo(str, enum.Enum):
    """Tipos de períodos académicos soportados
    Adaptable a cualquier institución educativa.
    """

    # Períodos universitarios estándar
    semestral = "semestral"  # 16-18 semanas (universidades)
    trimestral = "trimestral"  # 12 semanas
    cuatrimestral = "cuatrimestral"  # 16 semanas
    bimestral = "bimestral"  # 8 semanas

    # Períodos especiales
    mensual = "mensual"  # 4 semanas (cursos intensivos)
    modular = "modular"  # Bloques de 4-6 semanas
    anual = "anual"  # 40 semanas (colegios)

    # Períodos flexibles
    continuo = "continuo"  # Sin fecha fija (rolling admissions)
    intersemestral = "intersemestral"  # Verano/vacaciones
    intensivo = "intensivo"  # 2-4 semanas (bootcamps)


class EstadoPeriodo(str, enum.Enum):
    """Estados del ciclo de vida de un período académico."""

    programado = "programado"  # Creado pero no iniciado
    preinscripciones = "preinscripciones"  # Pre-inscripciones abiertas
    inscripciones_abiertas = "inscripciones_abiertas"  # Inscripciones regulares
    en_curso = "en_curso"  # Clases en progreso
    evaluaciones = "evaluaciones"  # Período de exámenes finales
    finalizado = "finalizado"  # Período completado
    cancelado = "cancelado"  # Período cancelado
