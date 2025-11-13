# __init__.py
"""Modelos del sistema de comunicación.

Este módulo contiene todos los modelos relacionados con el sistema de comunicación:
- Mensajería (Mensaje, SalaChat, ParticipanteSala)
- Notificaciones (Notificacion, ConfiguracionNotificaciones)
- Comentarios y Reacciones
- Chat de grupo
- Bots y FAQ
"""

# Modelos de chat
# from .archivo_chat import ArchivoChat  # Deshabilitado temporalmente
from .chat import (
    ConfiguracionNotificaciones,
    EstadoMensaje,
    LecturaMensaje,
    Notificacion,
    ParticipanteSala,
    SalaChat,
    TipoMensaje,
    TipoSala,
)

# Modelos de bots
from .chat_bot import ChatBot

# Modelos de chat grupal
from .chat_grupo import ChatGrupo

# Modelos de comentarios y reacciones
from .comentario import Comentario, TipoComentario
from .faq_bot import FAQBot

# Modelo principal de mensajes (29 campos completos)
from .mensaje import Mensaje
from .mensaje_bot import MensajeBot
from .reaccion import Reaccion, ReaccionMensaje
from .videollamada import Videollamada, VideollamadaParticipante, VideollamadaGrabacion

# Exportar todos los modelos
__all__ = [
    # "ArchivoChat",  # Deshabilitado temporalmente
    # Bots
    "ChatBot",
    # Chat Grupal
    "ChatGrupo",
    # Comentarios y Reacciones
    "Comentario",
    "ConfiguracionNotificaciones",
    "EstadoMensaje",
    "FAQBot",
    "LecturaMensaje",
    "Mensaje",  # Modelo principal con 29 campos
    "MensajeBot",
    "Notificacion",
    "ParticipanteSala",
    "Reaccion",
    "ReaccionMensaje",
    # Chat
    "SalaChat",
    "TipoComentario",
    "TipoMensaje",
    "TipoSala",
    # Videollamadas
    "Videollamada",
    "VideollamadaParticipante",
    "VideollamadaGrabacion",
]
