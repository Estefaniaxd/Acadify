# backend/app/services/websocket_service.py
import json
import logging
from typing import Dict, Set, List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Administrador de conexiones WebSocket para chats y notificaciones.
    """

    def __init__(self):
        # Conexiones activas por grupo: group_id -> {user_id: WebSocket}
        self.group_connections: Dict[UUID, Dict[UUID, WebSocket]] = {}
        # Conexiones globales para notificaciones: user_id -> WebSocket
        self.user_connections: Dict[UUID, WebSocket] = {}
        # Usuarios conectados a cada grupo: group_id -> set(user_id)
        self.connected_users: Dict[UUID, Set[UUID]] = {}

    # -----------------------
    # Conexión y desconexión
    # -----------------------
    async def connect(self, websocket: WebSocket, group_chat_id: UUID, user_id: UUID):
        await websocket.accept()
        self.group_connections.setdefault(group_chat_id, {})
        self.connected_users.setdefault(group_chat_id, set())

        self.group_connections[group_chat_id][user_id] = websocket
        self.connected_users[group_chat_id].add(user_id)

        logger.info(f"User {user_id} connected to chat {group_chat_id}")

    def disconnect(self, group_chat_id: UUID, user_id: UUID):
        """Desconectar usuario de un grupo de chat"""
        if group_chat_id in self.group_connections:
            self.group_connections[group_chat_id].pop(user_id, None)
            self.connected_users[group_chat_id].discard(user_id)

            # Limpiar si no hay usuarios
            if not self.group_connections[group_chat_id]:
                del self.group_connections[group_chat_id]
                del self.connected_users[group_chat_id]

        logger.info(f"User {user_id} disconnected from chat {group_chat_id}")

    async def connect_user_global(self, websocket: WebSocket, user_id: UUID):
        await websocket.accept()
        self.user_connections[user_id] = websocket
        logger.info(f"User {user_id} connected for global notifications")

    def disconnect_user_global(self, user_id: UUID):
        self.user_connections.pop(user_id, None)
        logger.info(f"User {user_id} disconnected from global notifications")

    # -----------------------
    # Envío de mensajes
    # -----------------------
    async def send_personal_message(self, user_id: UUID, message: dict):
        """Enviar mensaje directo a un usuario específico"""
        for group_id, connections in self.group_connections.items():
            if user_id in connections:
                try:
                    await connections[user_id].send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    self.disconnect(group_id, user_id)

    async def broadcast_to_group(
        self, group_chat_id: UUID, message: dict, exclude_user: Optional[UUID] = None
    ):
        """Enviar mensaje a todos los usuarios conectados a un grupo"""
        if group_chat_id not in self.group_connections:
            return

        connections = self.group_connections[group_chat_id].copy()
        disconnected_users = []

        for user_id, websocket in connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected_users.append(user_id)

        for user_id in disconnected_users:
            self.disconnect(group_chat_id, user_id)

    async def send_notification_to_user(self, user_id: UUID, notification: dict):
        """Enviar notificación a un usuario específico"""
        # Primero intentar conexión global
        ws = self.user_connections.get(user_id)
        if ws:
            try:
                await ws.send_text(json.dumps(notification))
                return
            except Exception as e:
                logger.error(f"Error sending notification to user {user_id}: {e}")
                self.disconnect_user_global(user_id)

        # Intentar enviar por grupo
        await self.send_personal_message(user_id, notification)

    # -----------------------
    # Indicadores y consultas
    # -----------------------
    async def send_typing_indicator(self, group_chat_id: UUID, user_id: UUID, is_typing: bool):
        """Enviar indicador de escritura"""
        typing_message = {
            "type": "typing_indicator",
            "data": {
                "user_id": str(user_id),
                "is_typing": is_typing,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.broadcast_to_group(group_chat_id, typing_message, exclude_user=user_id)

    def get_connected_users(self, group_chat_id: UUID) -> List[UUID]:
        return list(self.connected_users.get(group_chat_id, []))

    def is_user_connected(self, group_chat_id: UUID, user_id: UUID) -> bool:
        return user_id in self.connected_users.get(group_chat_id, set())

    def get_total_connections(self) -> int:
        total = len(self.user_connections)
        total += sum(len(connections) for connections in self.group_connections.values())
        return total

    # -----------------------
    # Notificaciones de sistema
    # -----------------------
    async def broadcast_system_notification(self, notification: dict):
        """Enviar notificación del sistema a todos los usuarios"""
        # Global
        for user_id, ws in list(self.user_connections.items()):
            try:
                await ws.send_text(json.dumps(notification))
            except Exception:
                self.disconnect_user_global(user_id)
        # Por grupo
        for group_id in list(self.group_connections.keys()):
            await self.broadcast_to_group(group_id, notification)

    # -----------------------
    # Limpieza de conexiones
    # -----------------------
    async def handle_connection_cleanup(self):
        """Limpiar conexiones inactivas enviando pings"""
        ping_message = {"type": "ping", "timestamp": datetime.utcnow().isoformat()}

        # Global
        for user_id, ws in list(self.user_connections.items()):
            try:
                await ws.send_text(json.dumps(ping_message))
            except Exception:
                self.disconnect_user_global(user_id)

        # Por grupo
        for group_id in list(self.group_connections.keys()):
            for user_id, ws in list(self.group_connections[group_id].items()):
                try:
                    await ws.send_text(json.dumps(ping_message))
                except Exception:
                    self.disconnect(group_id, user_id)


# Singleton
websocket_manager = WebSocketManager()
