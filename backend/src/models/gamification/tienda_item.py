"""
Modelo para items de la tienda virtual.

Este modelo representa los items disponibles para compra en la tienda,
incluyendo ropa de avatar, accesorios, fondos, marcos y items funcionales.

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
from sqlalchemy.dialects.postgresql import UUID, ENUM, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.db.base_class import Base
from src.enums.gamification import CategoriaItem, RarezaItem


class TiendaItem(Base):
    """
    Modelo para items disponibles en la tienda virtual.
    
    Cada item puede ser:
    - Visual: Ropa, accesorios, fondos (asociado a AvatarAsset)
    - Funcional: Items con efectos especiales (recuperar racha, etc.)
    - Etiqueta: Badges para el perfil
    
    Los items tienen requisitos (nivel, puntos) y pueden ser limitados
    o de temporada.
    
    Attributes:
        item_id: UUID único del item
        nombre: Nombre del item
        descripcion: Descripción detallada
        categoria: Categoría del item (CategoriaItem enum)
        subcategoria: Subcategoría opcional para organización
        precio_puntos: Costo en puntos
        rareza: Nivel de rareza (RarezaItem enum)
        nivel_minimo_requerido: Nivel mínimo para comprar (ej: "Plata I")
        puntos_minimos_requeridos: Puntos mínimos acumulados requeridos
        asset_id: Referencia a AvatarAsset si es item visual
        preview_url: URL de preview del item
        es_limitado: Si tiene stock limitado
        stock_disponible: Cantidad disponible (null = ilimitado)
        es_funcional: Si es un item con efecto funcional
        efecto_json: Metadata del efecto funcional
        disponible_desde: Fecha desde que está disponible
        disponible_hasta: Fecha hasta que está disponible (temporada)
        es_activo: Si el item está activo en la tienda
        orden_visualizacion: Orden de visualización en tienda
        fecha_creacion: Timestamp de creación
        fecha_actualizacion: Timestamp de última actualización
    
    Relationships:
        asset: Relación con AvatarAsset (si aplica)
        inventarios: Items en inventarios de usuarios
        transacciones: Historial de transacciones
    
    Example:
        >>> # Item de ropa común
        >>> item = TiendaItem(
        ...     nombre="Camisa Blanca Básica",
        ...     categoria=CategoriaItem.ROPA_SUPERIOR,
        ...     precio_puntos=75,
        ...     rareza=RarezaItem.COMUN,
        ...     es_funcional=False
        ... )
        
        >>> # Item funcional
        >>> recuperador = TiendaItem(
        ...     nombre="Recuperador de Racha",
        ...     categoria=CategoriaItem.FUNCIONAL,
        ...     precio_puntos=200,
        ...     rareza=RarezaItem.RARO,
        ...     es_funcional=True,
        ...     efecto_json={"tipo": "recuperar_racha", "dias": 1}
        ... )
    """
    
    __tablename__ = "tienda_items"
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "precio_puntos >= 0",
            name="check_precio_positivo"
        ),
        CheckConstraint(
            "stock_disponible IS NULL OR stock_disponible >= 0",
            name="check_stock_positivo"
        ),
        CheckConstraint(
            "puntos_minimos_requeridos >= 0",
            name="check_puntos_minimos_positivo"
        ),
        Index("idx_tienda_categoria", "categoria"),
        Index("idx_tienda_rareza", "rareza"),
        Index("idx_tienda_activo", "es_activo"),
        Index("idx_tienda_funcional", "es_funcional"),
    )
    
    # Primary Key
    item_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        doc="UUID único del item"
    )
    
    # Información básica
    nombre = Column(
        String(100),
        nullable=False,
        doc="Nombre del item"
    )
    
    descripcion = Column(
        String(500),
        nullable=True,
        doc="Descripción detallada del item"
    )
    
    # Categorización
    categoria = Column(
        ENUM(CategoriaItem, name="categoria_item_enum", create_type=False),
        nullable=False,
        index=True,
        doc="Categoría principal del item"
    )
    
    subcategoria = Column(
        String(50),
        nullable=True,
        doc="Subcategoría opcional (ej: casual, formal, deportivo)"
    )
    
    # Precio y rareza
    precio_puntos = Column(
        Integer,
        nullable=False,
        doc="Costo del item en puntos"
    )
    
    rareza = Column(
        ENUM(RarezaItem, name="rareza_item_enum", create_type=False),
        nullable=False,
        index=True,
        doc="Nivel de rareza del item"
    )
    
    # Requisitos
    nivel_minimo_requerido = Column(
        String(20),
        nullable=True,
        doc="Nivel mínimo requerido para comprar (ej: 'Plata I')"
    )
    
    puntos_minimos_requeridos = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Puntos acumulados mínimos para comprar"
    )
    
    # Asset asociado (para items visuales)
    asset_id = Column(
        UUID(as_uuid=True),
        ForeignKey("avatar_asset.id", ondelete="SET NULL"),
        nullable=True,
        doc="Referencia a AvatarAsset si es item visual"
    )
    
    preview_url = Column(
        String(500),
        nullable=True,
        doc="URL de imagen de preview del item"
    )
    
    # Stock y disponibilidad
    es_limitado = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        doc="Si el item tiene stock limitado"
    )
    
    stock_disponible = Column(
        Integer,
        nullable=True,
        doc="Cantidad disponible (null = ilimitado)"
    )
    
    # Items funcionales
    es_funcional = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
        doc="Si es un item con efecto funcional"
    )
    
    efecto_json = Column(
        JSON,
        nullable=True,
        doc="Metadata del efecto funcional (tipo, parámetros, etc.)"
    )
    
    # Temporalidad
    disponible_desde = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        doc="Fecha desde que el item está disponible"
    )
    
    disponible_hasta = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        doc="Fecha hasta que el item está disponible (para items de temporada)"
    )
    
    # Estado
    es_activo = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        index=True,
        doc="Si el item está activo en la tienda"
    )
    
    orden_visualizacion = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Orden de visualización en la tienda"
    )
    
    # Metadata
    fecha_creacion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp de creación del item"
    )
    
    fecha_actualizacion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="Timestamp de última actualización"
    )
    
    # Relaciones
    asset = relationship(
        "AvatarAsset",
        foreign_keys=[asset_id],
        backref="tienda_items"
    )
    
    inventarios = relationship(
        "InventarioUsuario",
        back_populates="item",
        cascade="all, delete-orphan"
    )
    
    transacciones = relationship(
        "TransaccionTienda",
        back_populates="item",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return (
            f"<TiendaItem("
            f"id={self.item_id}, "
            f"nombre='{self.nombre}', "
            f"categoria={self.categoria.value}, "
            f"precio={self.precio_puntos}, "
            f"rareza={self.rareza.value}"
            f")>"
        )
    
    @property
    def esta_disponible(self) -> bool:
        """
        Verifica si el item está actualmente disponible.
        
        Returns:
            True si está activo y dentro del período de disponibilidad
        """
        if not self.es_activo:
            return False
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        if self.disponible_desde and now < self.disponible_desde:
            return False
        
        if self.disponible_hasta and now > self.disponible_hasta:
            return False
        
        return True
    
    @property
    def tiene_stock(self) -> bool:
        """
        Verifica si hay stock disponible.
        
        Returns:
            True si hay stock o es ilimitado
        """
        if not self.es_limitado:
            return True
        
        return self.stock_disponible is not None and self.stock_disponible > 0
    
    def to_dict(self) -> dict:
        """
        Convierte el item a diccionario para API.
        
        Returns:
            Diccionario con información del item
        """
        return {
            "item_id": str(self.item_id),
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "categoria": self.categoria.value,
            "subcategoria": self.subcategoria,
            "precio_puntos": self.precio_puntos,
            "rareza": self.rareza.value,
            "nivel_minimo_requerido": self.nivel_minimo_requerido,
            "puntos_minimos_requeridos": self.puntos_minimos_requeridos,
            "preview_url": self.preview_url,
            "es_limitado": self.es_limitado,
            "stock_disponible": self.stock_disponible,
            "es_funcional": self.es_funcional,
            "efecto": self.efecto_json if self.es_funcional else None,
            "esta_disponible": self.esta_disponible,
            "tiene_stock": self.tiene_stock,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }
