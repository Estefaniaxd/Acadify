"""Service layer para el sistema de videollamadas con Jitsi.

Este módulo implementa la lógica de negocio para videollamadas,
siguiendo principios SOLID y Clean Code.

Principios aplicados:
- Single Responsibility: Cada método tiene una responsabilidad clara
- Open/Closed: Extensible mediante herencia sin modificar código existente
- Liskov Substitution: Interfaces consistentes
- Interface Segregation: Métodos específicos por funcionalidad
- Dependency Inversion: Dependemos de abstracciones (CRUD, schemas)

Author: AI Assistant
Date: 2025-11-01
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from src.crud.communication.videollamada import crud_videollamada
from src.enums.communication.videollamada_enums import (
    CalidadConexion,
    EstadoVideollamada,
)
from src.models.communication.videollamada import (
    VideollamadaParticipante,
)
from src.schemas.communication.videollamada_schemas import (
    GrabacionCreate,
    GrabacionResponse,
    ParticipanteResponse,
    VideollamadaCreate,
    VideollamadaDetallada,
    VideollamadaResponse,
)


class VideollamadaServiceError(Exception):
    """Excepción base para errores del servicio de videollamadas."""


class VideollamadaNotFoundError(VideollamadaServiceError):
    """Excepción cuando no se encuentra una videollamada."""


class VideollamadaStateError(VideollamadaServiceError):
    """Excepción cuando se intenta una operación en un estado inválido."""


class ParticipanteError(VideollamadaServiceError):
    """Excepción relacionada con participantes."""


def now_utc() -> datetime:
    """Retorna datetime actual con timezone UTC."""
    return datetime.now(UTC)


class VideollamadaService:
    """Servicio de videollamadas con lógica de negocio.

    Responsabilidades:
    - Crear videollamadas con tokens JWT para Jitsi
    - Gestionar participantes (unirse, salir, actualizar)
    - Controlar estados y transiciones
    - Integrar con grabaciones y transcripciones
    - Validar reglas de negocio
    """

    def __init__(self) -> None:
        """Inicializar servicio."""
        self.crud = crud_videollamada

    # ==================== CREAR Y OBTENER VIDEOLLAMADAS ====================

    def crear_videollamada(
        self, db: Session, *, videollamada_in: VideollamadaCreate, iniciador_id: UUID
    ) -> VideollamadaResponse:
        """Crear una nueva videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_in: Datos de creación validados por Pydantic
            iniciador_id: UUID del usuario que inicia la llamada

        Returns:
            VideollamadaResponse: Videollamada creada con datos completos

        Raises:
            VideollamadaServiceError: Si hay error en creación

        Business Rules:
            - El iniciador se agrega automáticamente como primer participante
            - El iniciador recibe privilegios de moderador
            - Estado inicial siempre es ACTIVA
        """
        try:
            # Crear videollamada usando CRUD
            videollamada = self.crud.create_videollamada(
                db=db,
                jitsi_room_name=videollamada_in.jitsi_room_name,
                tipo_llamada=videollamada_in.tipo_llamada,
                iniciador_id=iniciador_id,
                sala_chat_id=videollamada_in.sala_chat_id,
                configuracion=videollamada_in.configuracion,
            )

            # Convertir a schema de respuesta
            return VideollamadaResponse.model_validate(videollamada)

        except ValueError as e:
            msg = f"Error al crear videollamada: {e!s}"
            raise VideollamadaServiceError(msg) from e
        except Exception as e:
            msg = f"Error inesperado: {e!s}"
            raise VideollamadaServiceError(msg) from e

    def obtener_videollamada(
        self, db: Session, videollamada_id: UUID, *, incluir_participantes: bool = False
    ) -> VideollamadaResponse | VideollamadaDetallada:
        """Obtener videollamada por ID.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            incluir_participantes: Si debe cargar participantes y grabaciones

        Returns:
            VideollamadaResponse o VideollamadaDetallada según incluir_participantes

        Raises:
            VideollamadaNotFoundError: Si no existe la videollamada
        """
        if incluir_participantes:
            videollamada = self.crud.get_with_participants(db, videollamada_id)
        else:
            videollamada = self.crud.get(db, videollamada_id)

        if not videollamada:
            msg = f"Videollamada {videollamada_id} no encontrada"
            raise VideollamadaNotFoundError(msg)

        if incluir_participantes:
            return VideollamadaDetallada.model_validate(videollamada)
        return VideollamadaResponse.model_validate(videollamada)

    def listar_videollamadas_activas(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[VideollamadaResponse]:
        """Listar videollamadas activas.

        Args:
            db: Sesión de base de datos
            skip: Registros a saltar (paginación)
            limit: Límite de registros

        Returns:
            List[VideollamadaResponse]: Lista de videollamadas activas
        """
        videollamadas = self.crud.get_activas(db, skip=skip, limit=limit)
        return [VideollamadaResponse.model_validate(v) for v in videollamadas]

    def listar_videollamadas_por_sala_chat(
        self, db: Session, sala_chat_id: UUID, *, incluir_finalizadas: bool = False
    ) -> list[VideollamadaResponse]:
        """Listar videollamadas de una sala de chat.

        Args:
            db: Sesión de base de datos
            sala_chat_id: UUID de la sala de chat
            incluir_finalizadas: Si incluir llamadas finalizadas/canceladas

        Returns:
            List[VideollamadaResponse]: Lista de videollamadas
        """
        videollamadas = self.crud.get_by_sala_chat(
            db, sala_chat_id, incluir_finalizadas=incluir_finalizadas
        )
        return [VideollamadaResponse.model_validate(v) for v in videollamadas]

    # ==================== GESTIÓN DE PARTICIPANTES ====================

    def unirse_a_videollamada(
        self,
        db: Session,
        *,
        videollamada_id: UUID,
        usuario_id: UUID,
        es_moderador: bool = False,
    ) -> ParticipanteResponse:
        """Agregar participante a videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            usuario_id: UUID del usuario que se une
            es_moderador: Si tiene privilegios de moderador

        Returns:
            ParticipanteResponse: Participante agregado

        Raises:
            VideollamadaNotFoundError: Si no existe la videollamada
            VideollamadaStateError: Si la videollamada no está activa
            ParticipanteError: Si el usuario ya está en la llamada

        Business Rules:
            - Solo se puede unir a llamadas en estado ACTIVA
            - No se permite duplicar participantes
        """
        try:
            participante = self.crud.agregar_participante(
                db=db,
                videollamada_id=videollamada_id,
                usuario_id=usuario_id,
                es_moderador=es_moderador,
            )

            return ParticipanteResponse.model_validate(participante)

        except ValueError as e:
            error_msg = str(e)
            if "no encontrada" in error_msg:
                raise VideollamadaNotFoundError(error_msg) from e
            if "no está activa" in error_msg:
                raise VideollamadaStateError(error_msg) from e
            if "ya está en la videollamada" in error_msg:
                raise ParticipanteError(error_msg) from e
            raise VideollamadaServiceError(error_msg) from e

    def salir_de_videollamada(
        self, db: Session, *, videollamada_id: UUID, usuario_id: UUID
    ) -> ParticipanteResponse | None:
        """Remover participante de videollamada (marcar fecha_salida).

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            usuario_id: UUID del usuario que sale

        Returns:
            Optional[ParticipanteResponse]: Participante actualizado o None

        Business Rules:
            - Se calcula automáticamente la duración de participación
            - No se elimina el registro, solo se marca fecha_salida
        """
        participante = self.crud.remover_participante(
            db=db, videollamada_id=videollamada_id, usuario_id=usuario_id
        )

        if participante:
            return ParticipanteResponse.model_validate(participante)
        return None

    def obtener_participantes_activos(
        self, db: Session, videollamada_id: UUID
    ) -> list[ParticipanteResponse]:
        """Obtener participantes activos en una videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada

        Returns:
            List[ParticipanteResponse]: Lista de participantes sin fecha_salida
        """
        participantes = self.crud.get_participantes_activos(db, videollamada_id)
        return [ParticipanteResponse.model_validate(p) for p in participantes]

    def actualizar_calidad_conexion(
        self,
        db: Session,
        *,
        participante_id: UUID,
        calidad: CalidadConexion,
        latencia_ms: float | None = None,
        perdida_paquetes_pct: float | None = None,
    ) -> ParticipanteResponse:
        """Actualizar calidad de conexión de un participante.

        Args:
            db: Sesión de base de datos
            participante_id: UUID del participante
            calidad: Enum de calidad de conexión
            latencia_ms: Latencia en milisegundos (opcional)
            perdida_paquetes_pct: Porcentaje de pérdida de paquetes (opcional)

        Returns:
            ParticipanteResponse: Participante actualizado

        Business Rules:
            - Si se proporcionan métricas, se puede calcular calidad automáticamente
            - Se guarda en datos_conexion para análisis posterior
        """
        from src.crud.base import CRUDBase

        crud_participante = CRUDBase(VideollamadaParticipante, id_field="id")

        participante = crud_participante.get(db, participante_id)
        if not participante:
            msg = f"Participante {participante_id} no encontrado"
            raise ParticipanteError(msg)

        # Si se proporcionan métricas, calcular calidad automáticamente
        if latencia_ms is not None and perdida_paquetes_pct is not None:
            calidad = CalidadConexion.desde_metricas(latencia_ms, perdida_paquetes_pct)

        # Actualizar datos
        participante.calidad_conexion = calidad

        # Guardar métricas en datos_conexion
        if latencia_ms or perdida_paquetes_pct:
            datos = participante.datos_conexion or {}
            if latencia_ms:
                datos["latencia_ms"] = latencia_ms
            if perdida_paquetes_pct:
                datos["perdida_paquetes_pct"] = perdida_paquetes_pct
            datos["timestamp"] = now_utc().isoformat()
            participante.datos_conexion = datos

        db.add(participante)
        db.commit()
        db.refresh(participante)

        return ParticipanteResponse.model_validate(participante)

    # ==================== CONTROL DE ESTADO ====================

    def finalizar_videollamada(
        self, db: Session, videollamada_id: UUID, *, resumen_ia: str | None = None
    ) -> VideollamadaResponse:
        """Finalizar una videollamada activa.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            resumen_ia: Resumen generado por IA (opcional)

        Returns:
            VideollamadaResponse: Videollamada finalizada

        Raises:
            VideollamadaNotFoundError: Si no existe
            VideollamadaStateError: Si no está en estado ACTIVA

        Business Rules:
            - Solo se puede finalizar si estado = ACTIVA
            - Valida transición de estado usando enum.puede_transicionar_a()
            - Todos los participantes activos son removidos automáticamente
            - Se calcula duración total
        """
        # Verificar transición de estado válida
        videollamada = self.crud.get(db, videollamada_id)
        if not videollamada:
            msg = f"Videollamada {videollamada_id} no encontrada"
            raise VideollamadaNotFoundError(msg)

        # Validar transición usando método del enum
        if not videollamada.estado.puede_transicionar_a(EstadoVideollamada.FINALIZADA):
            msg = f"No se puede finalizar videollamada en estado {videollamada.estado.value}"
            raise VideollamadaStateError(msg)

        try:
            videollamada = self.crud.finalizar_llamada(
                db, videollamada_id, resumen_ia=resumen_ia
            )

            if not videollamada:
                msg = "Error al finalizar videollamada"
                raise VideollamadaServiceError(msg)

            return VideollamadaResponse.model_validate(videollamada)

        except ValueError as e:
            raise VideollamadaStateError(str(e)) from e

    def cancelar_videollamada(
        self, db: Session, videollamada_id: UUID
    ) -> VideollamadaResponse:
        """Cancelar una videollamada activa.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada

        Returns:
            VideollamadaResponse: Videollamada cancelada

        Raises:
            VideollamadaNotFoundError: Si no existe
            VideollamadaStateError: Si transición no es válida

        Business Rules:
            - Se puede cancelar desde ACTIVA
            - Valida transición usando enum
        """
        # Verificar transición
        videollamada = self.crud.get(db, videollamada_id)
        if not videollamada:
            msg = f"Videollamada {videollamada_id} no encontrada"
            raise VideollamadaNotFoundError(msg)

        if not videollamada.estado.puede_transicionar_a(EstadoVideollamada.CANCELADA):
            msg = f"No se puede cancelar videollamada en estado {videollamada.estado.value}"
            raise VideollamadaStateError(msg)

        videollamada = self.crud.cancelar_llamada(db, videollamada_id)

        if not videollamada:
            msg = "Error al cancelar videollamada"
            raise VideollamadaServiceError(msg)

        return VideollamadaResponse.model_validate(videollamada)

    # ==================== GRABACIONES ====================

    def agregar_grabacion(
        self, db: Session, *, videollamada_id: UUID, grabacion_in: GrabacionCreate
    ) -> GrabacionResponse:
        """Agregar grabación a videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            grabacion_in: Datos de la grabación validados

        Returns:
            GrabacionResponse: Grabación creada

        Business Rules:
            - Primera grabación se establece como principal en videollamada.grabacion_url
            - Estado inicial es COMPLETADO por defecto
        """
        try:
            grabacion = self.crud.agregar_grabacion(
                db=db,
                videollamada_id=videollamada_id,
                archivo_url=grabacion_in.archivo_url,
                formato=grabacion_in.formato,
                duracion_segundos=grabacion_in.duracion_segundos,
                tamano_bytes=grabacion_in.tamano_bytes,
                calidad=grabacion_in.calidad,
                thumbnail_url=grabacion_in.thumbnail_url,
                metadatos=grabacion_in.metadatos,
            )

            return GrabacionResponse.model_validate(grabacion)

        except Exception as e:
            msg = f"Error al agregar grabación: {e!s}"
            raise VideollamadaServiceError(msg) from e

    def obtener_grabaciones(
        self, db: Session, videollamada_id: UUID
    ) -> list[GrabacionResponse]:
        """Obtener todas las grabaciones de una videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada

        Returns:
            List[GrabacionResponse]: Lista de grabaciones
        """
        grabaciones = self.crud.get_grabaciones(db, videollamada_id)
        return [GrabacionResponse.model_validate(g) for g in grabaciones]

    # ==================== TRANSCRIPCIONES ====================

    def actualizar_transcripcion(
        self, db: Session, videollamada_id: UUID, transcripcion: str
    ) -> VideollamadaResponse:
        """Actualizar transcripción de videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            transcripcion: Texto de transcripción

        Returns:
            VideollamadaResponse: Videollamada actualizada

        Raises:
            VideollamadaNotFoundError: Si no existe
        """
        videollamada = self.crud.actualizar_transcripcion(
            db, videollamada_id, transcripcion
        )

        if not videollamada:
            msg = f"Videollamada {videollamada_id} no encontrada"
            raise VideollamadaNotFoundError(msg)

        return VideollamadaResponse.model_validate(videollamada)

    # ==================== UTILIDADES ====================

    def obtener_room_name_disponible(self, db: Session, base_name: str) -> str:
        """Generar nombre de sala Jitsi único.

        Args:
            db: Sesión de base de datos
            base_name: Nombre base para la sala

        Returns:
            str: Nombre único de sala (con sufijo numérico si es necesario)

        Business Rules:
            - Convierte a minúsculas y reemplaza espacios por guiones
            - Si existe, agrega sufijo numérico incremental
        """
        import re
        import unicodedata

        # Normalizar Unicode: convertir acentos (á→a, é→e, etc.)
        normalized = unicodedata.normalize('NFKD', base_name)
        ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
        
        # Normalizar: minúsculas, solo alfanuméricos y guiones
        room_name = ascii_name.lower()
        room_name = re.sub(r"[^a-z0-9-]", "-", room_name)
        room_name = re.sub(r"-+", "-", room_name).strip("-")

        # Verificar disponibilidad
        original_name = room_name
        counter = 1

        while self.crud.get_by_room_name(db, room_name):
            room_name = f"{original_name}-{counter}"
            counter += 1

        return room_name

    def validar_puede_unirse(
        self, db: Session, videollamada_id: UUID, usuario_id: UUID
    ) -> dict[str, Any]:
        """Validar si un usuario puede unirse a una videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            usuario_id: UUID del usuario

        Returns:
            Dict con:
                - puede_unirse: bool
                - razon: str (si no puede unirse)
                - videollamada: VideollamadaResponse (si puede unirse)
        """
        try:
            videollamada = self.crud.get(db, videollamada_id)

            if not videollamada:
                return {"puede_unirse": False, "razon": "Videollamada no encontrada"}

            if videollamada.estado != EstadoVideollamada.ACTIVA:
                return {
                    "puede_unirse": False,
                    "razon": f"Videollamada en estado {videollamada.estado.value}",
                }

            # Verificar si ya está en la llamada
            participantes = self.crud.get_participantes_activos(db, videollamada_id)
            usuarios_activos = {p.usuario_id for p in participantes}

            if usuario_id in usuarios_activos:
                return {"puede_unirse": False, "razon": "Ya estás en esta videollamada"}

            # Verificar límite de participantes si está configurado
            max_participantes = videollamada.configuracion.get("max_participantes")
            if max_participantes and len(participantes) >= max_participantes:
                return {
                    "puede_unirse": False,
                    "razon": f"Límite de participantes alcanzado ({max_participantes})",
                }

            return {
                "puede_unirse": True,
                "videollamada": VideollamadaResponse.model_validate(videollamada),
            }

        except Exception as e:
            return {"puede_unirse": False, "razon": f"Error al validar: {e!s}"}


# Instancia global del servicio
videollamada_service = VideollamadaService()
