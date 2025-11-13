"""ENUMs para cursos - VERSIÓN MEJORADA.

Define modalidades, niveles, categorías y estados de cursos.
"""

import enum


class ModalidadCurso(str, enum.Enum):
    """Modalidad de dictado del curso."""

    # Duración
    anual = "anual"  # Curso de todo el año
    semestral = "semestral"  # Un semestre
    trimestral = "trimestral"  # Un trimestre
    cuatrimestral = "cuatrimestral"  # Un cuatrimestre
    bimestral = "bimestral"  # Dos meses
    mensual = "mensual"  # Un mes
    modular = "modular"  # Por módulos
    flexible = "flexible"  # Sin duración fija
    intensivo = "intensivo"  # Curso intensivo corto
    otro = "otro"


class NivelDificultad(str, enum.Enum):
    """Nivel de dificultad del curso."""

    basico = "basico"  # Introductorio, sin requisitos
    intermedio = "intermedio"  # Conocimientos previos recomendados
    avanzado = "avanzado"  # Requiere dominio de fundamentos
    experto = "experto"  # Nivel profesional/especializado


class TipoCurso(str, enum.Enum):
    """Tipo de curso según su naturaleza."""

    teorico = "teorico"  # Solo teoría
    practico = "practico"  # Solo práctica/laboratorio
    teorico_practico = "teorico_practico"  # Combinado
    laboratorio = "laboratorio"  # Laboratorio específico
    taller = "taller"  # Taller práctico
    proyecto = "proyecto"  # Proyecto integrador
    seminario = "seminario"  # Seminario/discusión
    investigacion = "investigacion"  # Investigación
    practica_profesional = "practica_profesional"  # Práctica empresarial


class CategoriaCurso(str, enum.Enum):
    """Categoría curricular del curso."""

    obligatorio = "obligatorio"  # Curso obligatorio del programa
    fundamental = "fundamental"  # Fundamentación básica
    profesional = "profesional"  # Formación profesional específica
    electivo = "electivo"  # Electiva de programa
    libre = "libre"  # Libre elección
    nivelacion = "nivelacion"  # Curso de nivelación
    complementario = "complementario"  # Complementario al programa


class EstadoCurso(str, enum.Enum):
    """Estado del ciclo de vida de un curso."""

    borrador = "borrador"  # En creación
    programado = "programado"  # Programado para futuro período
    inscripciones_abiertas = "inscripciones_abiertas"  # Aceptando inscripciones
    proximo = "proximo"  # Próximo a iniciar
    en_curso = "en_curso"  # Actualmente dictándose
    finalizado = "finalizado"  # Curso terminado
    cancelado = "cancelado"  # Cancelado antes de iniciar
    suspendido = "suspendido"  # Suspendido temporalmente
    archivado = "archivado"  # Archivado (histórico)


class IdiomaCurso(str, enum.Enum):
    """Idioma principal del curso."""

    espanol = "español"
    ingles = "inglés"
    frances = "francés"
    aleman = "alemán"
    portugues = "portugués"
    italiano = "italiano"
    chino = "chino"
    japones = "japonés"
    otro = "otro"
