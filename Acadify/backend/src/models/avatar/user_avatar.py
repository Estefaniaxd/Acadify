"""
Modelo para avatars de usuarios.
"""

from sqlalchemy import Column, String, Boolean, JSON, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.base_class import Base


class UserAvatar(Base):
    """
    Modelo para almacenar avatars creados por usuarios.
    Cada avatar es una composición de capas (assets) guardada como imagen final.
    """
    __tablename__ = "user_avatar"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()")
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID del usuario propietario del avatar"
    )
    
    name = Column(
        String(100),
        nullable=False,
        doc="Nombre del avatar asignado por el usuario"
    )
    
    base_gender = Column(
        String(20),
        nullable=False,
        default='male',
        server_default=text("'male'"),
        doc="Género base del avatar: male o female"
    )
    
    layers = Column(
        JSON,
        nullable=False,
        doc="Lista ordenada de capas: [{'category': 'hair', 'filename': 'hair/short_black.png'}, ...]"
    )
    
    image_url = Column(
        String(500),
        nullable=False,
        doc="URL de la imagen compuesta final (ej: /static/avatars/{user_id}/{avatar_id}.png)"
    )
    
    layers_hash = Column(
        String(64),
        nullable=False,
        index=True,
        doc="Hash SHA256 de las capas para cache y deduplicación"
    )
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        doc="Si este avatar está activo como avatar principal del usuario"
    )
    
    is_public = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        doc="Si el avatar es público (visible para otros usuarios)"
    )
    
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relación con Usuario
    user = relationship(
        "Usuario",
        backref="avatars",
        foreign_keys=[user_id]
    )

    def __repr__(self):
        return f"<UserAvatar(id={self.id}, user_id={self.user_id}, name={self.name}, active={self.is_active})>"

    @property
    def filename(self):
        """Retorna el nombre del archivo de imagen."""
        if self.image_url:
            return self.image_url.split('/')[-1]
        return f"{self.id}.png"

    @property
    def full_image_path(self):
        """Retorna la ruta completa del archivo de imagen."""
        return f"static/avatars/{self.user_id}/{self.filename}"

    def get_layer_by_category(self, category: str):
        """
        Obtiene la capa de una categoría específica.
        
        Args:
            category: Categoría de la capa (hair, eyes, etc.)
            
        Returns:
            Dict con información de la capa o None si no existe
        """
        if not self.layers:
            return None
            
        for layer in self.layers:
            if layer.get('category') == category:
                return layer
        return None

    def has_category(self, category: str) -> bool:
        """
        Verifica si el avatar tiene una capa de la categoría especificada.
        
        Args:
            category: Categoría a verificar
            
        Returns:
            True si tiene la categoría, False si no
        """
        return self.get_layer_by_category(category) is not None

    def get_categories(self) -> list:
        """
        Retorna lista de categorías presentes en el avatar.
        
        Returns:
            Lista de nombres de categorías
        """
        if not self.layers:
            return []
        return [layer.get('category') for layer in self.layers if layer.get('category')]