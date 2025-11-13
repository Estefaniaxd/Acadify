from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base


class Reaccion(Base):
    """Modelo para reacciones a COMENTARIOS.

    Representa las reacciones de usuarios a comentarios en el sistema.
    Separado de ReaccionMensaje para mantener contextos diferentes.

    Attributes:
        reaccion_id: Identificador único de la reacción
        comentario_id: Referencia al comentario reaccionado
        usuario_id: Usuario que realiza la reacción
        emoji: Emoji de la reacción
        tipo: Tipo de reacción (like, love, etc.)
        fecha_creacion: Fecha de creación de la reacción
        activo: Estado de la reacción
    """

    __tablename__ = "Reacciones"

    # Identificación
    reaccion_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    comentario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Comentario.comentario_id"),
        nullable=False,
        index=True,
    )
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False, index=True
    )

    # Contenido de la reacción
    emoji = Column(String, nullable=False)
    tipo = Column(String)

    # Metadatos
    fecha_creacion = Column(DateTime, server_default=func.now())
    activo = Column(Boolean, default=True)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    comentario = relationship("Comentario", back_populates="reacciones")

    @property
    def esta_activa(self) -> bool:
        """Verifica si la reacción está activa."""
        return self.activo

    def to_dict(self) -> dict:
        """Serializa el modelo a diccionario."""
        return {
            "reaccion_id": str(self.reaccion_id),
            "comentario_id": str(self.comentario_id),
            "usuario_id": str(self.usuario_id),
            "emoji": self.emoji,
            "tipo": self.tipo,
            "fecha_creacion": (
                self.fecha_creacion.isoformat() if self.fecha_creacion else None
            ),
            "activo": self.activo,
            "esta_activa": self.esta_activa,
        }


class ReaccionMensaje(Base):
    """Modelo para reacciones a MENSAJES de chat.

    Representa las reacciones de usuarios a mensajes en salas de chat.
    Separado de Reaccion (comentarios) para mantener contextos diferentes.

    Attributes:
        id: Identificador único de la reacción
        mensaje_id: Referencia al mensaje reaccionado
        usuario_id: Usuario que realiza la reacción
        emoji: Emoji de la reacción
        fecha_reaccion: Fecha de la reacción
    """

    __tablename__ = "reacciones_mensajes"

    # Identificación
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    mensaje_id = Column(
        UUID(as_uuid=True), ForeignKey("mensajes.id"), nullable=False, index=True
    )
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False, index=True
    )

    # Contenido de la reacción
    emoji = Column(String, nullable=False)

    # Metadatos
    fecha_reaccion = Column(DateTime, server_default=func.now())

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    # mensaje = relationship("Mensaje", foreign_keys=[mensaje_id])  # Relación con Mensaje

    @property
    def es_reciente(self) -> bool:
        """Verifica si la reacción es reciente (últimas 24 horas)."""
        if not self.fecha_reaccion:
            return False
        from datetime import timedelta

        return (datetime.utcnow() - self.fecha_reaccion) <= timedelta(hours=24)

    def to_dict(self) -> dict:
        """Serializa el modelo a diccionario."""
        return {
            "id": str(self.id),
            "mensaje_id": str(self.mensaje_id),
            "usuario_id": str(self.usuario_id),
            "emoji": self.emoji,
            "fecha_reaccion": (
                self.fecha_reaccion.isoformat() if self.fecha_reaccion else None
            ),
            "es_reciente": self.es_reciente,
        }
