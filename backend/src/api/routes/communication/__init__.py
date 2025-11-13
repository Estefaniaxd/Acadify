"""Communication routes package.

Exporta routers de:
- chat: Salas de chat y mensajes (REST API)
- chat_ws: WebSocket para chat en tiempo real
- videollamadas: Sistema de videollamadas con Jitsi
- notificaciones: Sistema de notificaciones (implementación básica)
- archivo_chat: Archivos en chats
- faq_bot: Bot de preguntas frecuentes
- chat_bot: Chatbot general
- mensaje_bot: Mensajes del bot
"""

from src.api.routes.communication.chat import router as chat_router
from src.api.routes.communication.chat_ws import router as chat_ws_router
from src.api.routes.communication.notificaciones import router as notificaciones_router
from src.api.routes.communication.videollamadas import router as videollamadas_router

__all__ = [
    "chat_router",
    "chat_ws_router",
    "videollamadas_router",
    "notificaciones_router",
]
