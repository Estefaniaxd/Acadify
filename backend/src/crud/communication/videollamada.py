"""CRUD operations para el sistema de videollamadas con Jitsi.

Este módulo implementa operaciones CRUD para gestionar videollamadas,
participantes y grabaciones siguiendo principios SOLID y Clean Code.

Utiliza Python Enums para type-safety y validación de valores.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from src.crud.base import CRUDBase
from src.enums.communication.videollamada_enums import (
    EstadoProcesamiento,
    EstadoVideollamada,
    TipoLlamada,
)
from src.models.communication.videollamada import (
    Videollamada,
    VideollamadaGrabacion,
    VideollamadaParticipante,
)


def now_utc() -> datetime:
    """Retorna datetime actual con timezone UTC."""
    return datetime.now(UTC)


# ==================== CRUD VIDEOLLAMADAS ====================


class CRUDVideollamada(CRUDBase[Videollamada, Any, Any]):
    """CRUD operations para videollamadas.

    Implementa operaciones de creación, lectura, actualización y eliminación
    para videollamadas siguiendo el patrón Repository.
    """

    def __init__(self) -> None:
        """Inicializar CRUD con modelo Videollamada."""
        super().__init__(Videollamada, id_field="id")

    def create_videollamada(
        self,
        db: Session,
        *,
        jitsi_room_name: str,
        tipo_llamada: TipoLlamada,
        iniciador_id: UUID,
        sala_chat_id: UUID | None = None,
        configuracion: dict[str, Any] | None = None,
    ) -> Videollamada:
        """Crear una nueva videollamada.

        Args:
            db: Sesión de base de datos
            jitsi_room_name: Nombre único de la sala Jitsi
            tipo_llamada: Tipo de llamada (TipoLlamada enum)
            iniciador_id: UUID del usuario que inicia la llamada
            sala_chat_id: UUID de la sala de chat asociada (opcional)
            configuracion: Configuración adicional en formato dict

        Returns:
            Videollamada: Nueva videollamada creada

        Raises:
            ValueError: Si tipo_llamada no es válido
        """
        # Validación automática con enum - no necesita check manual
        if not isinstance(tipo_llamada, TipoLlamada):
            msg = f"tipo_llamada debe ser TipoLlamada enum, recibido: {tipo_llamada}"
            raise ValueError(msg)

        db_obj = Videollamada(
            jitsi_room_name=jitsi_room_name,
            tipo_llamada=tipo_llamada,
            iniciador_id=iniciador_id,
            sala_chat_id=sala_chat_id,
            estado=EstadoVideollamada.ACTIVA,
            fecha_inicio=now_utc(),
            configuracion=configuracion or {},
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Agregar al iniciador como primer participante y moderador
        self._agregar_participante_interno(
            db=db, videollamada_id=db_obj.id, usuario_id=iniciador_id, es_moderador=True
        )

        return db_obj

    def get_with_participants(
        self, db: Session, videollamada_id: UUID
    ) -> Videollamada | None:
        """Obtener videollamada con sus participantes cargados.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada

        Returns:
            Optional[Videollamada]: Videollamada con participantes o None
        """
        return (
            db.query(self.model)
            .options(joinedload(self.model.participantes))
            .filter(self.model.id == videollamada_id)
            .filter(self.model.deleted_at.is_(None))
            .first()
        )

    def get_activas(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Videollamada]:
        """Obtener videollamadas activas.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar

        Returns:
            List[Videollamada]: Lista de videollamadas activas
        """
        return (
            db.query(self.model)
            .filter(self.model.estado == EstadoVideollamada.ACTIVA)
            .filter(self.model.deleted_at.is_(None))
            .order_by(desc(self.model.fecha_inicio))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_sala_chat(
        self, db: Session, sala_chat_id: UUID, *, incluir_finalizadas: bool = False
    ) -> list[Videollamada]:
        """Obtener videollamadas de una sala de chat específica.

        Args:
            db: Sesión de base de datos
            sala_chat_id: UUID de la sala de chat
            incluir_finalizadas: Si incluir llamadas finalizadas/canceladas

        Returns:
            List[Videollamada]: Lista de videollamadas
        """
        query = (
            db.query(self.model)
            .filter(self.model.sala_chat_id == sala_chat_id)
            .filter(self.model.deleted_at.is_(None))
        )

        if not incluir_finalizadas:
            query = query.filter(self.model.estado == EstadoVideollamada.ACTIVA)

        return query.order_by(desc(self.model.fecha_inicio)).all()

    def get_by_iniciador(
        self, db: Session, iniciador_id: UUID, *, skip: int = 0, limit: int = 100
    ) -> list[Videollamada]:
        """Obtener videollamadas iniciadas por un usuario.

        Args:
            db: Sesión de base de datos
            iniciador_id: UUID del usuario iniciador
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar

        Returns:
            List[Videollamada]: Lista de videollamadas
        """
        return (
            db.query(self.model)
            .filter(self.model.iniciador_id == iniciador_id)
            .filter(self.model.deleted_at.is_(None))
            .order_by(desc(self.model.fecha_inicio))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_room_name(
        self, db: Session, jitsi_room_name: str
    ) -> Videollamada | None:
        """Obtener videollamada por nombre de sala Jitsi.

        Args:
            db: Sesión de base de datos
            jitsi_room_name: Nombre de la sala Jitsi

        Returns:
            Optional[Videollamada]: Videollamada encontrada o None
        """
        return (
            db.query(self.model)
            .filter(self.model.jitsi_room_name == jitsi_room_name)
            .filter(self.model.deleted_at.is_(None))
            .first()
        )

    def agregar_participante(
        self,
        db: Session,
        *,
        videollamada_id: UUID,
        usuario_id: UUID,
        es_moderador: bool = False,
    ) -> VideollamadaParticipante:
        """Agregar un participante a una videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            usuario_id: UUID del usuario a agregar
            es_moderador: Si el usuario tendrá privilegios de moderador

        Returns:
            VideollamadaParticipante: Participante agregado

        Raises:
            ValueError: Si la videollamada no está activa o el participante ya existe
        """
        # Verificar que la videollamada existe y está activa
        videollamada = self.get(db, videollamada_id)
        if not videollamada:
            msg = f"Videollamada {videollamada_id} no encontrada"
            raise ValueError(msg)

        if videollamada.estado != EstadoVideollamada.ACTIVA:
            msg = f"Videollamada {videollamada_id} no está activa"
            raise ValueError(msg)

        # Verificar que el participante no existe ya
        participante_existente = (
            db.query(VideollamadaParticipante)
            .filter(
                VideollamadaParticipante.videollamada_id == videollamada_id,
                VideollamadaParticipante.usuario_id == usuario_id,
                VideollamadaParticipante.fecha_salida.is_(None),
            )
            .first()
        )

        if participante_existente:
            msg = f"Usuario {usuario_id} ya está en la videollamada"
            raise ValueError(msg)

        return self._agregar_participante_interno(
            db=db,
            videollamada_id=videollamada_id,
            usuario_id=usuario_id,
            es_moderador=es_moderador,
        )

    def _agregar_participante_interno(
        self,
        db: Session,
        *,
        videollamada_id: UUID,
        usuario_id: UUID,
        es_moderador: bool = False,
    ) -> VideollamadaParticipante:
        """Método interno para agregar participante (sin validaciones).

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            usuario_id: UUID del usuario
            es_moderador: Si es moderador

        Returns:
            VideollamadaParticipante: Participante creado
        """
        participante = VideollamadaParticipante(
            videollamada_id=videollamada_id,
            usuario_id=usuario_id,
            es_moderador=es_moderador,
            fecha_union=now_utc(),
        )

        db.add(participante)
        db.commit()
        db.refresh(participante)

        return participante

    def remover_participante(
        self, db: Session, *, videollamada_id: UUID, usuario_id: UUID
    ) -> VideollamadaParticipante | None:
        """Remover un participante de una videollamada (marcar fecha_salida).

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            usuario_id: UUID del usuario a remover

        Returns:
            Optional[VideollamadaParticipante]: Participante actualizado o None
        """
        participante = (
            db.query(VideollamadaParticipante)
            .filter(
                VideollamadaParticipante.videollamada_id == videollamada_id,
                VideollamadaParticipante.usuario_id == usuario_id,
                VideollamadaParticipante.fecha_salida.is_(None),
            )
            .first()
        )

        if participante:
            participante.fecha_salida = now_utc()

            # Calcular duración de participación
            if participante.fecha_union:
                # Normalizar timezone si fecha_union viene de DB sin timezone (SQLite)
                fecha_union = participante.fecha_union
                if fecha_union.tzinfo is None:
                    from datetime import UTC
                    fecha_union = fecha_union.replace(tzinfo=UTC)
                
                duracion = (participante.fecha_salida - fecha_union).total_seconds()
                participante.duracion_segundos = int(duracion)

            db.add(participante)
            db.commit()
            db.refresh(participante)

        return participante

    def get_participantes_activos(
        self, db: Session, videollamada_id: UUID
    ) -> list[VideollamadaParticipante]:
        """Obtener participantes activos en una videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada

        Returns:
            List[VideollamadaParticipante]: Lista de participantes activos
        """
        return (
            db.query(VideollamadaParticipante)
            .filter(
                VideollamadaParticipante.videollamada_id == videollamada_id,
                VideollamadaParticipante.fecha_salida.is_(None),
            )
            .order_by(VideollamadaParticipante.fecha_union)
            .all()
        )

    def finalizar_llamada(
        self, db: Session, videollamada_id: UUID, *, resumen_ia: str | None = None
    ) -> Videollamada | None:
        """Finalizar una videollamada activa.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            resumen_ia: Resumen generado por IA (opcional)

        Returns:
            Optional[Videollamada]: Videollamada finalizada o None

        Raises:
            ValueError: Si la videollamada no está activa
        """
        videollamada = self.get(db, videollamada_id)
        if not videollamada:
            return None

        if videollamada.estado != EstadoVideollamada.ACTIVA:
            msg = f"Videollamada {videollamada_id} no está activa"
            raise ValueError(msg)

        # Actualizar estado y fecha fin
        videollamada.estado = EstadoVideollamada.FINALIZADA
        videollamada.fecha_fin = now_utc()

        # Calcular duración total
        if videollamada.fecha_inicio:
            # Normalizar timezone si fecha_inicio viene de DB sin timezone (SQLite)
            fecha_inicio = videollamada.fecha_inicio
            if fecha_inicio.tzinfo is None:
                from datetime import UTC
                fecha_inicio = fecha_inicio.replace(tzinfo=UTC)
            
            duracion = (videollamada.fecha_fin - fecha_inicio).total_seconds()
            videollamada.duracion_segundos = int(duracion)

        # Agregar resumen si se proporciona
        if resumen_ia:
            videollamada.resumen_ia = resumen_ia

        db.add(videollamada)

        # Marcar salida de todos los participantes activos
        participantes_activos = self.get_participantes_activos(db, videollamada_id)
        for participante in participantes_activos:
            self.remover_participante(
                db=db,
                videollamada_id=videollamada_id,
                usuario_id=participante.usuario_id,
            )

        db.commit()
        db.refresh(videollamada)

        return videollamada

    def cancelar_llamada(
        self, db: Session, videollamada_id: UUID
    ) -> Videollamada | None:
        """Cancelar una videollamada activa.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada

        Returns:
            Optional[Videollamada]: Videollamada cancelada o None
        """
        videollamada = self.get(db, videollamada_id)
        if not videollamada or videollamada.estado != EstadoVideollamada.ACTIVA:
            return None

        videollamada.estado = EstadoVideollamada.CANCELADA
        videollamada.fecha_fin = now_utc()

        if videollamada.fecha_inicio:
            # Normalizar timezone si fecha_inicio viene de DB sin timezone (SQLite)
            fecha_inicio = videollamada.fecha_inicio
            if fecha_inicio.tzinfo is None:
                from datetime import UTC
                fecha_inicio = fecha_inicio.replace(tzinfo=UTC)
            
            duracion = (videollamada.fecha_fin - fecha_inicio).total_seconds()
            videollamada.duracion_segundos = int(duracion)

        db.add(videollamada)
        db.commit()
        db.refresh(videollamada)

        return videollamada

    def actualizar_transcripcion(
        self, db: Session, videollamada_id: UUID, transcripcion: str
    ) -> Videollamada | None:
        """Actualizar la transcripción de una videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            transcripcion: Texto de transcripción

        Returns:
            Optional[Videollamada]: Videollamada actualizada o None
        """
        videollamada = self.get(db, videollamada_id)
        if not videollamada:
            return None

        videollamada.transcripcion = transcripcion

        db.add(videollamada)
        db.commit()
        db.refresh(videollamada)

        return videollamada

    def get_grabaciones(
        self, db: Session, videollamada_id: UUID
    ) -> list[VideollamadaGrabacion]:
        """Obtener todas las grabaciones de una videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada

        Returns:
            List[VideollamadaGrabacion]: Lista de grabaciones
        """
        return (
            db.query(VideollamadaGrabacion)
            .filter(
                VideollamadaGrabacion.videollamada_id == videollamada_id,
                VideollamadaGrabacion.deleted_at.is_(None),
            )
            .order_by(VideollamadaGrabacion.created_at)
            .all()
        )

    def agregar_grabacion(
        self,
        db: Session,
        *,
        videollamada_id: UUID,
        archivo_url: str,
        formato: str | None = None,
        duracion_segundos: int | None = None,
        tamano_bytes: int | None = None,
        calidad: str | None = None,
        thumbnail_url: str | None = None,
        metadatos: dict[str, Any] | None = None,
    ) -> VideollamadaGrabacion:
        """Agregar una grabación a una videollamada.

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada
            archivo_url: URL del archivo de grabación
            formato: Formato del archivo (mp4, webm, etc.)
            duracion_segundos: Duración en segundos
            tamano_bytes: Tamaño del archivo en bytes
            calidad: Calidad de grabación (SD, HD, FHD, 4K)
            thumbnail_url: URL de la miniatura
            metadatos: Metadatos adicionales

        Returns:
            VideollamadaGrabacion: Grabación creada
        """
        grabacion = VideollamadaGrabacion(
            videollamada_id=videollamada_id,
            archivo_url=archivo_url,
            formato=formato,
            duracion_segundos=duracion_segundos,
            tamano_bytes=tamano_bytes,
            calidad=calidad,
            thumbnail_url=thumbnail_url,
            estado_procesamiento=EstadoProcesamiento.COMPLETADO,
            metadatos=metadatos or {},
        )

        db.add(grabacion)
        db.commit()
        db.refresh(grabacion)

        # Actualizar URL de grabación principal en videollamada
        videollamada = self.get(db, videollamada_id)
        if videollamada and not videollamada.grabacion_url:
            videollamada.grabacion_url = archivo_url
            db.add(videollamada)
            db.commit()

        return grabacion

    def soft_delete(self, db: Session, videollamada_id: UUID) -> Videollamada | None:
        """Soft delete de una videollamada (marcar deleted_at).

        Args:
            db: Sesión de base de datos
            videollamada_id: UUID de la videollamada

        Returns:
            Optional[Videollamada]: Videollamada eliminada o None
        """
        videollamada = self.get(db, videollamada_id)
        if not videollamada:
            return None

        videollamada.deleted_at = now_utc()

        db.add(videollamada)
        db.commit()
        db.refresh(videollamada)

        return videollamada


# Instancia global del CRUD
crud_videollamada = CRUDVideollamada()
