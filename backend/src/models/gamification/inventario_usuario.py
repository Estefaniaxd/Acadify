"""
Modelo para inventario de items de usuarios.

Este modelo registra todos los items que un usuario ha adquirido,
ya sea por compra, regalo, logro o evento.

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
from sqlalchemy.dialects.postgresql import UUID, ENUM, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.db.base_class import Base
from src.enums.gamification import MetodoAdquisicion


class InventarioUsuario(Base):
    """
    Modelo para items en el inventario de un usuario.
    
    Registra todos los items que un usuario posee, cómo los obtuvo,
    y su estado actual (equipado, cantidad disponible).
    
    Attributes:
        inventario_id: UUID único del registro de inventario
        usuario_id: ID del usuario propietario
        item_id: ID del item en el inventario
        fecha_adquisicion: Cuándo se obtuvo el item
        metodo_adquisicion: Cómo se obtuvo (compra, regalo, logro)
        precio_pagado: Puntos gastados (si fue compra)
        cantidad: Cantidad del item (para consumibles)
        esta_equipado: Si el item está actualmente equipado/activo
        metadata_json: Información adicional
        fecha_ultimo_uso: Última vez que se usó (para consumibles)
    
    Relationships:
        usuario: Usuario propietario
        item: Item del inventario
    
    Example:
        >>> # Usuario compra camisa
        >>> inv = InventarioUsuario(
        ...     usuario_id=usuario_id,
        ...     item_id=camisa_id,
        ...     metodo_adquisicion=MetodoAdquisicion.COMPRA,
        ...     precio_pagado=75,
        ...     cantidad=1
        ... )
        
        >>> # Item consumible (recuperador de racha)
        >>> inv = InventarioUsuario(
        ...     usuario_id=usuario_id,
        ...     item_id=recuperador_id,
        ...     metodo_adquisicion=MetodoAdquisicion.COMPRA,
        ...     precio_pagado=200,
        ...     cantidad=3  # Compró 3 recuperadores
        ... )
    """
    
    __tablename__ = "inventario_usuario"
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "cantidad > 0",
            name="check_cantidad_positiva"
        ),
        CheckConstraint(
            "precio_pagado >= 0",
            name="check_precio_pagado_positivo"
        ),
        # Índices
        Index("idx_inventario_usuario", "usuario_id"),
        Index("idx_inventario_item", "item_id"),
        Index("idx_inventario_equipado", "usuario_id", "esta_equipado"),
        Index("idx_inventario_metodo", "metodo_adquisicion"),
    )
    
    # Primary Key
    inventario_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        doc="UUID único del registro de inventario"
    )
    
    # Foreign Keys
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID del usuario propietario"
    )
    
    item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tienda_items.item_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID del item en el inventario"
    )
    
    # Información de adquisición
    fecha_adquisicion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        doc="Fecha y hora de adquisición del item"
    )
    
    metodo_adquisicion = Column(
        ENUM(MetodoAdquisicion, name="metodo_adquisicion_enum", create_type=False),
        nullable=False,
        default=MetodoAdquisicion.COMPRA,
        server_default=text("'compra'"),
        index=True,
        doc="Método por el cual se obtuvo el item"
    )
    
    precio_pagado = Column(
        Integer,
        nullable=True,
        doc="Puntos gastados para obtener el item (si fue compra)"
    )
    
    # Estado del item
    cantidad = Column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
        doc="Cantidad del item (para items consumibles)"
    )
    
    esta_equipado = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
        doc="Si el item está actualmente equipado/activo"
    )
    
    # Metadata adicional
    metadata_json = Column(
        JSON,
        nullable=True,
        doc="Información adicional del item (personalizaciones, etc.)"
    )
    
    # Tracking de uso
    fecha_ultimo_uso = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        doc="Última vez que se usó el item (para consumibles)"
    )
    
    veces_usado = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Cantidad de veces que se ha usado (para estadísticas)"
    )
    
    # Relaciones
    usuario = relationship(
        "Usuario",
        backref="inventario"
    )
    
    item = relationship(
        "TiendaItem",
        back_populates="inventarios"
    )
    
    def __repr__(self):
        return (
            f"<InventarioUsuario("
            f"id={self.inventario_id}, "
            f"usuario_id={self.usuario_id}, "
            f"item_id={self.item_id}, "
            f"cantidad={self.cantidad}, "
            f"equipado={self.esta_equipado}"
            f")>"
        )
    
    def usar_item(self) -> bool:
        """
        Usa un item consumible (reduce cantidad en 1).
        
        Returns:
            True si se usó correctamente, False si no hay cantidad
        """
        if self.cantidad <= 0:
            return False
        
        from datetime import datetime, timezone
        self.cantidad -= 1
        self.fecha_ultimo_uso = datetime.now(timezone.utc)
        self.veces_usado += 1
        
        return True
    
    @property
    def esta_disponible(self) -> bool:
        """
        Verifica si el item está disponible para usar.
        
        Returns:
            True si tiene cantidad disponible
        """
        return self.cantidad > 0
    
    def to_dict(self) -> dict:
        """
        Convierte el registro a diccionario para API.
        
        Returns:
            Diccionario con información del inventario
        """
        return {
            "inventario_id": str(self.inventario_id),
            "usuario_id": str(self.usuario_id),
            "item_id": str(self.item_id),
            "fecha_adquisicion": self.fecha_adquisicion.isoformat() if self.fecha_adquisicion else None,
            "metodo_adquisicion": self.metodo_adquisicion.value,
            "precio_pagado": self.precio_pagado,
            "cantidad": self.cantidad,
            "esta_equipado": self.esta_equipado,
            "esta_disponible": self.esta_disponible,
            "fecha_ultimo_uso": self.fecha_ultimo_uso.isoformat() if self.fecha_ultimo_uso else None,
            "veces_usado": self.veces_usado,
            "metadata": self.metadata_json,
        }
