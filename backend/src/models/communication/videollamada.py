"""Modelos para videollamadas con Jitsi Meet.

Este módulo define las tablas de base de datos para gestionar:
- Videollamadas usando Jitsi Meet como proveedor
- Participantes y su estado de conexión
- Grabaciones con procesamiento y almacenamiento

Siguiendo principios SOLID y Clean Code para mantener
un sistema escalable y mantenible.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base_class import Base
from src.enums.communication.videollamada_enums import (
    CalidadConexion,
    CalidadGrabacion,
    EstadoProcesamiento,
    EstadoVideollamada,
    FormatoGrabacion,
    TipoLlamada,
)

if TYPE_CHECKING:
    from src.models.auth import Usuario
    from src.models.communication import SalaChat


def now_utc() -> datetime:
    """Helper para obtener timestamp UTC actual."""
    return datetime.now(UTC)


# ==================== MODELOS ====================


class Videollamada(Base):
    """Representa una videollamada usando Jitsi Meet.

    Attributes:
        id: Identificador único UUID
        jitsi_room_name: Nombre único de la sala en Jitsi Meet
        tipo_llamada: Tipo de llamada (video o voz)
        iniciador_id: UUID del usuario que inició la llamada
        sala_chat_id: UUID de la sala de chat asociada (opcional)
        fecha_inicio: Timestamp cuando inició la llamada
        fecha_fin: Timestamp cuando finalizó la llamada
        duracion_segundos: Duración total en segundos
        estado: Estado actual (EstadoVideollamada enum)
        configuracion: JSON con configuración adicional de Jitsi
        grabacion_url: URL de la grabación principal (opcional)
        transcripcion: Texto de transcripción automática (opcional)
        resumen_ia: Resumen generado por IA (opcional)
    """

    __tablename__ = "videollamadas"

    # Campos principales
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    jitsi_room_name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    tipo_llamada: Mapped[str] = mapped_column(
        SQLEnum(TipoLlamada, name="tipo_llamada", native_enum=False),
        nullable=False,
        default=TipoLlamada.VIDEO,
    )
    iniciador_id: Mapped[UUID] = mapped_column(
        ForeignKey("Usuario.usuario_id"), nullable=False, index=True
    )
    sala_chat_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("salas_chat.id"), nullable=True, index=True
    )

    # Timestamps
    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, nullable=False
    )
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duracion_segundos: Mapped[int | None] = mapped_column(Integer)

    # Estado y configuración
    estado: Mapped[str] = mapped_column(
        SQLEnum(EstadoVideollamada, name="estado_videollamada", native_enum=False),
        default=EstadoVideollamada.ACTIVA,
        nullable=False,
        index=True,
    )
    configuracion: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Campos de procesamiento posterior
    grabacion_url: Mapped[str | None] = mapped_column(String(500))
    transcripcion: Mapped[str | None] = mapped_column(Text)
    resumen_ia: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    iniciador: Mapped["Usuario"] = relationship(foreign_keys=[iniciador_id])
    sala_chat: Mapped["SalaChat | None"] = relationship(back_populates="videollamadas")
    participantes: Mapped[list["VideollamadaParticipante"]] = relationship(
        back_populates="videollamada", cascade="all, delete-orphan"
    )
    grabaciones: Mapped[list["VideollamadaGrabacion"]] = relationship(
        back_populates="videollamada", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Representación en string de la videollamada."""
        return f"<Videollamada(id={self.id}, jitsi_room={self.jitsi_room_name}, estado={self.estado})>"


class VideollamadaParticipante(Base):
    """Representa un participante en una videollamada Jitsi.

    Attributes:
        id: Identificador único UUID
        videollamada_id: UUID de la videollamada
        usuario_id: UUID del usuario participante
        fecha_union: Timestamp de unión
        fecha_salida: Timestamp de salida (None si aún conectado)
        duracion_segundos: Duración de participación en segundos
        es_moderador: Si tiene permisos de moderador en Jitsi
        calidad_conexion: Calidad de conexión del participante
        estadisticas: JSON con métricas de red y calidad
    """

    __tablename__ = "videollamadas_participantes"

    # Campos principales
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    videollamada_id: Mapped[UUID] = mapped_column(
        ForeignKey("videollamadas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    usuario_id: Mapped[UUID] = mapped_column(
        ForeignKey("Usuario.usuario_id"), nullable=False, index=True
    )

    # Timestamps
    fecha_union: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, nullable=False
    )
    fecha_salida: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duracion_segundos: Mapped[int | None] = mapped_column(Integer)

    # Estado de participación
    es_moderador: Mapped[bool] = mapped_column(default=False)
    calidad_conexion: Mapped[str | None] = mapped_column(
        SQLEnum(CalidadConexion, name="calidad_conexion", native_enum=False)
    )
    estadisticas: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Relaciones
    videollamada: Mapped["Videollamada"] = relationship(back_populates="participantes")
    usuario: Mapped["Usuario"] = relationship()

    def __repr__(self) -> str:
        """Representación en string del participante."""
        return f"<VideollamadaParticipante(id={self.id}, usuario_id={self.usuario_id})>"


class VideollamadaGrabacion(Base):
    """Representa una grabación de videollamada almacenada.

    Attributes:
        id: Identificador único UUID
        videollamada_id: UUID de la videollamada grabada
        titulo: Título descriptivo de la grabación
        archivo_url: URL del archivo de video
        thumbnail_url: URL de la miniatura/preview
        formato: Formato del archivo (FormatoGrabacion enum)
        calidad: Calidad de video (CalidadGrabacion enum)
        duracion_segundos: Duración en segundos
        tamano_bytes: Tamaño del archivo en bytes
        fecha_subida: Timestamp de subida
        estado_procesamiento: Estado del procesamiento (EstadoProcesamiento enum)
        error_mensaje: Mensaje de error si falló el procesamiento
        metadatos: JSON con información adicional
    """

    __tablename__ = "videollamadas_grabaciones"

    # Campos principales
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    videollamada_id: Mapped[UUID] = mapped_column(
        ForeignKey("videollamadas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    archivo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))

    # Información del archivo
    formato: Mapped[str] = mapped_column(
        SQLEnum(FormatoGrabacion, name="formato_grabacion", native_enum=False),
        nullable=False,
    )
    calidad: Mapped[str] = mapped_column(
        SQLEnum(CalidadGrabacion, name="calidad_grabacion", native_enum=False),
        nullable=False,
    )
    duracion_segundos: Mapped[int] = mapped_column(Integer, nullable=False)
    tamano_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Timestamps y procesamiento
    fecha_subida: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, nullable=False
    )
    estado_procesamiento: Mapped[str] = mapped_column(
        SQLEnum(EstadoProcesamiento, name="estado_procesamiento", native_enum=False),
        default=EstadoProcesamiento.PENDIENTE,
        nullable=False,
        index=True,
    )
    error_mensaje: Mapped[str | None] = mapped_column(Text)
    metadatos: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Relaciones
    videollamada: Mapped["Videollamada"] = relationship(back_populates="grabaciones")

    def __repr__(self) -> str:
        """Representación en string de la grabación."""
        return f"<VideollamadaGrabacion(id={self.id}, titulo={self.titulo})>"
