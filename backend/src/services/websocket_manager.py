"""Sistema WebSocket para comunicación en tiempo real
Maneja conexiones, mensajes instantáneos, notificaciones push y presencia de usuarios.
"""

import asyncio
from datetime import UTC, datetime
import json
import logging
from typing import Any

from fastapi import Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user_websocket
from src.crud.communication.chat import (
    crud_lectura_mensaje,
    crud_mensaje,
    crud_notificacion,
    crud_participante_sala,
)
from src.db.session import get_db
from src.models.communication.chat import Mensaje, TipoMensaje
from src.models.users import Usuario
from src.schemas.communication.chat_schemas import MensajeCreate, NotificacionCreate


logger = logging.getLogger(__name__)


class ConnectionManager:
    """Gestor de conexiones WebSocket."""

    def __init__(self) -> None:
        # {usuario_id: {connection_id: WebSocket}}
        self.active_connections: dict[str, dict[str, WebSocket]] = {}
        # {sala_id: Set[usuario_id]}
        self.sala_participants: dict[str, set[str]] = {}
        # {usuario_id: {"sala_id": str, "last_activity": datetime}}
        self.user_activity: dict[str, dict[str, Any]] = {}
        # {connection_id: {"usuario_id": str, "sala_id": str}}
        self.connection_info: dict[str, dict[str, str]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        usuario_id: str,
        sala_id: str | None = None,
        connection_id: str | None = None,
    ) -> None:
        """Conectar usuario al WebSocket."""
        await websocket.accept()

        if connection_id is None:
            connection_id = f"{usuario_id}_{datetime.now(UTC).timestamp()}"

        # Registrar conexión
        if usuario_id not in self.active_connections:
            self.active_connections[usuario_id] = {}

        self.active_connections[usuario_id][connection_id] = websocket

        # Registrar información de la conexión
        self.connection_info[connection_id] = {
            "usuario_id": usuario_id,
            "sala_id": sala_id,
        }

        # Agregar a sala si se especifica
        if sala_id:
            await self.join_sala(usuario_id, sala_id)

        # Actualizar actividad
        self.user_activity[usuario_id] = {
            "sala_id": sala_id,
            "last_activity": datetime.now(UTC),
            "status": "online",
        }

        logger.info(f"Usuario {usuario_id} conectado. Connection ID: {connection_id}")

        # Notificar a otros usuarios de la sala que el usuario está online
        if sala_id:
            await self.broadcast_to_sala(
                sala_id,
                {
                    "type": "user_online",
                    "usuario_id": usuario_id,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                exclude_user=usuario_id,
            )

    async def disconnect(self, connection_id: str) -> None:
        """Desconectar usuario del WebSocket."""
        if connection_id not in self.connection_info:
            return

        conn_info = self.connection_info[connection_id]
        usuario_id = conn_info["usuario_id"]
        sala_id = conn_info.get("sala_id")

        # Remover conexión específica
        if usuario_id in self.active_connections:
            if connection_id in self.active_connections[usuario_id]:
                del self.active_connections[usuario_id][connection_id]

            # Si no quedan conexiones, remover usuario completamente
            if not self.active_connections[usuario_id]:
                del self.active_connections[usuario_id]

                # Actualizar estado a offline
                if usuario_id in self.user_activity:
                    self.user_activity[usuario_id]["status"] = "offline"
                    self.user_activity[usuario_id]["last_activity"] = datetime.now(UTC)

                # Remover de salas
                for participants in self.sala_participants.values():
                    participants.discard(usuario_id)

                # Notificar a otros usuarios que está offline
                if sala_id:
                    await self.broadcast_to_sala(
                        sala_id,
                        {
                            "type": "user_offline",
                            "usuario_id": usuario_id,
                            "timestamp": datetime.now(UTC).isoformat(),
                        },
                        exclude_user=usuario_id,
                    )

        # Limpiar información de conexión
        del self.connection_info[connection_id]

        logger.info(
            f"Usuario {usuario_id} desconectado. Connection ID: {connection_id}"
        )

    async def join_sala(self, usuario_id: str, sala_id: str) -> None:
        """Usuario se une a una sala."""
        if sala_id not in self.sala_participants:
            self.sala_participants[sala_id] = set()

        self.sala_participants[sala_id].add(usuario_id)

        # Actualizar actividad del usuario
        if usuario_id in self.user_activity:
            self.user_activity[usuario_id]["sala_id"] = sala_id
            self.user_activity[usuario_id]["last_activity"] = datetime.now(UTC)

    async def leave_sala(self, usuario_id: str, sala_id: str) -> None:
        """Usuario deja una sala."""
        if sala_id in self.sala_participants:
            self.sala_participants[sala_id].discard(usuario_id)

            # Limpiar sala vacía
            if not self.sala_participants[sala_id]:
                del self.sala_participants[sala_id]

    async def send_personal_message(
        self, usuario_id: str, message: dict[str, Any]
    ) -> None:
        """Enviar mensaje a un usuario específico (todas sus conexiones)."""
        if usuario_id in self.active_connections:
            disconnected_connections = []

            for connection_id, websocket in self.active_connections[usuario_id].items():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.exception(f"Error enviando mensaje a {usuario_id}: {e}")
                    disconnected_connections.append(connection_id)

            # Limpiar conexiones muertas
            for conn_id in disconnected_connections:
                await self.disconnect(conn_id)

    async def broadcast_to_sala(
        self, sala_id: str, message: dict[str, Any], exclude_user: str | None = None
    ) -> None:
        """Broadcast mensaje a todos los usuarios de una sala."""
        if sala_id not in self.sala_participants:
            return

        participants = self.sala_participants[sala_id].copy()
        if exclude_user:
            participants.discard(exclude_user)

        for usuario_id in participants:
            await self.send_personal_message(usuario_id, message)

    async def get_online_users_in_sala(self, sala_id: str) -> list[str]:
        """Obtener usuarios online en una sala."""
        if sala_id not in self.sala_participants:
            return []

        online_users = []
        for usuario_id in self.sala_participants[sala_id]:
            if usuario_id in self.active_connections:
                online_users.append(usuario_id)

        return online_users

    def get_user_status(self, usuario_id: str) -> dict[str, Any]:
        """Obtener estado de un usuario."""
        if usuario_id in self.user_activity:
            return self.user_activity[usuario_id]

        return {"status": "offline", "last_activity": None, "sala_id": None}


# Instancia global del gestor de conexiones
manager = ConnectionManager()


class WebSocketHandler:
    """Manejador de eventos WebSocket."""

    def __init__(self, db: Session, usuario: Usuario) -> None:
        self.db = db
        self.usuario = usuario

    async def handle_message(self, websocket: WebSocket, data: dict[str, Any]) -> None:
        """Manejar mensaje recibido del cliente."""
        message_type = data.get("type")

        try:
            if message_type == "send_message":
                await self._handle_send_message(data)
            elif message_type == "join_sala":
                await self._handle_join_sala(data)
            elif message_type == "leave_sala":
                await self._handle_leave_sala(data)
            elif message_type == "mark_read":
                await self._handle_mark_read(data)
            elif message_type == "typing":
                await self._handle_typing(data)
            elif message_type == "reaction":
                await self._handle_reaction(data)
            elif message_type == "get_online_users":
                await self._handle_get_online_users(websocket, data)
            else:
                logger.warning(f"Tipo de mensaje no reconocido: {message_type}")
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"Tipo de mensaje no reconocido: {message_type}",
                        }
                    )
                )

        except Exception as e:
            logger.exception(f"Error manejando mensaje {message_type}: {e}")
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

    async def _handle_send_message(self, data: dict[str, Any]) -> None:
        """Manejar envío de mensaje."""
        try:
            # Crear mensaje en base de datos
            mensaje_data = MensajeCreate(
                sala_id=data["sala_id"],
                contenido=data["contenido"],
                tipo_mensaje=data.get("tipo_mensaje", TipoMensaje.TEXTO),
                mensaje_padre_id=data.get("mensaje_padre_id"),
                archivos_urls=data.get("archivos_urls"),
                metadatos_archivos=data.get("metadatos_archivos"),
                menciones_usuarios=data.get("menciones_usuarios", []),
                menciones_ia=data.get("menciones_ia", False),
                menciones_todos=data.get("menciones_todos", False),
                es_importante=data.get("es_importante", False),
                es_anuncio=data.get("es_anuncio", False),
            )

            # Verificar que el usuario puede escribir en la sala
            participante = crud_participante_sala.get_participante(
                self.db,
                sala_id=str(mensaje_data.sala_id),
                usuario_id=str(self.usuario.id),
            )

            if not participante or not participante.puede_escribir:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permisos para escribir en esta sala",
                )

            # Crear mensaje
            mensaje = crud_mensaje.create_mensaje(
                self.db, obj_in=mensaje_data, usuario_id=str(self.usuario.id)
            )

            # Preparar mensaje para broadcast
            mensaje_broadcast = {
                "type": "new_message",
                "mensaje": {
                    "id": str(mensaje.id),
                    "sala_id": str(mensaje.sala_id),
                    "usuario_id": str(mensaje.usuario_id),
                    "contenido": mensaje.contenido,
                    "contenido_html": mensaje.contenido_html,
                    "tipo_mensaje": mensaje.tipo_mensaje.value,
                    "archivos_urls": mensaje.archivos_urls,
                    "metadatos_archivos": mensaje.metadatos_archivos,
                    "mensaje_padre_id": (
                        str(mensaje.mensaje_padre_id)
                        if mensaje.mensaje_padre_id
                        else None
                    ),
                    "menciones_usuarios": mensaje.menciones_usuarios,
                    "menciones_ia": mensaje.menciona_ia,
                    "menciones_todos": mensaje.menciones_todos,
                    "es_importante": mensaje.es_importante,
                    "es_anuncio": mensaje.es_anuncio,
                    "fecha_creacion": mensaje.fecha_creacion.isoformat(),
                    "usuario_nombre": self.usuario.nombre,
                    "usuario_apellido": self.usuario.apellido,
                    "usuario_avatar": getattr(self.usuario, "avatar_url", None),
                },
            }

            # Broadcast a la sala
            await manager.broadcast_to_sala(str(mensaje.sala_id), mensaje_broadcast)

            # Si menciona a Rutilio (IA), procesar respuesta automática
            if mensaje.menciona_ia:
                await self._handle_rutilio_mention(mensaje)

            # Crear notificaciones para menciones
            if mensaje.menciones_usuarios or mensaje.menciones_todos:
                await self._create_mention_notifications(mensaje)

        except Exception as e:
            logger.exception(f"Error enviando mensaje: {e}")
            raise

    async def _handle_join_sala(self, data: dict[str, Any]) -> None:
        """Manejar unirse a sala."""
        sala_id = data["sala_id"]

        # Verificar que el usuario puede acceder a la sala
        participante = crud_participante_sala.get_participante(
            self.db, sala_id=sala_id, usuario_id=str(self.usuario.id)
        )

        if not participante:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a esta sala",
            )

        await manager.join_sala(str(self.usuario.id), sala_id)

        # Notificar a otros usuarios
        await manager.broadcast_to_sala(
            sala_id,
            {
                "type": "user_joined",
                "usuario_id": str(self.usuario.id),
                "usuario_nombre": self.usuario.nombre,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            exclude_user=str(self.usuario.id),
        )

    async def _handle_leave_sala(self, data: dict[str, Any]) -> None:
        """Manejar salir de sala."""
        sala_id = data["sala_id"]
        await manager.leave_sala(str(self.usuario.id), sala_id)

        # Notificar a otros usuarios
        await manager.broadcast_to_sala(
            sala_id,
            {
                "type": "user_left",
                "usuario_id": str(self.usuario.id),
                "timestamp": datetime.now(UTC).isoformat(),
            },
            exclude_user=str(self.usuario.id),
        )

    async def _handle_mark_read(self, data: dict[str, Any]) -> None:
        """Manejar marcado de mensajes como leídos."""
        mensajes_ids = data.get("mensajes_ids", [])
        sala_id = data.get("sala_id")

        if sala_id:
            # Marcar toda la sala como leída
            crud_lectura_mensaje.marcar_mensajes_sala_leidos(
                self.db, sala_id=sala_id, usuario_id=str(self.usuario.id)
            )
        else:
            # Marcar mensajes específicos
            for mensaje_id in mensajes_ids:
                crud_lectura_mensaje.marcar_como_leido(
                    self.db, mensaje_id=mensaje_id, usuario_id=str(self.usuario.id)
                )

        # Notificar actualización de estado de lectura
        if sala_id:
            await manager.broadcast_to_sala(
                sala_id,
                {
                    "type": "messages_read",
                    "usuario_id": str(self.usuario.id),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

    async def _handle_typing(self, data: dict[str, Any]) -> None:
        """Manejar indicador de escritura."""
        sala_id = data["sala_id"]
        is_typing = data.get("is_typing", False)

        await manager.broadcast_to_sala(
            sala_id,
            {
                "type": "typing",
                "usuario_id": str(self.usuario.id),
                "usuario_nombre": self.usuario.nombre,
                "is_typing": is_typing,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            exclude_user=str(self.usuario.id),
        )

    async def _handle_reaction(self, data: dict[str, Any]) -> None:
        """Manejar reacciones a mensajes."""
        mensaje_id = data["mensaje_id"]
        emoji = data["emoji"]

        # Agregar reacción en base de datos
        success = crud_mensaje.agregar_reaccion(
            self.db, mensaje_id=mensaje_id, usuario_id=str(self.usuario.id), emoji=emoji
        )

        if success:
            # Obtener mensaje para broadcast
            mensaje = crud_mensaje.get(self.db, id=mensaje_id)
            if mensaje:
                await manager.broadcast_to_sala(
                    str(mensaje.sala_id),
                    {
                        "type": "message_reaction",
                        "mensaje_id": mensaje_id,
                        "emoji": emoji,
                        "usuario_id": str(self.usuario.id),
                        "reacciones": mensaje.reacciones,
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                )

    async def _handle_get_online_users(
        self, websocket: WebSocket, data: dict[str, Any]
    ) -> None:
        """Obtener usuarios online en una sala."""
        sala_id = data["sala_id"]
        online_users = await manager.get_online_users_in_sala(sala_id)

        await websocket.send_text(
            json.dumps(
                {
                    "type": "online_users",
                    "sala_id": sala_id,
                    "users": online_users,
                    "count": len(online_users),
                }
            )
        )

    async def _handle_rutilio_mention(self, mensaje: Mensaje) -> None:
        """Procesar mención a Rutilio (IA)."""
        try:
            # Simular respuesta de IA (aquí se integraría con el servicio de IA real)
            await asyncio.sleep(2)  # Simular tiempo de procesamiento

            respuesta_ia = await self._generate_rutilio_response(mensaje.contenido)

            # Crear mensaje de respuesta de Rutilio
            mensaje_ia = MensajeCreate(
                sala_id=mensaje.sala_id,
                contenido=respuesta_ia,
                tipo_mensaje=TipoMensaje.IA,
                mensaje_padre_id=mensaje.id,
            )

            # TODO: Crear usuario "Rutilio" o usar ID especial
            rutilio_user_id = "rutilio-ia-bot"

            mensaje_respuesta = crud_mensaje.create_mensaje(
                self.db, obj_in=mensaje_ia, usuario_id=rutilio_user_id
            )

            # Broadcast respuesta de IA
            await manager.broadcast_to_sala(
                str(mensaje.sala_id),
                {
                    "type": "new_message",
                    "mensaje": {
                        "id": str(mensaje_respuesta.id),
                        "sala_id": str(mensaje_respuesta.sala_id),
                        "usuario_id": rutilio_user_id,
                        "contenido": mensaje_respuesta.contenido,
                        "tipo_mensaje": TipoMensaje.IA.value,
                        "mensaje_padre_id": str(mensaje.id),
                        "fecha_creacion": mensaje_respuesta.fecha_creacion.isoformat(),
                        "usuario_nombre": "Rutilio",
                        "usuario_apellido": "IA Assistant",
                        "usuario_avatar": "/static/rutilio-avatar.png",
                        "es_ia": True,
                    },
                },
            )

        except Exception as e:
            logger.exception(f"Error procesando mención de Rutilio: {e}")

    async def _generate_rutilio_response(self, contenido: str) -> str:
        """Generar respuesta de Rutilio basada en el contenido."""
        # Aquí se integraría con el servicio de IA real
        # Por ahora, respuestas predefinidas simples

        contenido_lower = contenido.lower()

        if "tarea" in contenido_lower or "assignment" in contenido_lower:
            return "¡Hola! 👋 Soy Rutilio, tu asistente de IA. Veo que tienes una pregunta sobre tareas. ¿En qué puedo ayudarte específicamente? Puedo ayudarte con plazos, instrucciones, o recursos para completar tus asignaciones. 📚"

        if "ayuda" in contenido_lower or "help" in contenido_lower:
            return "¡Por supuesto que puedo ayudarte! 🤝 Soy tu asistente académico virtual. Puedo ayudarte con:\n\n📚 Explicar conceptos\n📝 Revisar tareas\n📅 Recordar fechas importantes\n🔍 Buscar recursos\n💡 Dar sugerencias de estudio\n\n¿Qué necesitas?"

        if "examen" in contenido_lower or "test" in contenido_lower:
            return "¡Perfecto! 📋 Para ayudarte con tu examen, necesito saber:\n\n• ¿De qué materia es?\n• ¿Qué temas específicos incluye?\n• ¿Cuándo es la fecha?\n\nPuedo ayudarte a crear un plan de estudio, explicar conceptos, o darte tips para prepararte mejor. 🎯"

        if "gracias" in contenido_lower or "thanks" in contenido_lower:
            return "¡De nada! 😊 Siempre es un placer ayudarte. Recuerda que estoy aquí 24/7 para apoyarte en tu proceso de aprendizaje. ¡Mucho éxito en tus estudios! 🌟"

        return "¡Hola! 👋 Soy Rutilio, tu asistente de IA educativo. He recibido tu mensaje y estoy aquí para ayudarte con cualquier duda académica. ¿Podrías ser más específico sobre qué necesitas? Puedo ayudarte con tareas, explicar conceptos, buscar recursos, y mucho más. 🤖📚"

    async def _create_mention_notifications(self, mensaje: Mensaje) -> None:
        """Crear notificaciones para usuarios mencionados."""
        try:
            # Notificación para menciones específicas
            if mensaje.menciones_usuarios:
                for usuario_mencionado in mensaje.menciones_usuarios:
                    notificacion = NotificacionCreate(
                        usuario_id=usuario_mencionado,
                        titulo=f"Te mencionaron en {mensaje.sala.nombre}",
                        mensaje=f"{self.usuario.nombre} te mencionó: {mensaje.contenido[:100]}...",
                        tipo_notificacion="mencion",
                        sala_id=mensaje.sala_id,
                        mensaje_id=mensaje.id,
                        url_accion=f"/salas/{mensaje.sala_id}",
                        icono="at-symbol",
                        color="#3B82F6",
                    )

                    crud_notificacion.create(self.db, obj_in=notificacion)

                    # Enviar notificación push via WebSocket
                    await manager.send_personal_message(
                        usuario_mencionado,
                        {
                            "type": "notification",
                            "notificacion": notificacion.dict(),
                            "timestamp": datetime.now(UTC).isoformat(),
                        },
                    )

            # Notificación para @todos
            if mensaje.menciones_todos:
                # Obtener todos los participantes de la sala
                participantes = crud_participante_sala.get_participantes_sala(
                    self.db, sala_id=str(mensaje.sala_id)
                )

                for participante in participantes:
                    if (
                        participante.usuario_id != self.usuario.id
                    ):  # No notificar al remitente
                        notificacion = NotificacionCreate(
                            usuario_id=str(participante.usuario_id),
                            titulo=f"Mensaje importante en {mensaje.sala.nombre}",
                            mensaje=f"{self.usuario.nombre} mencionó a todos: {mensaje.contenido[:100]}...",
                            tipo_notificacion="mencion_todos",
                            sala_id=mensaje.sala_id,
                            mensaje_id=mensaje.id,
                            url_accion=f"/salas/{mensaje.sala_id}",
                            icono="megaphone",
                            color="#F59E0B",
                        )

                        crud_notificacion.create(self.db, obj_in=notificacion)

                        # Enviar notificación push
                        await manager.send_personal_message(
                            str(participante.usuario_id),
                            {
                                "type": "notification",
                                "notificacion": notificacion.dict(),
                                "timestamp": datetime.now(UTC).isoformat(),
                            },
                        )

        except Exception as e:
            logger.exception(f"Error creando notificaciones de mención: {e}")


# Funciones auxiliares para FastAPI
async def websocket_endpoint(
    websocket: WebSocket,
    usuario_id: str | None = None,
    sala_id: str | None = None,
    token: str | None = None,
    db: Session = Depends(get_db),
) -> None:
    """Endpoint principal de WebSocket."""
    try:
        # Autenticar usuario (implementar según tu sistema de auth)
        if token:
            usuario = await get_current_user_websocket(token, db)
        else:
            # Fallback - obtener usuario por ID (para desarrollo)
            from crud.user.usuario import crud_usuario

            usuario = crud_usuario.get(db, id=usuario_id)

        if not usuario:
            await websocket.close(code=1008, reason="Authentication failed")
            return

        # Conectar usuario
        connection_id = f"{usuario.id}_{datetime.now(UTC).timestamp()}"
        await manager.connect(websocket, str(usuario.id), sala_id, connection_id)

        # Crear handler
        handler = WebSocketHandler(db, usuario)

        # Enviar mensaje de bienvenida
        await websocket.send_text(
            json.dumps(
                {
                    "type": "connected",
                    "usuario_id": str(usuario.id),
                    "connection_id": connection_id,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
        )

        # Loop principal de mensajes
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                await handler.handle_message(websocket, message_data)

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": "Formato de mensaje inválido. Se esperaba JSON válido.",
                        }
                    )
                )
            except Exception as e:
                logger.exception(f"Error en WebSocket loop: {e}")
                await websocket.send_text(
                    json.dumps({"type": "error", "message": str(e)})
                )

    except Exception as e:
        logger.exception(f"Error en websocket_endpoint: {e}")

    finally:
        # Desconectar usuario
        if "connection_id" in locals():
            await manager.disconnect(connection_id)
