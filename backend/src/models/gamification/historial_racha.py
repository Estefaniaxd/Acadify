"""
Modelo para historial de rachas.

Este modelo registra todos los cambios en las rachas de los usuarios,
incluyendo incrementos, pérdidas, recuperaciones y milestones alcanzados.

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
from sqlalchemy.dialects.postgresql import UUID, ENUM, DATE, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.db.base_class import Base
from src.enums.gamification import TipoEventoRacha


class HistorialRacha(Base):
    """
    Modelo para registrar cambios en las rachas de usuarios.
    
    Mantiene un log completo de todos los eventos relacionados con
    las rachas: incrementos, pérdidas, recuperaciones y milestones.
    
    Attributes:
        historial_id: UUID único del registro
        usuario_id: ID del usuario
        fecha: Fecha del evento
        racha_anterior: Valor de la racha antes del evento
        racha_nueva: Valor de la racha después del evento
        tipo_evento: Tipo de evento (TipoEventoRacha enum)
        puntos_otorgados: Puntos otorgados por este evento (si aplica)
        descripcion: Descripción detallada del evento
        timestamp: Timestamp exacto del evento
    
    Relationships:
        usuario: Usuario al que pertenece el registro
    
    Example:
        >>> # Racha incrementada
        >>> historial = HistorialRacha(
        ...     usuario_id=usuario_id,
        ...     fecha=date.today(),
        ...     racha_anterior=5,
        ...     racha_nueva=6,
        ...     tipo_evento=TipoEventoRacha.INCREMENTO,
        ...     puntos_otorgados=15
        ... )
        
        >>> # Racha perdida
        >>> historial = HistorialRacha(
        ...     usuario_id=usuario_id,
        ...     fecha=date.today(),
        ...     racha_anterior=10,
        ...     racha_nueva=0,
        ...     tipo_evento=TipoEventoRacha.PERDIDA,
        ...     descripcion="No hubo actividad el día anterior"
        ... )
        
        >>> # Milestone alcanzado
        >>> historial = HistorialRacha(
        ...     usuario_id=usuario_id,
        ...     fecha=date.today(),
        ...     racha_anterior=7,
        ...     racha_nueva=7,
        ...     tipo_evento=TipoEventoRacha.MILESTONE,
        ...     puntos_otorgados=50,
        ...     descripcion="Milestone: 7 días consecutivos"
        ... )
    """
    
    __tablename__ = "historial_racha"
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "racha_anterior >= 0",
            name="check_racha_anterior_positiva"
        ),
        CheckConstraint(
            "racha_nueva >= 0",
            name="check_racha_nueva_positiva"
        ),
        CheckConstraint(
            "puntos_otorgados >= 0",
            name="check_puntos_otorgados_positivo"
        ),
        # Índices
        Index("idx_historial_racha_usuario", "usuario_id"),
        Index("idx_historial_racha_fecha", "fecha"),
        Index("idx_historial_racha_tipo", "tipo_evento"),
        Index("idx_historial_racha_timestamp", "timestamp"),
    )
    
    # Primary Key
    historial_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        doc="UUID único del registro de historial"
    )
    
    # Foreign Key
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID del usuario"
    )
    
    # Información del evento
    fecha = Column(
        DATE,
        nullable=False,
        index=True,
        doc="Fecha del evento"
    )
    
    racha_anterior = Column(
        Integer,
        nullable=False,
        doc="Valor de la racha antes del evento"
    )
    
    racha_nueva = Column(
        Integer,
        nullable=False,
        doc="Valor de la racha después del evento"
    )
    
    tipo_evento = Column(
        ENUM(TipoEventoRacha, name="tipo_evento_racha_enum", create_type=False),
        nullable=False,
        index=True,
        doc="Tipo de evento que ocurrió"
    )
    
    puntos_otorgados = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Puntos otorgados por este evento"
    )
    
    descripcion = Column(
        String(500),
        nullable=True,
        doc="Descripción detallada del evento"
    )
    
    # Timestamp
    timestamp = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        doc="Timestamp exacto del evento"
    )
    
    # Relación
    usuario = relationship(
        "Usuario",
        backref="historial_rachas"
    )
    
    def __repr__(self):
        return (
            f"<HistorialRacha("
            f"id={self.historial_id}, "
            f"usuario_id={self.usuario_id}, "
            f"tipo={self.tipo_evento.value}, "
            f"{self.racha_anterior} → {self.racha_nueva}"
            f")>"
        )
    
    @property
    def cambio_racha(self) -> int:
        """
        Calcula el cambio en la racha.
        
        Returns:
            Diferencia entre racha nueva y anterior
        """
        return self.racha_nueva - self.racha_anterior
    
    @property
    def fue_incremento(self) -> bool:
        """Verifica si fue un incremento."""
        return self.tipo_evento == TipoEventoRacha.INCREMENTO
    
    @property
    def fue_perdida(self) -> bool:
        """Verifica si fue una pérdida."""
        return self.tipo_evento == TipoEventoRacha.PERDIDA
    
    @property
    def fue_milestone(self) -> bool:
        """Verifica si fue un milestone."""
        return self.tipo_evento == TipoEventoRacha.MILESTONE
    
    def to_dict(self) -> dict:
        """
        Convierte el registro a diccionario para API.
        
        Returns:
            Diccionario con información del evento
        """
        return {
            "historial_id": str(self.historial_id),
            "usuario_id": str(self.usuario_id),
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "racha_anterior": self.racha_anterior,
            "racha_nueva": self.racha_nueva,
            "cambio": self.cambio_racha,
            "tipo_evento": self.tipo_evento.value,
            "puntos_otorgados": self.puntos_otorgados,
            "descripcion": self.descripcion,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
