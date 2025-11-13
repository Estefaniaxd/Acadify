"""
Modelo para transacciones de la tienda.

Este modelo registra todas las transacciones (compras, ventas, regalos)
que ocurren en la tienda virtual.

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
    text,
)
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.db.base_class import Base


class TransaccionTienda(Base):
    """
    Modelo para registrar transacciones de la tienda.
    
    Mantiene un log completo de todas las transacciones realizadas
    en la tienda virtual para auditoría y análisis.
    
    Attributes:
        transaccion_id: UUID único de la transacción
        usuario_id: ID del usuario que realizó la transacción
        item_id: ID del item involucrado
        tipo_transaccion: Tipo (compra, venta, regalo)
        cantidad: Cantidad de items en la transacción
        puntos: Puntos involucrados (positivo = gasto, negativo = ganancia)
        puntos_antes: Puntos del usuario antes de la transacción
        puntos_despues: Puntos del usuario después de la transacción
        exitosa: Si la transacción fue exitosa
        razon_fallo: Razón si la transacción falló
        metadata_json: Información adicional
        fecha_transaccion: Timestamp de la transacción
        ip_usuario: IP del usuario (opcional, para seguridad)
    
    Relationships:
        usuario: Usuario que realizó la transacción
        item: Item involucrado en la transacción
    
    Example:
        >>> # Transacción de compra exitosa
        >>> trans = TransaccionTienda(
        ...     usuario_id=usuario_id,
        ...     item_id=item_id,
        ...     tipo_transaccion="compra",
        ...     cantidad=1,
        ...     puntos=150,
        ...     puntos_antes=500,
        ...     puntos_despues=350,
        ...     exitosa=True
        ... )
        
        >>> # Transacción fallida
        >>> trans = TransaccionTienda(
        ...     usuario_id=usuario_id,
        ...     item_id=item_id,
        ...     tipo_transaccion="compra",
        ...     cantidad=1,
        ...     puntos=1000,
        ...     puntos_antes=500,
        ...     puntos_despues=500,
        ...     exitosa=False,
        ...     razon_fallo="Puntos insuficientes"
        ... )
    """
    
    __tablename__ = "transacciones_tienda"
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "cantidad > 0",
            name="check_transaccion_cantidad_positiva"
        ),
        CheckConstraint(
            "puntos >= 0",
            name="check_transaccion_puntos_positivo"
        ),
        CheckConstraint(
            "puntos_antes >= 0",
            name="check_transaccion_puntos_antes_positivo"
        ),
        CheckConstraint(
            "puntos_despues >= 0",
            name="check_transaccion_puntos_despues_positivo"
        ),
        # Índices
        Index("idx_transaccion_usuario", "usuario_id"),
        Index("idx_transaccion_item", "item_id"),
        Index("idx_transaccion_tipo", "tipo_transaccion"),
        Index("idx_transaccion_exitosa", "exitosa"),
        Index("idx_transaccion_fecha", "fecha_transaccion"),
    )
    
    # Primary Key
    transaccion_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        doc="UUID único de la transacción"
    )
    
    # Foreign Keys
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID del usuario que realizó la transacción"
    )
    
    item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tienda_items.item_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="ID del item involucrado (puede ser null si se eliminó)"
    )
    
    # Información de la transacción
    tipo_transaccion = Column(
        String(20),
        nullable=False,
        index=True,
        doc="Tipo de transacción: compra, venta, regalo, reembolso"
    )
    
    cantidad = Column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
        doc="Cantidad de items en la transacción"
    )
    
    puntos = Column(
        Integer,
        nullable=False,
        doc="Puntos involucrados en la transacción"
    )
    
    puntos_antes = Column(
        Integer,
        nullable=False,
        doc="Puntos del usuario antes de la transacción"
    )
    
    puntos_despues = Column(
        Integer,
        nullable=False,
        doc="Puntos del usuario después de la transacción"
    )
    
    # Estado de la transacción
    exitosa = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        index=True,
        doc="Si la transacción fue exitosa"
    )
    
    razon_fallo = Column(
        String(500),
        nullable=True,
        doc="Razón del fallo si la transacción no fue exitosa"
    )
    
    # Metadata adicional
    metadata_json = Column(
        JSON,
        nullable=True,
        doc="Información adicional de la transacción"
    )
    
    # Tracking
    fecha_transaccion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        doc="Timestamp de la transacción"
    )
    
    ip_usuario = Column(
        String(45),
        nullable=True,
        doc="Dirección IP del usuario (para seguridad)"
    )
    
    # Relaciones
    usuario = relationship(
        "Usuario",
        backref="transacciones_tienda"
    )
    
    item = relationship(
        "TiendaItem",
        back_populates="transacciones"
    )
    
    def __repr__(self):
        return (
            f"<TransaccionTienda("
            f"id={self.transaccion_id}, "
            f"usuario_id={self.usuario_id}, "
            f"tipo={self.tipo_transaccion}, "
            f"puntos={self.puntos}, "
            f"exitosa={self.exitosa}"
            f")>"
        )
    
    @property
    def fue_compra(self) -> bool:
        """Verifica si fue una compra."""
        return self.tipo_transaccion == "compra"
    
    @property
    def fue_venta(self) -> bool:
        """Verifica si fue una venta."""
        return self.tipo_transaccion == "venta"
    
    @property
    def fue_regalo(self) -> bool:
        """Verifica si fue un regalo."""
        return self.tipo_transaccion == "regalo"
    
    def to_dict(self) -> dict:
        """
        Convierte la transacción a diccionario para API.
        
        Returns:
            Diccionario con información de la transacción
        """
        return {
            "transaccion_id": str(self.transaccion_id),
            "usuario_id": str(self.usuario_id),
            "item_id": str(self.item_id) if self.item_id else None,
            "tipo_transaccion": self.tipo_transaccion,
            "cantidad": self.cantidad,
            "puntos": self.puntos,
            "puntos_antes": self.puntos_antes,
            "puntos_despues": self.puntos_despues,
            "exitosa": self.exitosa,
            "razon_fallo": self.razon_fallo,
            "fecha_transaccion": self.fecha_transaccion.isoformat() if self.fecha_transaccion else None,
            "metadata": self.metadata_json,
        }
