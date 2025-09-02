# backend/app/utils/websocket_utils.py
from typing import Dict, Optional, List
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import logging
import json
from redis.asyncio import Redis

# Conexión Redis
redis = Redis(host="localhost", port=6379, decode_responses=True)

# Ejemplo de uso

logger = logging.getLogger("websockets")
logging.basicConfig(level=logging.INFO, format="%(message)s")  # JSON logs

def log_json(event: str, data: dict):
    """Logger en formato JSON para producción."""
    log_entry = {
        "event": event,
        "data": data
    }
    logger.info(json.dumps(log_entry))


class ConnectionManager:
    """
    Gestor avanzado de conexiones WebSocket con soporte Redis Pub/Sub
    para múltiples instancias de la aplicación.
    """
    def __init__(self, redis_url: Optional[str] = None):
        self.active_connections: Dict[UUID, Dict[str, WebSocket]] = {}
        self.redis_url = redis_url
        self.redis = None
        if redis_url:
            asyncio.create_task(self._connect_redis())

    async def _connect_redis(self):
        """Conecta a Redis para Pub/Sub entre instancias"""
        self.redis = await redis.from_url(self.redis_url)
        log_json("REDIS", {"message": "Conexión a Redis establecida"})

    # -------------------------------
    # Conexión y desconexión
    # -------------------------------
    async def connect(self, websocket: WebSocket, group_chat_id: UUID, user_id: str):
        """Acepta y registra un WebSocket en un grupo"""
        await websocket.accept()
        self.active_connections.setdefault(group_chat_id, {})[user_id] = websocket
        log_json("USER_CONNECTED", {"user_id": user_id, "group_chat_id": str(group_chat_id)})

    def disconnect(self, group_chat_id: UUID, user_id: str):
        """Elimina una conexión WebSocket de un grupo"""
        group = self.active_connections.get(group_chat_id)
        if group and user_id in group:
            group.pop(user_id)
            log_json("USER_DISCONNECTED", {"user_id": user_id, "group_chat_id": str(group_chat_id)})
            if not group:
                self.active_connections.pop(group_chat_id)
                log_json("GROUP_REMOVED", {"group_chat_id": str(group_chat_id)})

    # -------------------------------
    # Envío de mensajes
    # -------------------------------
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Envía un mensaje a un WebSocket específico"""
        try:
            await websocket.send_json(message)
        except WebSocketDisconnect:
            log_json("DISCONNECTED", {"message": "WebSocket desconectado durante envío personal"})
        except Exception as e:
            log_json("ERROR", {"message": str(e)})

    async def broadcast_to_group(
        self,
        group_chat_id: UUID,
        message: dict,
        exclude_user: Optional[str] = None
    ):
        """
        Difunde un mensaje a todos los usuarios del grupo.
        Opción de excluir un usuario (ej. quien envió el mensaje).
        """
        group = self.active_connections.get(group_chat_id)
        if not group:
            return

        disconnected_users: List[str] = []

        for user_id, connection in group.items():
            if user_id == exclude_user:
                continue
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected_users.append(user_id)
            except Exception as e:
                log_json("ERROR", {"message": f"Error enviando a {user_id}: {e}"})

        for user_id in disconnected_users:
            self.disconnect(group_chat_id, user_id)

        # Si Redis está activo, publicar mensaje a otras instancias
        if self.redis:
            await self.redis.publish(
                str(group_chat_id), 
                json.dumps({"message": message, "exclude_user": exclude_user})
            )

    # -------------------------------
    # Información de usuarios
    # -------------------------------
    def get_connected_users(self, group_chat_id: UUID) -> List[str]:
        """Devuelve lista de user_ids conectados a un grupo"""
        return list(self.active_connections.get(group_chat_id, {}).keys())

    # -------------------------------
    # Redis Pub/Sub listener
    # -------------------------------
    async def listen_redis_channel(self, group_chat_id: UUID):
        """Escucha un canal Redis para recibir mensajes de otras instancias"""
        if not self.redis:
            return

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(str(group_chat_id))

        async for message in pubsub.listen():
            if message and message['type'] == 'message':
                payload = json.loads(message['data'])
                exclude_user = payload.get("exclude_user")
                await self.broadcast_to_group(group_chat_id, payload["message"], exclude_user=exclude_user)

