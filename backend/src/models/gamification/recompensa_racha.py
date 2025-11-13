"""
Modelo para configuración de recompensas por rachas.

Este modelo define las recompensas que se otorgan al alcanzar
ciertos días de racha consecutivos (milestones).

Author: GitHub Copilot & Team
Date: 31 de octubre de 2025
Version: 1.0.0
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    CheckConstraint,
    Index,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, ENUM, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.db.base_class import Base
from src.enums.gamification import TipoMilestone


class RecompensaRacha(Base):
    """
    Modelo para configuración de recompensas por milestones de racha.
    
    Define qué recompensas se otorgan al alcanzar ciertos días
    consecutivos de racha (ej: 7 días, 30 días, 100 días).
    
    Attributes:
        recompensa_racha_id: UUID único de la recompensa
        dias_requeridos: Cantidad de días consecutivos requeridos
        puntos_recompensa: Puntos que se otorgan
        insignia_id: ID de insignia que se otorga (opcional)
        tipo_milestone: Tipo de milestone (TipoMilestone enum)
        mensaje_motivacional: Mensaje al alcanzar el milestone
        es_repetible: Si se puede obtener múltiples veces
        descripcion: Descripción detallada
        es_activa: Si la recompensa está activa
        fecha_creacion: Timestamp de creación
    
    Relationships:
        insignia: Insignia asociada (si aplica)
    
    Example:
        >>> # Recompensa semanal
        >>> recompensa = RecompensaRacha(
        ...     dias_requeridos=7,
        ...     puntos_recompensa=50,
        ...     tipo_milestone=TipoMilestone.SEMANAL,
        ...     mensaje_motivacional="¡Una semana completa! 🎉",
        ...     es_repetible=True
        ... )
        
        >>> # Recompensa especial con insignia
        >>> recompensa = RecompensaRacha(
        ...     dias_requeridos=100,
        ...     puntos_recompensa=750,
        ...     insignia_id=insignia_id,
        ...     tipo_milestone=TipoMilestone.ESPECIAL,
        ...     mensaje_motivacional="¡100 días consecutivos! Eres una leyenda 🏆",
        ...     es_repetible=False
        ... )
    """
    
    __tablename__ = "recompensas_racha"
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "dias_requeridos > 0",
            name="check_dias_requeridos_positivo"
        ),
        CheckConstraint(
            "puntos_recompensa >= 0",
            name="check_puntos_recompensa_positivo"
        ),
        # Índices
        Index("idx_recompensa_racha_dias", "dias_requeridos"),
        Index("idx_recompensa_racha_tipo", "tipo_milestone"),
        Index("idx_recompensa_racha_activa", "es_activa"),
    )
    
    # Primary Key
    recompensa_racha_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        doc="UUID único de la recompensa"
    )
    
    # Configuración del milestone
    dias_requeridos = Column(
        Integer,
        nullable=False,
        unique=True,
        doc="Días consecutivos requeridos para obtener la recompensa"
    )
    
    puntos_recompensa = Column(
        Integer,
        nullable=False,
        doc="Puntos que se otorgan al alcanzar el milestone"
    )
    
    # Insignia asociada (opcional)
    insignia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Insignia.insignia_id", ondelete="SET NULL"),
        nullable=True,
        doc="ID de la insignia que se otorga (opcional)"
    )
    
    # Tipo de milestone
    tipo_milestone = Column(
        ENUM(TipoMilestone, name="tipo_milestone_enum", create_type=False),
        nullable=False,
        index=True,
        doc="Tipo de milestone (diario, semanal, mensual, especial)"
    )
    
    # Mensajes y descripción
    mensaje_motivacional = Column(
        String(500),
        nullable=True,
        doc="Mensaje motivacional al alcanzar el milestone"
    )
    
    descripcion = Column(
        String(500),
        nullable=True,
        doc="Descripción detallada del milestone"
    )
    
    # Configuración
    es_repetible = Column(
        String(1),
        nullable=False,
        default='N',
        server_default=text("'N'"),
        doc="Si se puede obtener múltiples veces (Y/N)"
    )
    
    es_activa = Column(
        String(1),
        nullable=False,
        default='Y',
        server_default=text("'Y'"),
        index=True,
        doc="Si la recompensa está activa (Y/N)"
    )
    
    # Metadata
    fecha_creacion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp de creación"
    )
    
    fecha_actualizacion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="Timestamp de última actualización"
    )
    
    # Relación
    insignia = relationship(
        "Insignia",
        foreign_keys=[insignia_id],
        backref="recompensas_racha"
    )
    
    def __repr__(self):
        return (
            f"<RecompensaRacha("
            f"id={self.recompensa_racha_id}, "
            f"dias={self.dias_requeridos}, "
            f"puntos={self.puntos_recompensa}, "
            f"tipo={self.tipo_milestone.value}"
            f")>"
        )
    
    @property
    def es_activa_bool(self) -> bool:
        """Convierte es_activa (Y/N) a booleano."""
        return self.es_activa == 'Y'
    
    @property
    def es_repetible_bool(self) -> bool:
        """Convierte es_repetible (Y/N) a booleano."""
        return self.es_repetible == 'Y'
    
    @property
    def tiene_insignia(self) -> bool:
        """Verifica si otorga insignia."""
        return self.insignia_id is not None
    
    def to_dict(self) -> dict:
        """
        Convierte la recompensa a diccionario para API.
        
        Returns:
            Diccionario con información de la recompensa
        """
        return {
            "recompensa_racha_id": str(self.recompensa_racha_id),
            "dias_requeridos": self.dias_requeridos,
            "puntos_recompensa": self.puntos_recompensa,
            "insignia_id": str(self.insignia_id) if self.insignia_id else None,
            "tipo_milestone": self.tipo_milestone.value,
            "mensaje_motivacional": self.mensaje_motivacional,
            "descripcion": self.descripcion,
            "es_repetible": self.es_repetible_bool,
            "es_activa": self.es_activa_bool,
            "tiene_insignia": self.tiene_insignia,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }
