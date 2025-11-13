"""Modelo para assets de avatars (archivos de imágenes base)."""

from sqlalchemy import JSON, Column, Integer, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.sql import func

from src.db.base_class import Base


class AvatarAsset(Base):
    """Modelo para almacenar información de assets disponibles para avatars.
    Cada asset representa una imagen PNG que puede formar parte de un avatar.
    """

    __tablename__ = "avatar_asset"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )

    category = Column(
        String(50),
        nullable=False,
        index=True,
        doc="Categoría del asset: base, hair, eyes, clothes, accessories, backgrounds",
    )

    target_gender = Column(
        String(20),
        nullable=False,
        default="unisex",
        server_default=text("'unisex'"),
        index=True,
        doc="Género objetivo del asset: male, female, unisex",
    )

    filename = Column(
        String(255),
        nullable=False,
        unique=True,
        doc="Nombre del archivo relativo a static/assets/ (ej: hair/short_black.png)",
    )

    display_name = Column(
        String(100), nullable=True, doc="Nombre amigable para mostrar en UI (opcional)"
    )

    file_size = Column(Integer, nullable=False, doc="Tamaño del archivo en bytes")

    width = Column(Integer, nullable=False, doc="Ancho de la imagen en píxeles")

    height = Column(Integer, nullable=False, doc="Alto de la imagen en píxeles")

    meta_info = Column(
        JSON, nullable=True, doc="Metadatos adicionales: color, tags, rarity, etc."
    )

    is_active = Column(
        String(1),
        nullable=False,
        default="Y",
        server_default=text("'Y'"),
        doc="Si el asset está activo y disponible para uso",
    )

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<AvatarAsset(id={self.id}, category={self.category}, filename={self.filename})>"

    @property
    def relative_path(self):
        """Retorna la ruta relativa del asset."""
        return self.filename

    @property
    def is_normalized(self):
        """Verifica si el asset tiene la resolución estándar (512x512)."""
        return self.width == 512 and self.height == 512
