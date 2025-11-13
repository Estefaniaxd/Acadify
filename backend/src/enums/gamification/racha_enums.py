"""
Enums para el sistema de rachas.

Este módulo define los tipos de eventos y milestones relacionados
con el sistema de rachas diarias estilo Duolingo.

Author: GitHub Copilot & Team
Date: 31 de octubre de 2025
Version: 1.0.0
"""

import enum


class TipoEventoRacha(str, enum.Enum):
    """
    Tipos de eventos que pueden ocurrir en el sistema de rachas.
    
    Estos eventos se registran en el historial para trackear
    el progreso y cambios en las rachas de los usuarios.
    """
    INCREMENTO = "incremento"            # Racha aumentó en 1 día
    PERDIDA = "perdida"                  # Racha se perdió (reset a 0)
    RECUPERACION = "recuperacion"        # Racha fue recuperada con item
    CONGELACION = "congelacion"          # Racha protegida con item
    MILESTONE = "milestone"              # Se alcanzó un milestone
    RECORD_PERSONAL = "record_personal"  # Nueva mejor racha personal


class TipoMilestone(str, enum.Enum):
    """
    Tipos de milestones en el sistema de rachas.
    
    Los milestones son logros especiales que se otorgan
    al alcanzar ciertos días consecutivos de racha.
    """
    DIARIO = "diario"        # Recompensa diaria (1-7 días)
    SEMANAL = "semanal"      # Completar 7 días (1 semana)
    MENSUAL = "mensual"      # Completar 30 días (1 mes)
    ESPECIAL = "especial"    # Milestones especiales (60, 100, 365 días)


class TipoActividadRacha(str, enum.Enum):
    """
    Tipos de actividades que cuentan para mantener la racha.
    
    El usuario debe realizar AL MENOS una de estas actividades
    cada día para mantener su racha activa.
    """
    TAREA_COMPLETADA = "tarea_completada"
    EXAMEN_REALIZADO = "examen_realizado"
    CLASE_ASISTIDA = "clase_asistida"
    MATERIAL_ESTUDIADO = "material_estudiado"
    COMENTARIOS_REALIZADOS = "comentarios_realizados"
    PARTICIPACION_FORO = "participacion_foro"
