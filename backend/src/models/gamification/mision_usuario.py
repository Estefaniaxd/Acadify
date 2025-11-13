"""Modelo de relación entre Usuario y Misión."""
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import ENUM, JSON, TIMESTAMP, UUID
from sqlalchemy.orm import relationship

from src.db.base_class import Base
from src.enums.gamification.mision_enums import EstadoMision


class MisionUsuario(Base):
    """Modelo de asignación y progreso de misiones por usuario."""

    __tablename__ = "misiones_usuario"

    mision_usuario_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    # Referencias
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mision_id = Column(
        UUID(as_uuid=True),
        ForeignKey("misiones.mision_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Estado y progreso
    estado = Column(
        ENUM(EstadoMision, name="estado_mision", create_type=False),
        nullable=False,
        default=EstadoMision.DISPONIBLE,
        index=True,
    )
    progreso_actual = Column(Integer, nullable=False, default=0)

    # Fechas importantes
    fecha_asignacion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
    )
    fecha_inicio = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_completada = Column(TIMESTAMP(timezone=True), nullable=True, index=True)
    fecha_reclamada = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_expiracion = Column(TIMESTAMP(timezone=True), nullable=True, index=True)

    # Metadatos
    metadata_progreso = Column(
        JSON, nullable=True
    )  # Información adicional del progreso
    fecha_actualizacion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow,
    )

    # Relaciones
    usuario = relationship("Usuario", back_populates="misiones_usuario")
    mision = relationship("Mision", back_populates="misiones_usuario")
