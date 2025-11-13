"""Enumeraciones para el sistema de misiones."""
from enum import Enum


class TipoMision(str, Enum):
    """Tipos de misiones disponibles."""
    PARTICIPACION = "participacion"  # Participar en clases/foros
    ENTREGA = "entrega"              # Entregar tareas/trabajos
    EVALUACION = "evaluacion"        # Completar exámenes
    RACHA = "racha"                  # Mantener rachas de estudio
    SOCIAL = "social"                # Interactuar con compañeros
    LOGRO = "logro"                  # Desbloquear logros
    PUNTOS = "puntos"                # Acumular puntos


class EstadoMision(str, Enum):
    """Estados posibles de una misión de usuario."""
    DISPONIBLE = "disponible"        # Misión activa y disponible
    EN_PROGRESO = "en_progreso"      # Usuario ha iniciado la misión
    COMPLETADA = "completada"        # Misión completada pero no reclamada
    RECLAMADA = "reclamada"          # Recompensa reclamada
    EXPIRADA = "expirada"            # Misión expiró sin completarse
    BLOQUEADA = "bloqueada"          # No disponible por requisitos


class FrecuenciaMision(str, Enum):
    """Frecuencia de renovación de misiones."""
    DIARIA = "diaria"                # Se renueva cada día
    SEMANAL = "semanal"              # Se renueva cada semana
    MENSUAL = "mensual"              # Se renueva cada mes
    UNICA = "unica"                  # Solo se puede completar una vez


class DificultadMision(str, Enum):
    """Nivel de dificultad de la misión."""
    FACIL = "facil"                  # Fácil de completar
    NORMAL = "normal"                # Dificultad media
    DIFICIL = "dificil"              # Requiere esfuerzo
    EPICA = "epica"                  # Muy difícil, grandes recompensas
