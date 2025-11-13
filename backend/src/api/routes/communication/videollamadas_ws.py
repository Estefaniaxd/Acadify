"""WebSocket Endpoint para Videollamadas
Maneja conexiones WebSocket específicas para eventos de videollamadas en tiempo real.
"""

import builtins
import contextlib
from datetime import UTC, datetime
import json
import logging
from typing import Any

from fastapi import Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from api.dependencies import get_current_user_websocket, get_db
from crud.communication.videollamada import (
    crud_videollamada,
    crud_videollamada_participante,
)
from models.users import Usuario
from services.videollamada_websocket import videollamada_ws_manager


logger = logging.getLogger(__name__)


class VideollamadaWebSocketHandler:
    """Handler para eventos WebSocket de videollamadas.
    Procesa mensajes entrantes y coordina respuestas.
    """

    def __init__(self, db: Session, usuario: Usuario, videollamada_id: str) -> None:
        self.db = db
        self.usuario = usuario
        self.videollamada_id = videollamada_id
        self.connection_id = None

    async def handle_message(self, websocket: WebSocket, data: dict[str, Any]) -> None:
        """Manejar mensaje recibido del cliente.

        Args:
            websocket: Conexión WebSocket
            data: Datos del mensaje
        """
        message_type = data.get("type")

        try:
            # Routing de mensajes según tipo
            if message_type == "audio_toggle":
                await self._handle_audio_toggle(data)

            elif message_type == "video_toggle":
                await self._handle_video_toggle(data)

            elif message_type == "screenshare_toggle":
                await self._handle_screenshare_toggle(data)

            elif message_type == "mute_participant":
                await self._handle_mute_participant(data)

            elif message_type == "remove_participant":
                await self._handle_remove_participant(data)

            elif message_type == "start_recording":
                await self._handle_start_recording(data)

            elif message_type == "stop_recording":
                await self._handle_stop_recording(data)

            elif message_type == "get_participants_state":
                await self._handle_get_participants_state(websocket)

            elif message_type == "ping":
                await self._handle_ping(websocket)

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

    # ===============================
    # Handlers de Audio/Video
    # ===============================

    async def _handle_audio_toggle(self, data: dict[str, Any]) -> None:
        """Handler para activar/desactivar audio."""
        enabled = data.get("enabled", False)

        # Actualizar estado en BD
        participante = crud_videollamada_participante.get_participante(
            self.db,
            videollamada_id=self.videollamada_id,
            usuario_id=str(self.usuario.id),
        )

        if participante:
            crud_videollamada_participante.update(
                self.db, db_obj=participante, obj_in={"audio_activo": enabled}
            )

        # Emitir evento
        await videollamada_ws_manager.emit_audio_toggled(
            videollamada_id=self.videollamada_id,
            usuario_id=str(self.usuario.id),
            enabled=enabled,
        )

    async def _handle_video_toggle(self, data: dict[str, Any]) -> None:
        """Handler para activar/desactivar video."""
        enabled = data.get("enabled", False)

        # Actualizar estado en BD
        participante = crud_videollamada_participante.get_participante(
            self.db,
            videollamada_id=self.videollamada_id,
            usuario_id=str(self.usuario.id),
        )

        if participante:
            crud_videollamada_participante.update(
                self.db, db_obj=participante, obj_in={"video_activo": enabled}
            )

        # Emitir evento
        await videollamada_ws_manager.emit_video_toggled(
            videollamada_id=self.videollamada_id,
            usuario_id=str(self.usuario.id),
            enabled=enabled,
        )

    async def _handle_screenshare_toggle(self, data: dict[str, Any]) -> None:
        """Handler para activar/desactivar compartir pantalla."""
        enabled = data.get("enabled", False)

        # Actualizar estado en BD
        participante = crud_videollamada_participante.get_participante(
            self.db,
            videollamada_id=self.videollamada_id,
            usuario_id=str(self.usuario.id),
        )

        if participante:
            crud_videollamada_participante.update(
                self.db, db_obj=participante, obj_in={"compartiendo_pantalla": enabled}
            )

        # Emitir evento
        await videollamada_ws_manager.emit_screenshare_toggled(
            videollamada_id=self.videollamada_id,
            usuario_id=str(self.usuario.id),
            enabled=enabled,
        )

    # ===============================
    # Handlers de Moderación
    # ===============================

    async def _handle_mute_participant(self, data: dict[str, Any]) -> None:
        """Handler para silenciar participante (solo moderadores)."""
        target_usuario_id = data.get("usuario_id")

        if not target_usuario_id:
            msg = "usuario_id requerido"
            raise ValueError(msg)

        # Verificar que el usuario actual es moderador
        participante_actual = crud_videollamada_participante.get_participante(
            self.db,
            videollamada_id=self.videollamada_id,
            usuario_id=str(self.usuario.id),
        )

        if not participante_actual or not participante_actual.es_moderador:
            msg = "Solo moderadores pueden silenciar participantes"
            raise PermissionError(msg)

        # Actualizar estado del participante objetivo
        participante_target = crud_videollamada_participante.get_participante(
            self.db, videollamada_id=self.videollamada_id, usuario_id=target_usuario_id
        )

        if participante_target:
            crud_videollamada_participante.update(
                self.db, db_obj=participante_target, obj_in={"audio_activo": False}
            )

        # Emitir evento
        await videollamada_ws_manager.emit_participant_muted(
            videollamada_id=self.videollamada_id,
            usuario_id=target_usuario_id,
            muted_by_moderador_id=str(self.usuario.id),
        )

    async def _handle_remove_participant(self, data: dict[str, Any]) -> None:
        """Handler para expulsar participante (solo moderadores)."""
        target_usuario_id = data.get("usuario_id")
        razon = data.get("razon")

        if not target_usuario_id:
            msg = "usuario_id requerido"
            raise ValueError(msg)

        # Verificar que el usuario actual es moderador
        participante_actual = crud_videollamada_participante.get_participante(
            self.db,
            videollamada_id=self.videollamada_id,
            usuario_id=str(self.usuario.id),
        )

        if not participante_actual or not participante_actual.es_moderador:
            msg = "Solo moderadores pueden expulsar participantes"
            raise PermissionError(msg)

        # Remover participante
        participante_target = crud_videollamada_participante.get_participante(
            self.db, videollamada_id=self.videollamada_id, usuario_id=target_usuario_id
        )

        if participante_target:
            crud_videollamada_participante.remover_participante(
                self.db,
                videollamada_id=self.videollamada_id,
                usuario_id=target_usuario_id,
            )

        # Emitir evento
        await videollamada_ws_manager.emit_participant_removed(
            videollamada_id=self.videollamada_id,
            usuario_id=target_usuario_id,
            removed_by_moderador_id=str(self.usuario.id),
            razon=razon,
        )

        # Forzar desconexión del participante
        await videollamada_ws_manager.leave_videollamada(
            self.videollamada_id, target_usuario_id
        )

    # ===============================
    # Handlers de Grabación
    # ===============================

    async def _handle_start_recording(self, data: dict[str, Any]) -> None:
        """Handler para iniciar grabación (solo moderadores)."""
        # Verificar permisos de moderador
        participante = crud_videollamada_participante.get_participante(
            self.db,
            videollamada_id=self.videollamada_id,
            usuario_id=str(self.usuario.id),
        )

        if not participante or not participante.es_moderador:
            msg = "Solo moderadores pueden iniciar grabación"
            raise PermissionError(msg)

        # Verificar que la videollamada permite grabación
        videollamada = crud_videollamada.get(self.db, id=self.videollamada_id)
        if not videollamada or not videollamada.configuracion.get(
            "permitir_grabacion", False
        ):
            msg = "Esta videollamada no permite grabaciones"
            raise PermissionError(msg)

        # Crear registro de grabación en BD
        from schemas.communication.videollamada_schemas import GrabacionCreate

        grabacion_data = GrabacionCreate(
            videollamada_id=self.videollamada_id,
            iniciado_por_usuario_id=str(self.usuario.id),
            url_grabacion=data.get("url_grabacion", ""),  # Se actualizará después
            duracion_segundos=0,  # Se actualizará al finalizar
            tamano_bytes=0,
        )

        grabacion = crud_videollamada_participante.agregar_grabacion(
            self.db, videollamada_id=self.videollamada_id, obj_in=grabacion_data
        )

        # Emitir evento
        await videollamada_ws_manager.emit_recording_started(
            videollamada_id=self.videollamada_id,
            grabacion_id=str(grabacion.id),
            iniciado_por_usuario_id=str(self.usuario.id),
        )

    async def _handle_stop_recording(self, data: dict[str, Any]) -> None:
        """Handler para detener grabación (solo moderadores)."""
        grabacion_id = data.get("grabacion_id")

        if not grabacion_id:
            msg = "grabacion_id requerido"
            raise ValueError(msg)

        # Verificar permisos
        participante = crud_videollamada_participante.get_participante(
            self.db,
            videollamada_id=self.videollamada_id,
            usuario_id=str(self.usuario.id),
        )

        if not participante or not participante.es_moderador:
            msg = "Solo moderadores pueden detener grabación"
            raise PermissionError(msg)

        # Actualizar grabación en BD
        from crud.communication.videollamada import crud_videollamada_grabacion

        grabacion = crud_videollamada_grabacion.get(self.db, id=grabacion_id)
        if grabacion:
            duracion = data.get("duracion_segundos", 0)

            crud_videollamada_grabacion.update(
                self.db,
                db_obj=grabacion,
                obj_in={
                    "duracion_segundos": duracion,
                    "url_grabacion": data.get("url_grabacion", grabacion.url_grabacion),
                    "tamano_bytes": data.get("tamano_bytes", grabacion.tamano_bytes),
                },
            )

            # Emitir evento
            await videollamada_ws_manager.emit_recording_stopped(
                videollamada_id=self.videollamada_id,
                grabacion_id=grabacion_id,
                detenido_por_usuario_id=str(self.usuario.id),
                duracion_segundos=duracion,
            )

    # ===============================
    # Handlers de Utilidad
    # ===============================

    async def _handle_get_participants_state(self, websocket: WebSocket) -> None:
        """Handler para obtener estado de todos los participantes."""
        participants = videollamada_ws_manager.get_active_participants(
            self.videollamada_id
        )

        states = {}
        for usuario_id in participants:
            state = videollamada_ws_manager.get_participant_state(
                self.videollamada_id, usuario_id
            )
            if state:
                states[usuario_id] = state

        await websocket.send_text(
            json.dumps(
                {
                    "type": "participants_state",
                    "videollamada_id": self.videollamada_id,
                    "participants": states,
                    "count": len(participants),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
        )

    async def _handle_ping(self, websocket: WebSocket) -> None:
        """Handler para ping/pong keep-alive."""
        await websocket.send_text(
            json.dumps({"type": "pong", "timestamp": datetime.now(UTC).isoformat()})
        )


async def websocket_videollamada_endpoint(
    websocket: WebSocket,
    videollamada_id: str,
    token: str | None = Query(None),
    db: Session = Depends(get_db),
) -> None:
    """Endpoint WebSocket para videollamadas.

    Args:
        websocket: Conexión WebSocket
        videollamada_id: ID de la videollamada
        token: Token JWT de autenticación
        db: Sesión de base de datos

    Usage:
        ws://localhost:8000/api/communication/videollamadas/ws/{videollamada_id}?token={jwt_token}
    """
    connection_id = None
    usuario = None

    try:
        # Autenticar usuario
        if not token:
            await websocket.close(code=1008, reason="Token requerido")
            return

        usuario = await get_current_user_websocket(token, db)
        if not usuario:
            await websocket.close(code=1008, reason="Authentication failed")
            return

        # Verificar que el usuario es participante de la videollamada
        participante = crud_videollamada_participante.get_participante(
            db, videollamada_id=videollamada_id, usuario_id=str(usuario.id)
        )

        if not participante:
            await websocket.close(
                code=1008, reason="No eres participante de esta videollamada"
            )
            return

        # Aceptar conexión WebSocket
        await websocket.accept()

        # Generar connection_id
        connection_id = (
            f"{usuario.id}_{videollamada_id}_{datetime.now(UTC).timestamp()}"
        )

        # Registrar en el manager
        await videollamada_ws_manager.join_videollamada(
            videollamada_id=videollamada_id,
            usuario_id=str(usuario.id),
            es_moderador=participante.es_moderador,
            metadata={
                "connection_id": connection_id,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
            },
        )

        # Crear handler
        handler = VideollamadaWebSocketHandler(db, usuario, videollamada_id)
        handler.connection_id = connection_id

        # Enviar mensaje de bienvenida
        await websocket.send_text(
            json.dumps(
                {
                    "type": "connected",
                    "videollamada_id": videollamada_id,
                    "usuario_id": str(usuario.id),
                    "connection_id": connection_id,
                    "es_moderador": participante.es_moderador,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
        )

        # Emitir evento de usuario unido
        await videollamada_ws_manager.emit_user_joined(
            db=db,
            videollamada_id=videollamada_id,
            usuario_id=str(usuario.id),
            participante=participante,
        )

        logger.info(
            f"WebSocket conectado: Usuario {usuario.id} en videollamada {videollamada_id}"
        )

        # Loop principal de mensajes
        while True:
            try:
                # Recibir mensaje del cliente
                data = await websocket.receive_text()
                message_data = json.loads(data)

                # Procesar mensaje
                await handler.handle_message(websocket, message_data)

            except WebSocketDisconnect:
                logger.info(f"Cliente desconectado: {usuario.id}")
                break

            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": "Formato de mensaje inválido. Se esperaba JSON.",
                        }
                    )
                )

            except Exception as e:
                logger.exception(f"Error en WebSocket loop: {e}")
                await websocket.send_text(
                    json.dumps({"type": "error", "message": str(e)})
                )

    except Exception as e:
        logger.exception(f"Error en websocket_videollamada_endpoint: {e}")
        with contextlib.suppress(builtins.BaseException):
            await websocket.close(code=1011, reason=str(e))

    finally:
        # Cleanup: desconectar usuario
        if usuario and videollamada_id:
            await videollamada_ws_manager.leave_videollamada(
                videollamada_id=videollamada_id, usuario_id=str(usuario.id)
            )

            # Emitir evento de usuario salido
            await videollamada_ws_manager.emit_user_left(
                videollamada_id=videollamada_id,
                usuario_id=str(usuario.id),
                razon="disconnect",
            )

            logger.info(
                f"WebSocket desconectado y limpiado: Usuario {usuario.id} "
                f"en videollamada {videollamada_id}"
            )
