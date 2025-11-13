"""Modelo de Misión para el sistema de gamificación."""
from datetime import datetime

from sqlalchemy import Column, Integer, String, text
from sqlalchemy.dialects.postgresql import BOOLEAN, ENUM, JSON, TEXT, TIMESTAMP, UUID
from sqlalchemy.orm import relationship

from src.db.base_class import Base
from src.enums.gamification.mision_enums import (
    DificultadMision,
    FrecuenciaMision,
    TipoMision,
)


class Mision(Base):
    """Modelo de misión del sistema de gamificación."""

    __tablename__ = "misiones"

    mision_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    nombre = Column(String(150), nullable=False)
    descripcion = Column(TEXT, nullable=False)
    icono = Column(String(50), nullable=True)  # Emoji o nombre de icono

    # Tipo y frecuencia
    tipo = Column(
        ENUM(TipoMision, name="tipo_mision", create_type=False),
        nullable=False,
    )
    frecuencia = Column(
        ENUM(FrecuenciaMision, name="frecuencia_mision", create_type=False),
        nullable=False,
        default=FrecuenciaMision.DIARIA,
    )
    dificultad = Column(
        ENUM(DificultadMision, name="dificultad_mision", create_type=False),
        nullable=False,
        default=DificultadMision.NORMAL,
    )

    # Objetivo y progreso
    objetivo = Column(Integer, nullable=False)  # Cantidad a completar
    unidad = Column(
        String(50), nullable=True
    )  # "tareas", "puntos", "días", etc.

    # Recompensas
    puntos_recompensa = Column(Integer, nullable=False, default=0)
    experiencia_recompensa = Column(Integer, nullable=False, default=0)
    recompensas_extra = Column(
        JSON, nullable=True
    )  # {"insignia_id": "...", "item_id": "..."}

    # Configuración
    es_activa = Column(BOOLEAN, nullable=False, default=True)
    requisitos = Column(JSON, nullable=True)  # Requisitos previos
    orden_visualizacion = Column(Integer, nullable=False, default=0)

    # Auditoría
    fecha_creacion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    fecha_actualizacion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow,
    )

    # Relaciones
    misiones_usuario = relationship("MisionUsuario", back_populates="mision")
