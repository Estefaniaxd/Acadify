"""
Modelo para etiquetas de perfil.

Este modelo define las etiquetas (badges) temáticos que los usuarios
pueden mostrar en sus perfiles, con sistema de rareza y evolución.

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
from src.enums.gamification import CategoriaEtiqueta, RarezaEtiqueta


class EtiquetaPerfil(Base):
    """
    Modelo para etiquetas de perfil (badges temáticos).
    
    Las etiquetas son badges que los usuarios pueden mostrar en sus perfiles.
    Tienen categorías temáticas, niveles de rareza y pueden evolucionar.
    
    Attributes:
        etiqueta_id: UUID único de la etiqueta
        nombre: Nombre de la etiqueta
        descripcion: Descripción detallada
        categoria: Categoría temática (CategoriaEtiqueta enum)
        rareza: Nivel de rareza (RarezaEtiqueta enum)
        icono_url: URL del icono de la etiqueta
        color_hex: Color representativo (#RRGGBB)
        animacion_url: URL de animación (para legendarias)
        precio_puntos: Costo en puntos (null = no se puede comprar)
        es_comprable: Si se puede comprar en tienda
        requisito_logro: Requisito para desbloquear (si no es comprable)
        etiqueta_evolucion_id: ID de la etiqueta a la que evoluciona
        requisito_evolucion: Requisitos para evolucionar
        es_activa: Si la etiqueta está activa
        orden: Orden de visualización
        fecha_creacion: Timestamp de creación
        fecha_actualizacion: Timestamp de última actualización
    
    Relationships:
        etiqueta_evolucion: Etiqueta siguiente en la cadena de evolución
        usuarios_etiquetas: Usuarios que tienen esta etiqueta
    
    Example:
        >>> # Etiqueta común comprable
        >>> etiqueta = EtiquetaPerfil(
        ...     nombre="Lector Principiante",
        ...     categoria=CategoriaEtiqueta.LECTURA,
        ...     rareza=RarezaEtiqueta.COMUN,
        ...     precio_puntos=100,
        ...     es_comprable=True
        ... )
        
        >>> # Etiqueta épica por logro
        >>> etiqueta = EtiquetaPerfil(
        ...     nombre="Perfeccionista",
        ...     categoria=CategoriaEtiqueta.LOGRO_TAREAS,
        ...     rareza=RarezaEtiqueta.EPICO,
        ...     es_comprable=False,
        ...     requisito_logro={
        ...         "tipo": "tareas_perfectas",
        ...         "cantidad": 10
        ...     }
        ... )
        
        >>> # Etiqueta con evolución
        >>> etiqueta_base = EtiquetaPerfil(
        ...     nombre="Matemático Novato",
        ...     rareza=RarezaEtiqueta.COMUN,
        ...     etiqueta_evolucion_id=etiqueta_avanzada_id,
        ...     requisito_evolucion={
        ...         "tipo": "tareas_completadas",
        ...         "materia": "matematicas",
        ...         "cantidad": 20
        ...     }
        ... )
    """
    
    __tablename__ = "etiquetas_perfil"
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "precio_puntos IS NULL OR precio_puntos >= 0",
            name="check_etiqueta_precio_positivo"
        ),
        CheckConstraint(
            "NOT (es_comprable = true AND precio_puntos IS NULL)",
            name="check_etiqueta_comprable_tiene_precio"
        ),
        # Índices
        Index("idx_etiqueta_categoria", "categoria"),
        Index("idx_etiqueta_rareza", "rareza"),
        Index("idx_etiqueta_activa", "es_activa"),
        Index("idx_etiqueta_comprable", "es_comprable"),
    )
    
    # Primary Key
    etiqueta_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        doc="UUID único de la etiqueta"
    )
    
    # Información básica
    nombre = Column(
        String(100),
        nullable=False,
        unique=True,
        doc="Nombre de la etiqueta"
    )
    
    descripcion = Column(
        String(500),
        nullable=True,
        doc="Descripción detallada de la etiqueta"
    )
    
    # Categorización
    categoria = Column(
        ENUM(CategoriaEtiqueta, name="categoria_etiqueta_enum", create_type=False),
        nullable=False,
        index=True,
        doc="Categoría temática de la etiqueta"
    )
    
    rareza = Column(
        ENUM(RarezaEtiqueta, name="rareza_etiqueta_enum", create_type=False),
        nullable=False,
        index=True,
        doc="Nivel de rareza de la etiqueta"
    )
    
    # Visualización
    icono_url = Column(
        String(500),
        nullable=True,
        doc="URL del icono de la etiqueta"
    )
    
    color_hex = Column(
        String(7),
        nullable=True,
        doc="Color representativo en formato hexadecimal (#RRGGBB)"
    )
    
    animacion_url = Column(
        String(500),
        nullable=True,
        doc="URL de animación (para etiquetas legendarias)"
    )
    
    # Adquisición
    precio_puntos = Column(
        Integer,
        nullable=True,
        doc="Costo en puntos (null si no se puede comprar)"
    )
    
    es_comprable = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        index=True,
        doc="Si la etiqueta se puede comprar en tienda"
    )
    
    requisito_logro = Column(
        JSON,
        nullable=True,
        doc="Requisito para desbloquear si no es comprable"
    )
    
    # Sistema de evolución
    etiqueta_evolucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("etiquetas_perfil.etiqueta_id", ondelete="SET NULL"),
        nullable=True,
        doc="ID de la etiqueta a la que evoluciona"
    )
    
    requisito_evolucion = Column(
        JSON,
        nullable=True,
        doc="Requisitos para evolucionar a la siguiente etiqueta"
    )
    
    # Estado
    es_activa = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        index=True,
        doc="Si la etiqueta está activa en el sistema"
    )
    
    orden = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Orden de visualización"
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
    
    # Relaciones
    etiqueta_evolucion = relationship(
        "EtiquetaPerfil",
        remote_side=[etiqueta_id],
        foreign_keys=[etiqueta_evolucion_id],
        backref="etiquetas_previas"
    )
    
    usuarios_etiquetas = relationship(
        "UsuarioEtiqueta",
        back_populates="etiqueta",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return (
            f"<EtiquetaPerfil("
            f"id={self.etiqueta_id}, "
            f"nombre='{self.nombre}', "
            f"categoria={self.categoria.value}, "
            f"rareza={self.rareza.value}"
            f")>"
        )
    
    @property
    def puede_evolucionar(self) -> bool:
        """
        Verifica si la etiqueta tiene evolución disponible.
        
        Returns:
            True si tiene etiqueta de evolución definida
        """
        return self.etiqueta_evolucion_id is not None
    
    @property
    def nivel_rareza_numerico(self) -> int:
        """
        Retorna un valor numérico para la rareza (para comparaciones).
        
        Returns:
            1 = Común, 2 = Raro, 3 = Épico, 4 = Legendario
        """
        rareza_map = {
            RarezaEtiqueta.COMUN: 1,
            RarezaEtiqueta.RARO: 2,
            RarezaEtiqueta.EPICO: 3,
            RarezaEtiqueta.LEGENDARIO: 4,
        }
        return rareza_map.get(self.rareza, 0)
    
    def to_dict(self) -> dict:
        """
        Convierte la etiqueta a diccionario para API.
        
        Returns:
            Diccionario con información de la etiqueta
        """
        return {
            "etiqueta_id": str(self.etiqueta_id),
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "categoria": self.categoria.value,
            "rareza": self.rareza.value,
            "icono_url": self.icono_url,
            "color_hex": self.color_hex,
            "animacion_url": self.animacion_url,
            "precio_puntos": self.precio_puntos,
            "es_comprable": self.es_comprable,
            "requisito_logro": self.requisito_logro,
            "puede_evolucionar": self.puede_evolucionar,
            "etiqueta_evolucion_id": str(self.etiqueta_evolucion_id) if self.etiqueta_evolucion_id else None,
            "requisito_evolucion": self.requisito_evolucion,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }
