"""Service Layer para Videollamadas con Jitsi Meet.

Esta capa de servicios encapsula la lógica de negocio compleja y coordina
las operaciones entre CRUD, JWT generation, WebSocket events y validaciones.

Principios SOLID aplicados:
- Single Responsibility: Cada método maneja un caso de uso específico
- Open/Closed: Extensible mediante nuevos métodos sin modificar existentes
- Liskov Substitution: Interfaces consistentes y predecibles
- Interface Segregation: Métodos específicos por funcionalidad
- Dependency Inversion: Depende de abstracciones (CRUD, schemas) no implementaciones

Clean Code Principles:
- Nombres descriptivos y claros
- Funciones pequeñas con una responsabilidad
- Sin código duplicado (DRY)
- Manejo explícito de errores
- Logging comprehensivo
- Type hints completos

References:
    - Clean Architecture by Robert C. Martin
    - Domain-Driven Design by Eric Evans
"""

from datetime import datetime
import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# CRUD Operations
from src.crud.communication.videollamada import (
    crud_videollamada,
    crud_videollamada_grabacion,
    crud_videollamada_participante,
)

# Models
from src.models.communication.videollamada import (
    Videollamada,
)
from src.models.users import usuario as Usuario

# Schemas
from src.schemas.communication.videollamada_schemas import (
    ESTADO_ACTIVA,
    ESTADO_FINALIZADA,
    EstadisticasVideollamada,
    GrabacionResponse,
    ParticipanteCreate,
    ParticipanteResponse,
    UnirseVideollamadaResponse,
    VideollamadaCreate,
    VideollamadaDetallada,
)

# WebSocket Manager
from src.services.videollamada_websocket import videollamada_ws_manager

# JWT Generator
from src.utils.jitsi_jwt import generate_moderator_token, generate_participant_token


logger = logging.getLogger(__name__)


class VideollamadaService:
    """Servicio de lógica de negocio para videollamadas.

    Coordina operaciones complejas entre múltiples capas:
    - CRUD operations (base de datos)
    - JWT generation (autenticación Jitsi)
    - WebSocket events (tiempo real)
    - Validaciones de negocio
    - Logging y auditoría

    Attributes:
        db: Sesión de base de datos SQLAlchemy
    """

    def __init__(self, db: Session) -> None:
        """Inicializar servicio con sesión de base de datos.

        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
        logger.debug("VideollamadaService inicializado")

    # ===============================
    # Ciclo de Vida de Videollamadas
    # ===============================

    async def crear_videollamada_completa(
        self,
        videollamada_in: VideollamadaCreate,
        usuario_creador: Usuario,
        auto_unir_creador: bool = True,
    ) -> tuple[VideollamadaDetallada, str | None]:
        """Crear videollamada completa con todas las configuraciones.

        Operaciones realizadas:
        1. Validar datos de entrada
        2. Crear videollamada en BD
        3. Agregar creador como participante moderador (opcional)
        4. Generar JWT token para creador (opcional)
        5. Emitir evento WebSocket call_started
        6. Registrar en WebSocket manager

        Args:
            videollamada_in: Datos de la videollamada
            usuario_creador: Usuario que crea la llamada
            auto_unir_creador: Si True, une automáticamente al creador

        Returns:
            Tupla de (VideollamadaDetallada, jwt_token opcional)

        Raises:
            HTTPException: Si hay errores de validación o creación
        """
        try:
            logger.info(
                f"Creando videollamada '{videollamada_in.titulo}' "
                f"por usuario {usuario_creador.id}"
            )

            # 1. Validar configuración
            self._validar_configuracion_videollamada(videollamada_in)

            # 2. Crear videollamada en BD
            videollamada = crud_videollamada.create(db=self.db, obj_in=videollamada_in)

            jwt_token = None

            # 3. Auto-unir creador como moderador si se solicita
            if auto_unir_creador:
                participante_data = ParticipanteCreate(
                    usuario_id=str(usuario_creador.id),
                    es_moderador=True,
                    audio_activo=True,
                    video_activo=True,
                )

                crud_videollamada.agregar_participante(
                    db=self.db,
                    videollamada_id=str(videollamada.id),
                    obj_in=participante_data,
                )

                # 4. Generar JWT token para creador
                jwt_token = self._generar_jwt_token(
                    videollamada=videollamada,
                    usuario=usuario_creador,
                    es_moderador=True,
                )

                logger.info(
                    f"Creador {usuario_creador.id} unido como moderador a "
                    f"videollamada {videollamada.id}"
                )

            # 5. Emitir evento WebSocket
            await videollamada_ws_manager.emit_call_started(
                db=self.db, videollamada=videollamada
            )

            # 6. Convertir a schema detallado
            videollamada_detallada = self._convertir_a_detallada(videollamada)

            logger.info(f"✅ Videollamada {videollamada.id} creada exitosamente")

            return videollamada_detallada, jwt_token

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error creando videollamada: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear videollamada: {e!s}",
            ) from e

    async def unirse_a_videollamada(
        self, videollamada_id: UUID, usuario: Usuario, es_moderador: bool = False
    ) -> UnirseVideollamadaResponse:
        """Unir usuario a una videollamada existente.

        Operaciones realizadas:
        1. Validar que la videollamada existe y está activa
        2. Verificar que el usuario no está ya unido
        3. Validar capacidad máxima
        4. Agregar participante a BD
        5. Generar JWT token de Jitsi
        6. Registrar en WebSocket manager
        7. Emitir evento user_joined_call

        Args:
            videollamada_id: ID de la videollamada
            usuario: Usuario que se une
            es_moderador: Si es moderador de la llamada

        Returns:
            UnirseVideollamadaResponse con datos del participante y JWT

        Raises:
            HTTPException: Si no se puede unir por validaciones
        """
        try:
            logger.info(
                f"Usuario {usuario.id} uniéndose a videollamada {videollamada_id}"
            )

            # 1. Obtener y validar videollamada
            videollamada = self._obtener_videollamada_activa(videollamada_id)

            # 2. Verificar si ya está unido
            participante_existente = crud_videollamada_participante.get_participante(
                self.db,
                videollamada_id=str(videollamada_id),
                usuario_id=str(usuario.id),
            )

            if participante_existente and participante_existente.fecha_salida is None:
                logger.warning(
                    f"Usuario {usuario.id} ya está en videollamada {videollamada_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya estás participando en esta videollamada",
                )

            # 3. Validar capacidad máxima
            participantes_activos = crud_videollamada.get_participantes_activos(
                self.db, videollamada_id=str(videollamada_id)
            )

            max_participantes = videollamada.configuracion.get("max_participantes", 50)
            if len(participantes_activos) >= max_participantes:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"La videollamada ha alcanzado su capacidad máxima ({max_participantes})",
                )

            # 4. Agregar participante a BD
            participante_data = ParticipanteCreate(
                usuario_id=str(usuario.id),
                es_moderador=es_moderador,
                audio_activo=True,
                video_activo=True,
            )

            participante = crud_videollamada.agregar_participante(
                db=self.db,
                videollamada_id=str(videollamada_id),
                obj_in=participante_data,
            )

            # 5. Generar JWT token
            jwt_token = self._generar_jwt_token(
                videollamada=videollamada, usuario=usuario, es_moderador=es_moderador
            )

            # 6. Registrar en WebSocket manager
            await videollamada_ws_manager.join_videollamada(
                videollamada_id=str(videollamada_id),
                usuario_id=str(usuario.id),
                es_moderador=es_moderador,
                metadata={
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido,
                    "correo": usuario.correo,
                },
            )

            # 7. Emitir evento WebSocket
            await videollamada_ws_manager.emit_user_joined(
                db=self.db,
                videollamada_id=str(videollamada_id),
                usuario_id=str(usuario.id),
                participante=participante,
            )

            # 8. Construir response
            response = UnirseVideollamadaResponse(
                id=participante.id,
                videollamada_id=participante.videollamada_id,
                usuario_id=participante.usuario_id,
                es_moderador=participante.es_moderador,
                audio_activo=participante.audio_activo,
                video_activo=participante.video_activo,
                compartiendo_pantalla=participante.compartiendo_pantalla,
                fecha_entrada=participante.fecha_entrada,
                fecha_salida=participante.fecha_salida,
                jwt_token=jwt_token,
                jitsi_room_name=videollamada.jitsi_room_name,
            )

            logger.info(
                f"✅ Usuario {usuario.id} unido exitosamente a "
                f"videollamada {videollamada_id}"
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error uniendo a videollamada: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al unirse a videollamada: {e!s}",
            ) from e

    async def salir_de_videollamada(
        self, videollamada_id: UUID, usuario: Usuario, razon: str | None = None
    ) -> ParticipanteResponse:
        """Salir de una videollamada.

        Operaciones realizadas:
        1. Validar que el usuario está en la videollamada
        2. Actualizar fecha_salida en BD
        3. Desregistrar del WebSocket manager
        4. Emitir evento user_left_call
        5. Verificar si quedan participantes (finalizar si está vacía)

        Args:
            videollamada_id: ID de la videollamada
            usuario: Usuario que sale
            razon: Razón de salida (opcional)

        Returns:
            ParticipanteResponse con datos actualizados

        Raises:
            HTTPException: Si el usuario no está en la videollamada
        """
        try:
            logger.info(
                f"Usuario {usuario.id} saliendo de videollamada {videollamada_id}"
            )

            # 1. Obtener participante
            participante = crud_videollamada_participante.get_participante(
                self.db,
                videollamada_id=str(videollamada_id),
                usuario_id=str(usuario.id),
            )

            if not participante or participante.fecha_salida is not None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No estás participando en esta videollamada",
                )

            # 2. Remover participante (actualiza fecha_salida)
            participante_actualizado = crud_videollamada.remover_participante(
                db=self.db,
                videollamada_id=str(videollamada_id),
                usuario_id=str(usuario.id),
            )

            # 3. Desregistrar del WebSocket
            await videollamada_ws_manager.leave_videollamada(
                videollamada_id=str(videollamada_id), usuario_id=str(usuario.id)
            )

            # 4. Emitir evento
            await videollamada_ws_manager.emit_user_left(
                videollamada_id=str(videollamada_id),
                usuario_id=str(usuario.id),
                razon=razon or "disconnect",
            )

            # 5. Verificar si quedan participantes activos
            participantes_activos = crud_videollamada.get_participantes_activos(
                self.db, videollamada_id=str(videollamada_id)
            )

            if not participantes_activos:
                logger.info(
                    f"No quedan participantes activos en videollamada {videollamada_id}. "
                    "Finalizando automáticamente."
                )
                await self._finalizar_videollamada_automatica(videollamada_id)

            # 6. Convertir a response
            response = ParticipanteResponse(
                id=participante_actualizado.id,
                videollamada_id=participante_actualizado.videollamada_id,
                usuario_id=participante_actualizado.usuario_id,
                es_moderador=participante_actualizado.es_moderador,
                audio_activo=participante_actualizado.audio_activo,
                video_activo=participante_actualizado.video_activo,
                compartiendo_pantalla=participante_actualizado.compartiendo_pantalla,
                fecha_entrada=participante_actualizado.fecha_entrada,
                fecha_salida=participante_actualizado.fecha_salida,
            )

            logger.info(
                f"✅ Usuario {usuario.id} salió exitosamente de "
                f"videollamada {videollamada_id}"
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error saliendo de videollamada: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al salir de videollamada: {e!s}",
            ) from e

    async def finalizar_videollamada(
        self,
        videollamada_id: UUID,
        usuario_finalizador: Usuario,
        razon: str | None = None,
    ) -> VideollamadaDetallada:
        """Finalizar videollamada (solo moderadores/iniciador).

        Operaciones realizadas:
        1. Validar permisos de moderador
        2. Actualizar estado y fecha_fin en BD
        3. Calcular estadísticas finales
        4. Emitir evento call_ended a todos los participantes
        5. Desconectar todos los WebSocket
        6. Limpiar recursos del manager

        Args:
            videollamada_id: ID de la videollamada
            usuario_finalizador: Usuario que finaliza (debe ser moderador)
            razon: Razón de finalización

        Returns:
            VideollamadaDetallada con estado finalizado

        Raises:
            HTTPException: Si no tiene permisos o videollamada no existe
        """
        try:
            logger.info(
                f"Finalizando videollamada {videollamada_id} "
                f"por usuario {usuario_finalizador.id}"
            )

            # 1. Obtener videollamada
            videollamada = crud_videollamada.get(self.db, id=videollamada_id)
            if not videollamada:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Videollamada no encontrada",
                )

            # 2. Verificar permisos
            self._verificar_permisos_moderador(videollamada, usuario_finalizador)

            # 3. Verificar que no esté ya finalizada
            if videollamada.estado == ESTADO_FINALIZADA:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="La videollamada ya ha sido finalizada",
                )

            # 4. Calcular duración
            duracion_segundos = None
            if videollamada.fecha_inicio:
                duracion = datetime.utcnow() - videollamada.fecha_inicio
                duracion_segundos = int(duracion.total_seconds())

            # 5. Finalizar en BD
            videollamada_actualizada = crud_videollamada.finalizar(
                db=self.db, videollamada_id=str(videollamada_id)
            )

            # 6. Emitir evento call_ended
            await videollamada_ws_manager.emit_call_ended(
                videollamada_id=str(videollamada_id),
                finalizado_por_usuario_id=str(usuario_finalizador.id),
                duracion_total_segundos=duracion_segundos,
                razon=razon,
            )

            # 7. Desconectar todos los participantes del WebSocket
            participantes_activos = videollamada_ws_manager.get_active_participants(
                str(videollamada_id)
            )

            for usuario_id in participantes_activos:
                await videollamada_ws_manager.leave_videollamada(
                    videollamada_id=str(videollamada_id), usuario_id=usuario_id
                )

            # 8. Convertir a detallada
            videollamada_detallada = self._convertir_a_detallada(
                videollamada_actualizada
            )

            logger.info(
                f"✅ Videollamada {videollamada_id} finalizada exitosamente. "
                f"Duración: {duracion_segundos}s"
            )

            return videollamada_detallada

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error finalizando videollamada: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al finalizar videollamada: {e!s}",
            ) from e

    # ===============================
    # Gestión de Grabaciones
    # ===============================

    async def iniciar_grabacion(
        self,
        videollamada_id: UUID,
        usuario_iniciador: Usuario,
        url_grabacion: str | None = None,
    ) -> GrabacionResponse:
        """Iniciar grabación de videollamada (solo moderadores).

        Args:
            videollamada_id: ID de la videollamada
            usuario_iniciador: Usuario que inicia (debe ser moderador)
            url_grabacion: URL de la grabación (opcional, se puede actualizar después)

        Returns:
            GrabacionResponse con datos de la grabación

        Raises:
            HTTPException: Si no tiene permisos o grabación no permitida
        """
        try:
            logger.info(
                f"Iniciando grabación en videollamada {videollamada_id} "
                f"por usuario {usuario_iniciador.id}"
            )

            # 1. Obtener videollamada
            videollamada = self._obtener_videollamada_activa(videollamada_id)

            # 2. Verificar permisos
            self._verificar_permisos_moderador(videollamada, usuario_iniciador)

            # 3. Verificar que la grabación está permitida
            if not videollamada.configuracion.get("permitir_grabacion", False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Esta videollamada no permite grabaciones",
                )

            # 4. Crear grabación en BD
            grabacion_data = GrabacionCreate(
                videollamada_id=videollamada_id,
                iniciado_por_usuario_id=str(usuario_iniciador.id),
                url_grabacion=url_grabacion or "",
                duracion_segundos=0,
                tamano_bytes=0,
            )

            grabacion = crud_videollamada.agregar_grabacion(
                db=self.db, videollamada_id=str(videollamada_id), obj_in=grabacion_data
            )

            # 5. Emitir evento WebSocket
            await videollamada_ws_manager.emit_recording_started(
                videollamada_id=str(videollamada_id),
                grabacion_id=str(grabacion.id),
                iniciado_por_usuario_id=str(usuario_iniciador.id),
            )

            # 6. Convertir a response
            response = GrabacionResponse(
                id=grabacion.id,
                videollamada_id=grabacion.videollamada_id,
                iniciado_por_usuario_id=grabacion.iniciado_por_usuario_id,
                fecha_inicio=grabacion.fecha_inicio,
                fecha_fin=grabacion.fecha_fin,
                duracion_segundos=grabacion.duracion_segundos,
                url_grabacion=grabacion.url_grabacion,
                tamano_bytes=grabacion.tamano_bytes,
            )

            logger.info(f"✅ Grabación {grabacion.id} iniciada exitosamente")

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error iniciando grabación: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al iniciar grabación: {e!s}",
            ) from e

    async def detener_grabacion(
        self,
        videollamada_id: UUID,
        grabacion_id: UUID,
        usuario_detenedor: Usuario,
        url_grabacion: str | None = None,
        tamano_bytes: int | None = None,
    ) -> GrabacionResponse:
        """Detener grabación de videollamada (solo moderadores).

        Args:
            videollamada_id: ID de la videollamada
            grabacion_id: ID de la grabación
            usuario_detenedor: Usuario que detiene (debe ser moderador)
            url_grabacion: URL final de la grabación
            tamano_bytes: Tamaño del archivo

        Returns:
            GrabacionResponse con datos finales

        Raises:
            HTTPException: Si no tiene permisos o grabación no existe
        """
        try:
            logger.info(
                f"Deteniendo grabación {grabacion_id} en videollamada {videollamada_id}"
            )

            # 1. Obtener videollamada y verificar permisos
            videollamada = crud_videollamada.get(self.db, id=videollamada_id)
            if not videollamada:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Videollamada no encontrada",
                )

            self._verificar_permisos_moderador(videollamada, usuario_detenedor)

            # 2. Obtener grabación
            grabacion = crud_videollamada_grabacion.get(self.db, id=grabacion_id)
            if not grabacion or str(grabacion.videollamada_id) != str(videollamada_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Grabación no encontrada",
                )

            # 3. Verificar que no esté ya detenida
            if grabacion.fecha_fin is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="La grabación ya ha sido detenida",
                )

            # 4. Calcular duración
            duracion = datetime.utcnow() - grabacion.fecha_inicio
            duracion_segundos = int(duracion.total_seconds())

            # 5. Actualizar grabación en BD
            grabacion_actualizada = crud_videollamada_grabacion.update(
                db=self.db,
                db_obj=grabacion,
                obj_in={
                    "fecha_fin": datetime.utcnow(),
                    "duracion_segundos": duracion_segundos,
                    "url_grabacion": url_grabacion or grabacion.url_grabacion,
                    "tamano_bytes": tamano_bytes or grabacion.tamano_bytes,
                },
            )

            # 6. Emitir evento WebSocket
            await videollamada_ws_manager.emit_recording_stopped(
                videollamada_id=str(videollamada_id),
                grabacion_id=str(grabacion_id),
                detenido_por_usuario_id=str(usuario_detenedor.id),
                duracion_segundos=duracion_segundos,
            )

            # 7. Convertir a response
            response = GrabacionResponse(
                id=grabacion_actualizada.id,
                videollamada_id=grabacion_actualizada.videollamada_id,
                iniciado_por_usuario_id=grabacion_actualizada.iniciado_por_usuario_id,
                fecha_inicio=grabacion_actualizada.fecha_inicio,
                fecha_fin=grabacion_actualizada.fecha_fin,
                duracion_segundos=grabacion_actualizada.duracion_segundos,
                url_grabacion=grabacion_actualizada.url_grabacion,
                tamano_bytes=grabacion_actualizada.tamano_bytes,
            )

            logger.info(
                f"✅ Grabación {grabacion_id} detenida. Duración: {duracion_segundos}s"
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error deteniendo grabación: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al detener grabación: {e!s}",
            ) from e

    # ===============================
    # Estadísticas y Consultas
    # ===============================

    def obtener_estadisticas(self, videollamada_id: UUID) -> EstadisticasVideollamada:
        """Obtener estadísticas completas de una videollamada.

        Args:
            videollamada_id: ID de la videollamada

        Returns:
            EstadisticasVideollamada con métricas completas

        Raises:
            HTTPException: Si videollamada no existe
        """
        try:
            videollamada = crud_videollamada.get(self.db, id=videollamada_id)
            if not videollamada:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Videollamada no encontrada",
                )

            # Obtener participantes
            participantes = crud_videollamada.get_participantes(
                self.db, videollamada_id=str(videollamada_id)
            )

            participantes_activos = [p for p in participantes if p.fecha_salida is None]

            # Obtener grabaciones
            grabaciones = crud_videollamada.get_grabaciones(
                self.db, videollamada_id=str(videollamada_id)
            )

            # Calcular duración
            duracion_segundos = 0
            if videollamada.fecha_inicio:
                fecha_fin = videollamada.fecha_fin or datetime.utcnow()
                duracion = fecha_fin - videollamada.fecha_inicio
                duracion_segundos = int(duracion.total_seconds())

            # Construir estadísticas
            return EstadisticasVideollamada(
                videollamada_id=videollamada.id,
                total_participantes=len(participantes),
                participantes_activos=len(participantes_activos),
                duracion_total_segundos=duracion_segundos,
                total_grabaciones=len(grabaciones),
                estado=videollamada.estado.value,
                fecha_inicio=videollamada.fecha_inicio,
                fecha_fin=videollamada.fecha_fin,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo estadísticas: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener estadísticas: {e!s}",
            ) from e

    # ===============================
    # Métodos Privados (Helpers)
    # ===============================

    def _validar_configuracion_videollamada(
        self, videollamada_in: VideollamadaCreate
    ) -> None:
        """Validar configuración de videollamada.

        Args:
            videollamada_in: Datos de entrada

        Raises:
            HTTPException: Si la configuración es inválida
        """
        config = videollamada_in.configuracion or {}

        # Validar max_participantes
        max_participantes = config.get("max_participantes", 50)
        if max_participantes < 2 or max_participantes > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_participantes debe estar entre 2 y 500",
            )

        # Validar que jitsi_room_name no esté en uso (si se especifica)
        if videollamada_in.jitsi_room_name:
            existing = crud_videollamada.get_by_room_name(
                self.db, room_name=videollamada_in.jitsi_room_name
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe una videollamada con el room name '{videollamada_in.jitsi_room_name}'",
                )

    def _obtener_videollamada_activa(self, videollamada_id: UUID) -> Videollamada:
        """Obtener videollamada y validar que esté activa.

        Args:
            videollamada_id: ID de la videollamada

        Returns:
            Videollamada activa

        Raises:
            HTTPException: Si no existe o no está activa
        """
        videollamada = crud_videollamada.get(self.db, id=videollamada_id)

        if not videollamada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Videollamada no encontrada",
            )

        if videollamada.estado != ESTADO_ACTIVA:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La videollamada está en estado '{videollamada.estado}' y no acepta nuevos participantes. Debe estar en estado 'activa'.",
            )

        return videollamada

    def _verificar_permisos_moderador(
        self, videollamada: Videollamada, usuario: Usuario
    ) -> None:
        """Verificar que el usuario tiene permisos de moderador.

        Args:
            videollamada: Videollamada
            usuario: Usuario a verificar

        Raises:
            HTTPException: Si no tiene permisos
        """
        # Verificar si es el iniciador
        if videollamada.iniciador_usuario_id == usuario.id:
            return

        # Verificar si es moderador
        participante = crud_videollamada_participante.get_participante(
            self.db, videollamada_id=str(videollamada.id), usuario_id=str(usuario.id)
        )

        if not participante or not participante.es_moderador:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos de moderador para esta acción",
            )

    def _generar_jwt_token(
        self, videollamada: Videollamada, usuario: Usuario, es_moderador: bool
    ) -> str:
        """Generar JWT token para Jitsi Meet.

        Args:
            videollamada: Videollamada
            usuario: Usuario
            es_moderador: Si es moderador

        Returns:
            JWT token string
        """
        if es_moderador:
            token = generate_moderator_token(
                room_name=videollamada.jitsi_room_name,
                user_id=str(usuario.id),
                user_name=f"{usuario.nombre} {usuario.apellido}",
                email=usuario.correo,
                expiry_hours=24,
            )
        else:
            token = generate_participant_token(
                room_name=videollamada.jitsi_room_name,
                user_id=str(usuario.id),
                user_name=f"{usuario.nombre} {usuario.apellido}",
                email=usuario.correo,
                expiry_hours=24,
            )

        return token

    def _convertir_a_detallada(
        self, videollamada: Videollamada
    ) -> VideollamadaDetallada:
        """Convertir modelo a schema detallado.

        Args:
            videollamada: Instancia del modelo

        Returns:
            VideollamadaDetallada schema
        """
        # Obtener participantes
        participantes = crud_videollamada.get_participantes(
            self.db, videollamada_id=str(videollamada.id)
        )

        participantes_response = [
            ParticipanteResponse(
                id=p.id,
                videollamada_id=p.videollamada_id,
                usuario_id=p.usuario_id,
                es_moderador=p.es_moderador,
                audio_activo=p.audio_activo,
                video_activo=p.video_activo,
                compartiendo_pantalla=p.compartiendo_pantalla,
                fecha_entrada=p.fecha_entrada,
                fecha_salida=p.fecha_salida,
            )
            for p in participantes
        ]

        # Obtener grabaciones
        grabaciones = crud_videollamada.get_grabaciones(
            self.db, videollamada_id=str(videollamada.id)
        )

        grabaciones_response = [
            GrabacionResponse(
                id=g.id,
                videollamada_id=g.videollamada_id,
                iniciado_por_usuario_id=g.iniciado_por_usuario_id,
                fecha_inicio=g.fecha_inicio,
                fecha_fin=g.fecha_fin,
                duracion_segundos=g.duracion_segundos,
                url_grabacion=g.url_grabacion,
                tamano_bytes=g.tamano_bytes,
            )
            for g in grabaciones
        ]

        return VideollamadaDetallada(
            id=videollamada.id,
            sala_chat_id=videollamada.sala_chat_id,
            iniciador_usuario_id=videollamada.iniciador_usuario_id,
            tipo_llamada=videollamada.tipo_llamada.value,
            estado=videollamada.estado.value,
            titulo=videollamada.titulo,
            descripcion=videollamada.descripcion,
            jitsi_room_name=videollamada.jitsi_room_name,
            fecha_programada=videollamada.fecha_programada,
            fecha_inicio=videollamada.fecha_inicio,
            fecha_fin=videollamada.fecha_fin,
            configuracion=videollamada.configuracion,
            metadatos=videollamada.metadatos,
            transcripcion=videollamada.transcripcion,
            fecha_creacion=videollamada.fecha_creacion,
            fecha_actualizacion=videollamada.fecha_actualizacion,
            participantes=participantes_response,
            grabaciones=grabaciones_response,
        )

    async def _finalizar_videollamada_automatica(self, videollamada_id: UUID) -> None:
        """Finalizar videollamada automáticamente (sin participantes).

        Args:
            videollamada_id: ID de la videollamada
        """
        try:
            videollamada = crud_videollamada.finalizar(
                db=self.db, videollamada_id=str(videollamada_id)
            )

            # Calcular duración
            duracion_segundos = None
            if videollamada.fecha_inicio:
                duracion = datetime.utcnow() - videollamada.fecha_inicio
                duracion_segundos = int(duracion.total_seconds())

            # Emitir evento
            await videollamada_ws_manager.emit_call_ended(
                videollamada_id=str(videollamada_id),
                finalizado_por_usuario_id=None,
                duracion_total_segundos=duracion_segundos,
                razon="no_participants",
            )

            logger.info(
                f"Videollamada {videollamada_id} finalizada automáticamente "
                "(sin participantes)"
            )

        except Exception as e:
            logger.exception(f"Error finalizando videollamada automáticamente: {e}")


# ===============================
# Factory Function
# ===============================


def get_videollamada_service(db: Session) -> VideollamadaService:
    """Factory function para obtener instancia del servicio.

    Args:
        db: Sesión de base de datos

    Returns:
        VideollamadaService instanciado
    """
    return VideollamadaService(db)
