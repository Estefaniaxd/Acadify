"""Sistema WebSocket para Videollamadas en Tiempo Real
Gestiona eventos de videollamadas: usuarios entrando/saliendo, estado de audio/video,
grabaciones, y sincronización de estado entre participantes.

Extiende el ConnectionManager base con funcionalidades específicas para videollamadas.
"""

from datetime import UTC, datetime
import logging
from typing import Any

from sqlalchemy.orm import Session

from models.communication.videollamada import Videollamada, VideollamadaParticipante
from services.websocket_manager import manager as base_manager


logger = logging.getLogger(__name__)


class VideollamadaEvents:
    """Tipos de eventos WebSocket para videollamadas.
    Documentación de cada evento con su estructura de payload.
    """

    # Eventos de ciclo de vida de llamada
    CALL_STARTED = "call_started"  # Llamada iniciada
    CALL_ENDED = "call_ended"  # Llamada finalizada
    CALL_CANCELLED = "call_cancelled"  # Llamada cancelada

    # Eventos de participantes
    USER_JOINED_CALL = "user_joined_call"  # Usuario se une a la llamada
    USER_LEFT_CALL = "user_left_call"  # Usuario sale de la llamada
    USER_RECONNECTING = "user_reconnecting"  # Usuario reconectando
    USER_RECONNECTED = "user_reconnected"  # Usuario reconectado

    # Eventos de audio/video
    PARTICIPANT_AUDIO_TOGGLED = (
        "participant_audio_toggled"  # Audio activado/desactivado
    )
    PARTICIPANT_VIDEO_TOGGLED = (
        "participant_video_toggled"  # Video activado/desactivado
    )
    PARTICIPANT_SCREENSHARE_TOGGLED = (
        "participant_screenshare_toggled"  # Compartir pantalla
    )

    # Eventos de grabación
    RECORDING_STARTED = "recording_started"  # Grabación iniciada
    RECORDING_STOPPED = "recording_stopped"  # Grabación detenida
    RECORDING_PAUSED = "recording_paused"  # Grabación pausada
    RECORDING_RESUMED = "recording_resumed"  # Grabación reanudada

    # Eventos de moderación
    MODERATOR_CHANGED = "moderator_changed"  # Cambio de moderador
    PARTICIPANT_MUTED = "participant_muted"  # Participante silenciado por moderador
    PARTICIPANT_REMOVED = "participant_removed"  # Participante expulsado
    PARTICIPANT_PROMOTED = "participant_promoted"  # Participante promovido a moderador

    # Eventos de estado
    CALL_STATE_UPDATED = "call_state_updated"  # Estado de llamada actualizado
    PARTICIPANT_STATE_UPDATED = (
        "participant_state_updated"  # Estado de participante actualizado
    )

    # Eventos de calidad
    QUALITY_WARNING = "quality_warning"  # Advertencia de calidad de conexión
    QUALITY_RECOVERED = "quality_recovered"  # Calidad recuperada

    # Eventos de chat en videollamada
    CALL_MESSAGE = "call_message"  # Mensaje en chat de videollamada


class VideollamadaWebSocketManager:
    """Gestor de WebSocket específico para videollamadas.
    Extiende ConnectionManager base con funcionalidades de videollamadas.
    """

    def __init__(self) -> None:
        # Reutilizar el ConnectionManager base
        self.base_manager = base_manager

        # {videollamada_id: Set[usuario_id]} - Participantes activos por videollamada
        self.videollamada_participants: dict[str, set[str]] = {}

        # {videollamada_id: Dict[usuario_id, estado]} - Estado de cada participante
        self.participant_states: dict[str, dict[str, dict[str, Any]]] = {}

        # {videollamada_id: metadata} - Metadata de videollamadas activas
        self.active_calls: dict[str, dict[str, Any]] = {}

        logger.info("VideollamadaWebSocketManager inicializado")

    # ===============================
    # Gestión de Conexiones
    # ===============================

    async def join_videollamada(
        self,
        videollamada_id: str,
        usuario_id: str,
        es_moderador: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Usuario se une a una videollamada.

        Args:
            videollamada_id: ID de la videollamada
            usuario_id: ID del usuario
            es_moderador: Si el usuario es moderador
            metadata: Información adicional del participante
        """
        # Agregar a participantes de la videollamada
        if videollamada_id not in self.videollamada_participants:
            self.videollamada_participants[videollamada_id] = set()

        self.videollamada_participants[videollamada_id].add(usuario_id)

        # Inicializar estado del participante
        if videollamada_id not in self.participant_states:
            self.participant_states[videollamada_id] = {}

        self.participant_states[videollamada_id][usuario_id] = {
            "audio_enabled": True,
            "video_enabled": True,
            "screenshare_enabled": False,
            "is_moderator": es_moderador,
            "joined_at": datetime.now(UTC).isoformat(),
            "connection_quality": "good",
            "is_reconnecting": False,
            "metadata": metadata or {},
        }

        # Incrementar contador en metadata de llamada activa
        if videollamada_id in self.active_calls:
            self.active_calls[videollamada_id]["participant_count"] += 1

        logger.info(
            f"Usuario {usuario_id} unido a videollamada {videollamada_id}. "
            f"Total participantes: {len(self.videollamada_participants[videollamada_id])}"
        )

    async def leave_videollamada(self, videollamada_id: str, usuario_id: str) -> None:
        """Usuario sale de una videollamada.

        Args:
            videollamada_id: ID de la videollamada
            usuario_id: ID del usuario
        """
        # Remover de participantes
        if videollamada_id in self.videollamada_participants:
            self.videollamada_participants[videollamada_id].discard(usuario_id)

            # Limpiar videollamada vacía
            if not self.videollamada_participants[videollamada_id]:
                del self.videollamada_participants[videollamada_id]

                # Limpiar metadata de llamada
                if videollamada_id in self.active_calls:
                    del self.active_calls[videollamada_id]

        # Remover estado del participante
        if videollamada_id in self.participant_states:
            if usuario_id in self.participant_states[videollamada_id]:
                del self.participant_states[videollamada_id][usuario_id]

            # Limpiar estados vacíos
            if not self.participant_states[videollamada_id]:
                del self.participant_states[videollamada_id]

        # Decrementar contador
        if videollamada_id in self.active_calls:
            self.active_calls[videollamada_id]["participant_count"] -= 1

        logger.info(f"Usuario {usuario_id} salió de videollamada {videollamada_id}")

    # ===============================
    # Eventos de Participantes
    # ===============================

    async def emit_user_joined(
        self,
        db: Session,
        videollamada_id: str,
        usuario_id: str,
        participante: VideollamadaParticipante,
    ) -> None:
        """Emitir evento cuando usuario se une a la llamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: ID de la videollamada
            usuario_id: ID del usuario que se unió
            participante: Instancia del participante
        """
        # Obtener estado actual del participante
        estado = self.participant_states.get(videollamada_id, {}).get(usuario_id, {})

        # Preparar payload del evento
        event_data = {
            "type": VideollamadaEvents.USER_JOINED_CALL,
            "videollamada_id": videollamada_id,
            "participante": {
                "id": str(participante.id),
                "usuario_id": usuario_id,
                "es_moderador": participante.es_moderador,
                "audio_enabled": estado.get("audio_enabled", True),
                "video_enabled": estado.get("video_enabled", True),
                "joined_at": estado.get("joined_at", datetime.now(UTC).isoformat()),
            },
            "participant_count": len(
                self.videollamada_participants.get(videollamada_id, set())
            ),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Broadcast a todos los participantes EXCEPTO el que se unió
        await self._broadcast_to_call(
            videollamada_id, event_data, exclude_user=usuario_id
        )

        logger.info(
            f"Evento USER_JOINED_CALL emitido para {usuario_id} en {videollamada_id}"
        )

    async def emit_user_left(
        self, videollamada_id: str, usuario_id: str, razon: str | None = None
    ) -> None:
        """Emitir evento cuando usuario sale de la llamada.

        Args:
            videollamada_id: ID de la videollamada
            usuario_id: ID del usuario que salió
            razon: Razón de la salida (opcional)
        """
        event_data = {
            "type": VideollamadaEvents.USER_LEFT_CALL,
            "videollamada_id": videollamada_id,
            "usuario_id": usuario_id,
            "razon": razon,
            "participant_count": len(
                self.videollamada_participants.get(videollamada_id, set())
            ),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Broadcast a todos los participantes restantes
        await self._broadcast_to_call(videollamada_id, event_data)

        logger.info(
            f"Evento USER_LEFT_CALL emitido para {usuario_id} en {videollamada_id}"
        )

    # ===============================
    # Eventos de Audio/Video
    # ===============================

    async def emit_audio_toggled(
        self,
        videollamada_id: str,
        usuario_id: str,
        enabled: bool,
        muted_by_moderator: bool = False,
    ) -> None:
        """Emitir evento cuando se activa/desactiva audio.

        Args:
            videollamada_id: ID de la videollamada
            usuario_id: ID del usuario
            enabled: True si se activó, False si se desactivó
            muted_by_moderator: Si fue silenciado por moderador
        """
        # Actualizar estado local
        if videollamada_id in self.participant_states:
            if usuario_id in self.participant_states[videollamada_id]:
                self.participant_states[videollamada_id][usuario_id][
                    "audio_enabled"
                ] = enabled

        event_data = {
            "type": VideollamadaEvents.PARTICIPANT_AUDIO_TOGGLED,
            "videollamada_id": videollamada_id,
            "usuario_id": usuario_id,
            "audio_enabled": enabled,
            "muted_by_moderator": muted_by_moderator,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        await self._broadcast_to_call(videollamada_id, event_data)

        logger.debug(f"Evento AUDIO_TOGGLED emitido: {usuario_id} audio={enabled}")

    async def emit_video_toggled(
        self, videollamada_id: str, usuario_id: str, enabled: bool
    ) -> None:
        """Emitir evento cuando se activa/desactiva video.

        Args:
            videollamada_id: ID de la videollamada
            usuario_id: ID del usuario
            enabled: True si se activó, False si se desactivó
        """
        # Actualizar estado local
        if videollamada_id in self.participant_states:
            if usuario_id in self.participant_states[videollamada_id]:
                self.participant_states[videollamada_id][usuario_id][
                    "video_enabled"
                ] = enabled

        event_data = {
            "type": VideollamadaEvents.PARTICIPANT_VIDEO_TOGGLED,
            "videollamada_id": videollamada_id,
            "usuario_id": usuario_id,
            "video_enabled": enabled,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        await self._broadcast_to_call(videollamada_id, event_data)

        logger.debug(f"Evento VIDEO_TOGGLED emitido: {usuario_id} video={enabled}")

    async def emit_screenshare_toggled(
        self, videollamada_id: str, usuario_id: str, enabled: bool
    ) -> None:
        """Emitir evento cuando se activa/desactiva compartir pantalla.

        Args:
            videollamada_id: ID de la videollamada
            usuario_id: ID del usuario
            enabled: True si se activó, False si se desactivó
        """
        # Actualizar estado local
        if videollamada_id in self.participant_states:
            if usuario_id in self.participant_states[videollamada_id]:
                self.participant_states[videollamada_id][usuario_id][
                    "screenshare_enabled"
                ] = enabled

        event_data = {
            "type": VideollamadaEvents.PARTICIPANT_SCREENSHARE_TOGGLED,
            "videollamada_id": videollamada_id,
            "usuario_id": usuario_id,
            "screenshare_enabled": enabled,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        await self._broadcast_to_call(videollamada_id, event_data)

        logger.info(
            f"Evento SCREENSHARE_TOGGLED emitido: {usuario_id} screenshare={enabled}"
        )

    # ===============================
    # Eventos de Grabación
    # ===============================

    async def emit_recording_started(
        self, videollamada_id: str, grabacion_id: str, iniciado_por_usuario_id: str
    ) -> None:
        """Emitir evento cuando se inicia grabación.

        Args:
            videollamada_id: ID de la videollamada
            grabacion_id: ID de la grabación
            iniciado_por_usuario_id: ID del usuario que inició
        """
        event_data = {
            "type": VideollamadaEvents.RECORDING_STARTED,
            "videollamada_id": videollamada_id,
            "grabacion_id": grabacion_id,
            "iniciado_por": iniciado_por_usuario_id,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        await self._broadcast_to_call(videollamada_id, event_data)

        logger.info(
            f"Evento RECORDING_STARTED emitido para videollamada {videollamada_id}"
        )

    async def emit_recording_stopped(
        self,
        videollamada_id: str,
        grabacion_id: str,
        detenido_por_usuario_id: str,
        duracion_segundos: int | None = None,
    ) -> None:
        """Emitir evento cuando se detiene grabación.

        Args:
            videollamada_id: ID de la videollamada
            grabacion_id: ID de la grabación
            detenido_por_usuario_id: ID del usuario que detuvo
            duracion_segundos: Duración de la grabación
        """
        event_data = {
            "type": VideollamadaEvents.RECORDING_STOPPED,
            "videollamada_id": videollamada_id,
            "grabacion_id": grabacion_id,
            "detenido_por": detenido_por_usuario_id,
            "duracion_segundos": duracion_segundos,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        await self._broadcast_to_call(videollamada_id, event_data)

        logger.info(
            f"Evento RECORDING_STOPPED emitido para videollamada {videollamada_id}"
        )

    # ===============================
    # Eventos de Ciclo de Vida
    # ===============================

    async def emit_call_started(self, db: Session, videollamada: Videollamada) -> None:
        """Emitir evento cuando se inicia una llamada.

        Args:
            db: Sesión de base de datos
            videollamada: Instancia de videollamada
        """
        videollamada_id = str(videollamada.id)

        # Registrar en llamadas activas
        self.active_calls[videollamada_id] = {
            "started_at": datetime.now(UTC).isoformat(),
            "participant_count": 0,
            "recording_active": False,
            "estado": videollamada.estado.value,
        }

        event_data = {
            "type": VideollamadaEvents.CALL_STARTED,
            "videollamada_id": videollamada_id,
            "titulo": videollamada.titulo,
            "tipo_llamada": videollamada.tipo_llamada.value,
            "jitsi_room_name": videollamada.jitsi_room_name,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Broadcast a sala de chat asociada (si existe)
        if videollamada.sala_chat_id:
            await self.base_manager.broadcast_to_sala(
                str(videollamada.sala_chat_id), event_data
            )

        logger.info(f"Evento CALL_STARTED emitido para videollamada {videollamada_id}")

    async def emit_call_ended(
        self,
        videollamada_id: str,
        finalizado_por_usuario_id: str | None = None,
        duracion_total_segundos: int | None = None,
        razon: str | None = None,
    ) -> None:
        """Emitir evento cuando finaliza una llamada.

        Args:
            videollamada_id: ID de la videollamada
            finalizado_por_usuario_id: ID del usuario que finalizó
            duracion_total_segundos: Duración total de la llamada
            razon: Razón de finalización
        """
        event_data = {
            "type": VideollamadaEvents.CALL_ENDED,
            "videollamada_id": videollamada_id,
            "finalizado_por": finalizado_por_usuario_id,
            "duracion_total_segundos": duracion_total_segundos,
            "razon": razon,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Broadcast a todos los participantes
        await self._broadcast_to_call(videollamada_id, event_data)

        # Limpiar recursos
        if videollamada_id in self.active_calls:
            del self.active_calls[videollamada_id]

        logger.info(f"Evento CALL_ENDED emitido para videollamada {videollamada_id}")

    # ===============================
    # Eventos de Moderación
    # ===============================

    async def emit_participant_muted(
        self, videollamada_id: str, usuario_id: str, muted_by_moderador_id: str
    ) -> None:
        """Emitir evento cuando moderador silencia a participante.

        Args:
            videollamada_id: ID de la videollamada
            usuario_id: ID del usuario silenciado
            muted_by_moderador_id: ID del moderador
        """
        event_data = {
            "type": VideollamadaEvents.PARTICIPANT_MUTED,
            "videollamada_id": videollamada_id,
            "usuario_id": usuario_id,
            "muted_by": muted_by_moderador_id,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        await self._broadcast_to_call(videollamada_id, event_data)

        # También emitir el toggle de audio
        await self.emit_audio_toggled(
            videollamada_id, usuario_id, enabled=False, muted_by_moderator=True
        )

        logger.info(
            f"Evento PARTICIPANT_MUTED emitido: {usuario_id} por {muted_by_moderador_id}"
        )

    async def emit_participant_removed(
        self,
        videollamada_id: str,
        usuario_id: str,
        removed_by_moderador_id: str,
        razon: str | None = None,
    ) -> None:
        """Emitir evento cuando moderador expulsa a participante.

        Args:
            videollamada_id: ID de la videollamada
            usuario_id: ID del usuario expulsado
            removed_by_moderador_id: ID del moderador
            razon: Razón de expulsión
        """
        event_data = {
            "type": VideollamadaEvents.PARTICIPANT_REMOVED,
            "videollamada_id": videollamada_id,
            "usuario_id": usuario_id,
            "removed_by": removed_by_moderador_id,
            "razon": razon,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Enviar notificación personal al expulsado
        await self.base_manager.send_personal_message(usuario_id, event_data)

        # Broadcast a los demás
        await self._broadcast_to_call(
            videollamada_id, event_data, exclude_user=usuario_id
        )

        logger.info(
            f"Evento PARTICIPANT_REMOVED emitido: {usuario_id} por {removed_by_moderador_id}"
        )

    # ===============================
    # Helpers Internos
    # ===============================

    async def _broadcast_to_call(
        self,
        videollamada_id: str,
        event_data: dict[str, Any],
        exclude_user: str | None = None,
    ) -> None:
        """Broadcast mensaje a todos los participantes de una videollamada.

        Args:
            videollamada_id: ID de la videollamada
            event_data: Datos del evento
            exclude_user: Usuario a excluir (opcional)
        """
        if videollamada_id not in self.videollamada_participants:
            logger.warning(f"No hay participantes en videollamada {videollamada_id}")
            return

        participants = self.videollamada_participants[videollamada_id].copy()
        if exclude_user:
            participants.discard(exclude_user)

        # Enviar a cada participante usando el base_manager
        for usuario_id in participants:
            try:
                await self.base_manager.send_personal_message(usuario_id, event_data)
            except Exception as e:
                logger.exception(f"Error enviando evento a {usuario_id}: {e}")

    # ===============================
    # Queries de Estado
    # ===============================

    def get_active_participants(self, videollamada_id: str) -> list[str]:
        """Obtener lista de participantes activos en una videollamada.

        Args:
            videollamada_id: ID de la videollamada

        Returns:
            Lista de IDs de usuarios activos
        """
        return list(self.videollamada_participants.get(videollamada_id, set()))

    def get_participant_state(
        self, videollamada_id: str, usuario_id: str
    ) -> dict[str, Any] | None:
        """Obtener estado de un participante específico.

        Args:
            videollamada_id: ID de la videollamada
            usuario_id: ID del usuario

        Returns:
            Diccionario con estado del participante o None
        """
        if videollamada_id not in self.participant_states:
            return None

        return self.participant_states[videollamada_id].get(usuario_id)

    def get_call_info(self, videollamada_id: str) -> dict[str, Any] | None:
        """Obtener información de una llamada activa.

        Args:
            videollamada_id: ID de la videollamada

        Returns:
            Diccionario con información de la llamada o None
        """
        return self.active_calls.get(videollamada_id)

    def is_call_active(self, videollamada_id: str) -> bool:
        """Verificar si una llamada está activa.

        Args:
            videollamada_id: ID de la videollamada

        Returns:
            True si la llamada está activa
        """
        return videollamada_id in self.active_calls


# Instancia global del gestor de videollamadas
videollamada_ws_manager = VideollamadaWebSocketManager()
