"""
Modelo para etiquetas obtenidas por usuarios.

Este modelo registra qué etiquetas tiene cada usuario, cómo las obtuvo,
y su estado (equipadas, progreso de evolución).

Author: GitHub Copilot & Team
Date: 31 de octubre de 2025
Version: 1.0.0
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    JSON,
    ForeignKey,
    CheckConstraint,
    Index,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.db.base_class import Base


class UsuarioEtiqueta(Base):
    """
    Modelo para etiquetas en posesión de un usuario.
    
    Registra qué etiquetas tiene cada usuario, cuáles están equipadas
    en su perfil, y el progreso hacia su evolución.
    
    Attributes:
        usuario_etiqueta_id: UUID único del registro
        usuario_id: ID del usuario propietario
        etiqueta_id: ID de la etiqueta obtenida
        fecha_obtencion: Cuándo se obtuvo la etiqueta
        metodo_obtencion: Cómo se obtuvo (compra, logro, evento)
        esta_equipada: Si está equipada en el perfil
        orden_visualizacion: Orden en el perfil (1-5, solo 5 equipadas max)
        progreso_evolucion: Progreso hacia la siguiente evolución
        veces_equipada: Contador de veces que se ha equipado
    
    Relationships:
        usuario: Usuario propietario
        etiqueta: Etiqueta obtenida
    
    Example:
        >>> # Usuario obtiene etiqueta por compra
        >>> usuario_etiqueta = UsuarioEtiqueta(
        ...     usuario_id=usuario_id,
        ...     etiqueta_id=etiqueta_id,
        ...     metodo_obtencion="compra",
        ...     esta_equipada=True,
        ...     orden_visualizacion=1
        ... )
        
        >>> # Etiqueta con progreso de evolución
        >>> usuario_etiqueta = UsuarioEtiqueta(
        ...     usuario_id=usuario_id,
        ...     etiqueta_id=etiqueta_id,
        ...     metodo_obtencion="logro",
        ...     progreso_evolucion={
        ...         "tareas_completadas": 15,
        ...         "tareas_requeridas": 20
        ...     }
        ... )
    """
    
    __tablename__ = "usuario_etiquetas"
    
    # Constraints
    __table_args__ = (
        # Un usuario no puede tener la misma etiqueta dos veces
        UniqueConstraint(
            "usuario_id",
            "etiqueta_id",
            name="uq_usuario_etiqueta"
        ),
        CheckConstraint(
            "orden_visualizacion >= 0 AND orden_visualizacion <= 5",
            name="check_orden_visualizacion_valido"
        ),
        CheckConstraint(
            "veces_equipada >= 0",
            name="check_veces_equipada_positivo"
        ),
        # Índices
        Index("idx_usuario_etiqueta_usuario", "usuario_id"),
        Index("idx_usuario_etiqueta_etiqueta", "etiqueta_id"),
        Index("idx_usuario_etiqueta_equipada", "usuario_id", "esta_equipada"),
        Index("idx_usuario_etiqueta_metodo", "metodo_obtencion"),
    )
    
    # Primary Key
    usuario_etiqueta_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        doc="UUID único del registro"
    )
    
    # Foreign Keys
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID del usuario propietario"
    )
    
    etiqueta_id = Column(
        UUID(as_uuid=True),
        ForeignKey("etiquetas_perfil.etiqueta_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID de la etiqueta obtenida"
    )
    
    # Información de obtención
    fecha_obtencion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        doc="Fecha y hora en que se obtuvo la etiqueta"
    )
    
    metodo_obtencion = Column(
        String(50),
        nullable=False,
        default="compra",
        server_default=text("'compra'"),
        index=True,
        doc="Método de obtención: compra, logro, evento, regalo"
    )
    
    # Estado de la etiqueta
    esta_equipada = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
        doc="Si la etiqueta está equipada en el perfil"
    )
    
    orden_visualizacion = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Orden en el perfil (1-5, máximo 5 etiquetas equipadas)"
    )
    
    # Progreso hacia evolución
    progreso_evolucion = Column(
        JSON,
        nullable=True,
        doc="Progreso hacia la siguiente evolución de la etiqueta"
    )
    
    # Estadísticas
    veces_equipada = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Cantidad de veces que se ha equipado"
    )
    
    fecha_primera_equipada = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        doc="Primera vez que se equipó"
    )
    
    fecha_ultima_equipada = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        doc="Última vez que se equipó"
    )
    
    # Relaciones
    usuario = relationship(
        "Usuario",
        backref="etiquetas"
    )
    
    etiqueta = relationship(
        "EtiquetaPerfil",
        back_populates="usuarios_etiquetas"
    )
    
    def __repr__(self):
        return (
            f"<UsuarioEtiqueta("
            f"id={self.usuario_etiqueta_id}, "
            f"usuario_id={self.usuario_id}, "
            f"etiqueta_id={self.etiqueta_id}, "
            f"equipada={self.esta_equipada}"
            f")>"
        )
    
    def equipar(self, orden: int = 0):
        """
        Equipa la etiqueta en el perfil del usuario.
        
        Args:
            orden: Posición en el perfil (1-5)
        """
        from datetime import datetime, timezone
        
        self.esta_equipada = True
        self.orden_visualizacion = orden
        self.veces_equipada += 1
        self.fecha_ultima_equipada = datetime.now(timezone.utc)
        
        if not self.fecha_primera_equipada:
            self.fecha_primera_equipada = datetime.now(timezone.utc)
    
    def desequipar(self):
        """Desequipa la etiqueta del perfil."""
        self.esta_equipada = False
        self.orden_visualizacion = 0
    
    def actualizar_progreso(self, progreso: dict):
        """
        Actualiza el progreso hacia la evolución.
        
        Args:
            progreso: Diccionario con el progreso actual
        """
        self.progreso_evolucion = progreso
    
    @property
    def puede_evolucionar(self) -> bool:
        """
        Verifica si cumple los requisitos para evolucionar.
        
        Returns:
            True si puede evolucionar (debe verificarse con la lógica completa)
        """
        # Esta es una verificación básica
        # La lógica completa debe estar en el servicio
        return self.progreso_evolucion is not None
    
    def to_dict(self) -> dict:
        """
        Convierte el registro a diccionario para API.
        
        Returns:
            Diccionario con información de la etiqueta del usuario
        """
        return {
            "usuario_etiqueta_id": str(self.usuario_etiqueta_id),
            "usuario_id": str(self.usuario_id),
            "etiqueta_id": str(self.etiqueta_id),
            "fecha_obtencion": self.fecha_obtencion.isoformat() if self.fecha_obtencion else None,
            "metodo_obtencion": self.metodo_obtencion,
            "esta_equipada": self.esta_equipada,
            "orden_visualizacion": self.orden_visualizacion,
            "progreso_evolucion": self.progreso_evolucion,
            "veces_equipada": self.veces_equipada,
            "fecha_primera_equipada": self.fecha_primera_equipada.isoformat() if self.fecha_primera_equipada else None,
            "fecha_ultima_equipada": self.fecha_ultima_equipada.isoformat() if self.fecha_ultima_equipada else None,
        }
