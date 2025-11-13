"""ENUMs para sistema de horarios.

Define días, tipos de sesión y configuraciones de horarios.
"""

import enum


class DiaSemana(int, enum.Enum):
    """Días de la semana (int para facilitar ordenamiento)."""

    lunes = 1
    martes = 2
    miercoles = 3
    jueves = 4
    viernes = 5
    sabado = 6
    domingo = 7


class TipoSesion(str, enum.Enum):
    """Tipo de sesión/clase."""

    # Académicas
    teorica = "teorica"  # Clase teórica magistral
    practica = "practica"  # Práctica/ejercicios
    teorico_practica = "teorico_practica"  # Combinada

    # Especiales
    laboratorio = "laboratorio"  # Laboratorio
    taller = "taller"  # Taller práctico
    seminario = "seminario"  # Seminario/discusión
    tutoria = "tutoria"  # Tutoría/asesoría
    proyecto = "proyecto"  # Trabajo en proyecto

    # Evaluativas
    examen = "examen"  # Examen
    parcial = "parcial"  # Parcial
    quiz = "quiz"  # Quiz/prueba corta
    presentacion = "presentacion"  # Presentación de trabajos
    evaluacion = "evaluacion"  # Evaluación general

    # Complementarias
    conferencia = "conferencia"  # Conferencia invitado
    visita = "visita"  # Visita técnica/empresarial
    campo = "campo"  # Trabajo de campo
    evento = "evento"  # Evento especial

    # Virtuales
    sincronica = "sincronica"  # Sesión virtual en tiempo real
    asincronica = "asincronica"  # Contenido asincrónico
    hibrida = "hibrida"  # Parte presencial, parte virtual


class ModalidadSesion(str, enum.Enum):
    """Modalidad de realización de la sesión."""

    presencial = "presencial"  # Presencial en aula
    virtual = "virtual"  # 100% virtual
    hibrida = "hibrida"  # Presencial + virtual simultáneo
    flexible = "flexible"  # Estudiante elige modalidad


class EstadoSesion(str, enum.Enum):
    """Estado de una sesión programada."""

    programada = "programada"  # Programada normalmente
    confirmada = "confirmada"  # Confirmada para realizarse
    en_curso = "en_curso"  # En desarrollo ahora
    realizada = "realizada"  # Ya realizada
    cancelada = "cancelada"  # Cancelada
    reprogramada = "reprogramada"  # Movida a otro horario
    suspendida = "suspendida"  # Suspendida temporalmente


class TipoRecurrencia(str, enum.Enum):
    """Tipo de recurrencia del horario."""

    semanal = "semanal"  # Se repite cada semana
    quincenal = "quincenal"  # Cada dos semanas
    mensual = "mensual"  # Cada mes
    unica = "unica"  # Sesión única
    personalizado = "personalizado"  # Patrón personalizado


class TipoAula(str, enum.Enum):
    """Tipo de aula/espacio físico."""

    aula_estandar = "aula_estandar"  # Aula estándar
    aula_magna = "aula_magna"  # Auditorio/aula magna
    laboratorio_computo = "laboratorio_computo"  # Lab de computación
    laboratorio_ciencias = "laboratorio_ciencias"  # Lab de ciencias
    laboratorio_idiomas = "laboratorio_idiomas"  # Lab de idiomas
    taller = "taller"  # Taller
    biblioteca = "biblioteca"  # Sala de biblioteca
    sala_conferencias = "sala_conferencias"  # Sala de conferencias
    gimnasio = "gimnasio"  # Gimnasio/deportes
    virtual = "virtual"  # Sala virtual
    externo = "externo"  # Espacio externo a institución
    campo = "campo"  # Campo/exterior
