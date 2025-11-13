"""ENUMs para sistema de inscripciones.

Define estados, tipos y categorías de inscripciones.
"""

import enum


class EstadoInscripcion(str, enum.Enum):
    """Estado del proceso de inscripción."""

    # Pre-inscripción
    pre_inscrita = "pre_inscrita"  # Reserva de cupo

    # Pendientes
    pendiente_pago = "pendiente_pago"  # Falta pago
    pendiente_documentos = "pendiente_documentos"  # Falta documentación
    pendiente_aprobacion = "pendiente_aprobacion"  # Espera aprobación

    # En espera
    en_lista_espera = "en_lista_espera"  # Lista de espera

    # Aprobadas
    aprobada = "aprobada"  # Inscripción aprobada
    confirmada = "confirmada"  # Estudiante confirmó asistencia

    # Activas
    activa = "activa"  # Cursando actualmente

    # Finalizadas
    completada = "completada"  # Completada exitosamente
    aprobada_curso = "aprobada_curso"  # Aprobó el curso
    reprobada_curso = "reprobada_curso"  # Reprobó el curso

    # Rechazadas/Canceladas
    rechazada = "rechazada"  # Rechazada por institución
    rechazada_requisitos = "rechazada_requisitos"  # No cumple requisitos
    cancelada = "cancelada"  # Cancelada por estudiante
    retirada = "retirada"  # Retirada durante el curso
    expirada = "expirada"  # Venció plazo de confirmación


class TipoInscripcion(str, enum.Enum):
    """Tipo de inscripción según naturaleza."""

    regular = "regular"  # Inscripción normal
    primera_vez = "primera_vez"  # Primer ingreso a institución
    reingreso = "reingreso"  # Regreso después de ausencia

    # Especiales
    convalidacion = "convalidacion"  # Con convalidación de créditos
    homologacion = "homologacion"  # Con homologación
    validacion = "validacion"  # Validación de conocimientos

    # Modalidades
    oyente = "oyente"  # Como oyente (sin certificación)
    auditoria = "auditoria"  # Auditoría (sin calificación)

    # Repetición
    repeticion = "repeticion"  # Repite curso perdido
    refuerzo = "refuerzo"  # Refuerzo/nivelación

    # Períodos especiales
    intersemestral = "intersemestral"  # Período intersemestral
    verano = "verano"  # Curso de verano
    intensivo = "intensivo"  # Modalidad intensiva

    # Institucionales
    becado = "becado"  # Con beca
    intercambio = "intercambio"  # Estudiante de intercambio
    extension = "extension"  # Educación continua/extensión


class MotivoRechazo(str, enum.Enum):
    """Motivo de rechazo de inscripción."""

    cupos_llenos = "cupos_llenos"  # Sin cupos disponibles
    no_cumple_requisitos = "no_cumple_requisitos"  # Requisitos no cumplidos
    documentacion_incompleta = "documentacion_incompleta"  # Falta documentos
    pago_no_realizado = "pago_no_realizado"  # Falta pago
    fecha_vencida = "fecha_vencida"  # Fuera de plazo
    conflicto_horario = "conflicto_horario"  # Conflicto de horarios
    sancion_academica = "sancion_academica"  # Sanción vigente
    deuda_pendiente = "deuda_pendiente"  # Deuda financiera
    duplicada = "duplicada"  # Inscripción duplicada
    otro = "otro"  # Otro motivo


class MotivoRetiro(str, enum.Enum):
    """Motivo de retiro del curso."""

    personal = "personal"  # Motivos personales
    economico = "economico"  # Motivos económicos
    laboral = "laboral"  # Motivos laborales
    salud = "salud"  # Problemas de salud
    familiar = "familiar"  # Situación familiar
    academico = "academico"  # Dificultades académicas
    cambio_programa = "cambio_programa"  # Cambió de programa
    traslado = "traslado"  # Traslado a otra institución
    insatisfaccion = "insatisfaccion"  # Insatisfacción con el curso
    conflicto_horario = "conflicto_horario"  # Conflicto de horarios
    otro = "otro"  # Otro motivo


class FormaPago(str, enum.Enum):
    """Forma de pago de la inscripción."""

    contado = "contado"  # Pago de contado
    cuotas = "cuotas"  # Pago en cuotas
    credito_educativo = "credito_educativo"  # Crédito educativo
    beca_completa = "beca_completa"  # Beca 100%
    beca_parcial = "beca_parcial"  # Beca parcial
    empresa = "empresa"  # Paga empresa
    gratuito = "gratuito"  # Sin costo
    otro = "otro"  # Otra forma
