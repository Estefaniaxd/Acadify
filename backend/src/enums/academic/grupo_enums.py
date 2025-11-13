"""ENUMs para secciones/grupos de curso - VERSIÓN MEJORADA.

Define jornadas, estados, capacidades y configuraciones de secciones.
"""

import enum


class JornadaGrupo(str, enum.Enum):
    """Jornada/turno de la sección."""

    manana = "manana"  # Mañana
    tarde = "tarde"  # Tarde
    nocturna = "nocturna"  # Noche
    mixta = "mixta"  # Varias jornadas
    completa = "completa"  # TODO el día
    sabatina = "sabatina"  # Sábados
    dominical = "dominical"  # Domingos
    fin_semana = "fin_semana"  # Fines de semana
    especial = "especial"  # Horario especial


class EstadoGrupo(str, enum.Enum):
    """Estado del ciclo de vida de una sección."""

    programado = "programado"  # Creado pero no abierto
    inscripciones_abiertas = "inscripciones_abiertas"  # Acepta inscripciones
    cupos_disponibles = "cupos_disponibles"  # Con cupos
    lista_espera = "lista_espera"  # Solo lista de espera
    lleno = "lleno"  # Sin cupos ni espera
    confirmado = "confirmado"  # Confirmado para iniciar
    en_curso = "en_curso"  # Clases en marcha
    finalizado = "finalizado"  # Completado exitosamente
    cancelado = "cancelado"  # Cancelado (pocos inscritos)
    suspendido = "suspendido"  # Suspendido temporalmente
    cerrado = "cerrado"  # Cerrado (no acepta más)


class TipoGrupo(str, enum.Enum):
    """Tipo de sección según características especiales."""

    regular = "regular"  # Sección estándar
    intensivo = "intensivo"  # Curso intensivo/acelerado
    nivelacion = "nivelacion"  # Nivelación/preparación
    recuperacion = "recuperacion"  # Para estudiantes que repiten
    honores = "honores"  # Sección de honores/avanzada
    especial = "especial"  # Necesidades especiales
    virtual = "virtual"  # 100% virtual
    hibrido = "hibrido"  # Virtual + presencial
    presencial = "presencial"  # 100% presencial
    laboratorio = "laboratorio"  # Laboratorio específico
    practica = "practica"  # Práctica supervisada


class ModalidadAsistencia(str, enum.Enum):
    """Modalidad de asistencia requerida."""

    obligatoria = "obligatoria"  # Asistencia obligatoria
    flexible = "flexible"  # Flexible dentro de normas
    libre = "libre"  # Asistencia libre
    mixta = "mixta"  # Algunos obligatorios, otros no


class FormatoEvaluacion(str, enum.Enum):
    """Formato principal de evaluación."""

    examenes = "examenes"  # Exámenes tradicionales
    proyectos = "proyectos"  # Proyectos prácticos
    talleres = "talleres"  # Talleres y ejercicios
    participacion = "participacion"  # Participación activa
    mixto = "mixto"  # Combinación de varios
    continua = "continua"  # Evaluación continua
    portafolio = "portafolio"  # Portafolio de evidencias
