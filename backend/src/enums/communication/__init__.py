"""Enums para el módulo de comunicación.

Exporta todos los enums relacionados con comunicación,
chat, mensajería y videollamadas.
"""

from src.enums.communication.chat_grupo_enums import (
    EstadoChatGrupo,
)
from src.enums.communication.videollamada_enums import (
    CalidadConexion,
    CalidadGrabacion,
    EstadoProcesamiento,
    EstadoVideollamada,
    FormatoGrabacion,
    TipoLlamada,
)


__all__ = [
    "CalidadConexion",
    "CalidadGrabacion",
    # Chat de Grupo
    "EstadoChatGrupo",
    "EstadoProcesamiento",
    "EstadoVideollamada",
    "FormatoGrabacion",
    # Videollamadas
    "TipoLlamada",
]
