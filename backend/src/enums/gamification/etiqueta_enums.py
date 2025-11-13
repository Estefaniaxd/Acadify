"""
Enums para el sistema de etiquetas de perfil.

Este módulo define las categorías y niveles de rareza para las etiquetas
que los usuarios pueden mostrar en sus perfiles.

Author: GitHub Copilot & Team
Date: 31 de octubre de 2025
Version: 1.0.0
"""

import enum


class CategoriaEtiqueta(str, enum.Enum):
    """
    Categorías temáticas de etiquetas de perfil.
    
    Las etiquetas se agrupan por temas relacionados con
    áreas académicas, habilidades o logros especiales.
    """
    # Áreas académicas
    MATEMATICAS = "matematicas"
    CIENCIAS = "ciencias"
    PROGRAMACION = "programacion"
    IDIOMAS = "idiomas"
    LITERATURA = "literatura"
    HISTORIA = "historia"
    ARTE = "arte"
    MUSICA = "musica"
    
    # Habilidades generales
    LECTURA = "lectura"
    ESCRITURA = "escritura"
    INVESTIGACION = "investigacion"
    PENSAMIENTO_CRITICO = "pensamiento_critico"
    CREATIVIDAD = "creatividad"
    LIDERAZGO = "liderazgo"
    
    # Logros y participación
    LOGRO_TAREAS = "logro_tareas"
    LOGRO_EXAMENES = "logro_examenes"
    PARTICIPACION = "participacion"
    COLABORACION = "colaboracion"
    
    # Especiales
    RACHA = "racha"
    RANKING = "ranking"
    EVENTO = "evento"
    ESPECIAL = "especial"


class RarezaEtiqueta(str, enum.Enum):
    """
    Niveles de rareza para etiquetas de perfil.
    
    La rareza indica la dificultad para obtener la etiqueta
    y su valor dentro del sistema de gamificación.
    
    Las etiquetas pueden evolucionar de un nivel a otro
    cumpliendo requisitos específicos.
    """
    COMUN = "comun"              # ⬜ Blanco - Fácil de obtener
    RARO = "raro"                # 🟦 Azul - Requiere esfuerzo
    EPICO = "epico"              # 🟪 Púrpura - Difícil de obtener
    LEGENDARIO = "legendario"    # 🟧 Dorado - Muy exclusivo


class TipoRequisito(str, enum.Enum):
    """
    Tipos de requisitos para desbloquear o evolucionar etiquetas.
    """
    TAREAS_COMPLETADAS = "tareas_completadas"
    TAREAS_PERFECTAS = "tareas_perfectas"
    EXAMENES_APROBADOS = "examenes_aprobados"
    EXAMENES_PERFECTOS = "examenes_perfectos"
    RACHA_DIAS = "racha_dias"
    PUNTOS_ACUMULADOS = "puntos_acumulados"
    MATERIALES_LEIDOS = "materiales_leidos"
    COMENTARIOS_REALIZADOS = "comentarios_realizados"
    RANKING_POSICION = "ranking_posicion"
    CURSOS_COMPLETADOS = "cursos_completados"
    PROMEDIO_CALIFICACION = "promedio_calificacion"
