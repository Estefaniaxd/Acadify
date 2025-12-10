"""
Esquemas Pydantic para el sistema de avatars.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# ======================
# Tipos y Literales
# ======================

GenderType = Literal["male", "female", "unisex"]

CategoryType = Literal[
    "base",
    "hair",
    "eyes",
    "mouth",
    "makeup",
    "clothes",
    "accessories",
    "backgrounds",
]

SubcategoryType = Literal[
    # CLOTHES
    "shirt", "pants", "skirt", "jacket", "socks", "shoes", "dress", "underwear",
    # HAIR
    "short", "medium", "long", "curly", "straight", "wavy", "ponytail", "braid",
    # ACCESSORIES
    "glasses", "hat", "earrings", "necklace", "bracelet", "ring", "watch", "headband", "mask",
    # EYES
    "normal", "anime", "realistic",
    # MAKEUP
    "lipstick", "eyeshadow", "blush", "eyeliner",
    # BACKGROUNDS
    "solid", "gradient", "pattern", "scene",
    # GENERAL
    "other", "none",
]

# ======================
# Layer y componentes base
# ======================


class LayerItem(BaseModel):
    """Representa una capa individual del avatar."""

    category: str = Field(
        ...,
        description="Categoría de la capa (hair, eyes, clothes, etc.)",
        min_length=1,
        max_length=50,
    )
    file: str = Field(
        ...,
        description="Nombre o ruta relativa del archivo (ej: hair/short_black.png o hair_4.png)",
        min_length=1,
        max_length=255,
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        """Valida que la categoría sea una de las permitidas."""
        allowed_categories = {
            "base",
            "hair",
            "eyes",
            "accessories",
            "backgrounds",
            "makeup",
            "mouth",
            "shirt",
            "pants",
            "skirt",
            "socks",
            "shoes",
            "jacket",
        }
        if v not in allowed_categories:
            raise ValueError(
                f"Category must be one of: {', '.join(allowed_categories)}"
            )
        return v

    @field_validator("file")
    @classmethod
    def validate_file(cls, v):
        """Valida el formato del archivo."""
        if not (v.endswith(".png") or v.endswith(".jpeg") or v.endswith(".jpg")):
            raise ValueError("File must be a PNG or JPEG image")
        # Permitimos tanto rutas con categoría (e.g. hair/short_black.png)
        # como basenames (e.g. hair_4.png). Las rutas sin categoría serán
        # resueltas en tiempo de ejecución por la lógica del servicio (validate_layers).
        return v


# ======================
# Requests (entrada)
# ======================


class PreviewRequest(BaseModel):
    """Request para generar preview de avatar."""

    base_gender: str = Field(
        ...,
        description="Género base del avatar (male o female)",
        pattern="^(male|female)$",
    )
    layers: List[LayerItem] = Field(
        ..., description="Lista de capas del avatar", min_length=1, max_length=15
    )

    @field_validator("layers")
    @classmethod
    def validate_layers_unique_categories(cls, layers):
        """Valida que no haya categorías duplicadas."""
        categories = [layer.category for layer in layers]
        if len(categories) != len(set(categories)):
            raise ValueError("Duplicate categories not allowed")
        return layers


class SaveAvatarRequest(BaseModel):
    """Request para guardar avatar permanentemente."""

    name: str = Field(
        ..., description="Nombre del avatar", min_length=1, max_length=100
    )
    base_gender: str = Field(
        ...,
        description="Género base del avatar (male o female)",
        pattern="^(male|female)$",
    )
    layers: List[LayerItem] = Field(
        ..., description="Lista de capas del avatar", min_length=1, max_length=15
    )
    is_active: bool = Field(
        default=False, description="Si este avatar será el activo del usuario"
    )
    is_public: bool = Field(default=True, description="Si el avatar será público")

    @field_validator("layers")
    @classmethod
    def validate_layers_unique_categories(cls, layers):
        """Valida que no haya categorías duplicadas."""
        categories = [layer.category for layer in layers]
        if len(categories) != len(set(categories)):
            raise ValueError("Duplicate categories not allowed")
        return layers


class UpdateAvatarRequest(BaseModel):
    """Request para actualizar avatar existente."""

    name: Optional[str] = Field(
        default=None,
        description="Nuevo nombre del avatar",
        min_length=1,
        max_length=100,
    )
    is_active: Optional[bool] = Field(
        default=None, description="Si este avatar será el activo"
    )
    is_public: Optional[bool] = Field(
        default=None, description="Si el avatar será público"
    )


# ======================
# Responses (salida)
# ======================


class AssetInfo(BaseModel):
    """Información de un asset individual."""

    id: str = Field(..., description="ID único del asset")
    filename: str = Field(..., description="Nombre del archivo")
    display_name: str = Field(..., description="Nombre para mostrar")
    category: str = Field(..., description="Categoría del asset")
    subcategory: Optional[str] = Field(None, description="Subcategoría del asset")
    target_gender: GenderType = Field(..., description="Género sugerido (informativo, NO bloquea uso)")
    url: str = Field(..., description="URL completa del asset")
    width: int = Field(..., description="Ancho en píxeles")
    height: int = Field(..., description="Alto en píxeles")
    file_size: int = Field(..., description="Tamaño en bytes")
    is_normalized: bool = Field(..., description="Si tiene la resolución estándar")
    meta_info: Dict[str, Any] = Field(
        default_factory=dict, description="Metadatos adicionales"
    )


class ManifestResponse(BaseModel):
    """Response del manifest de assets."""

    resolution: List[int] = Field(
        ..., description="Resolución estándar [width, height]"
    )
    categories: Dict[str, List[AssetInfo]] = Field(
        ..., description="Assets por categoría (flat)"
    )
    hierarchical: Optional[Dict[str, Dict[str, List[AssetInfo]]]] = Field(
        None, description="Assets organizados jerárquicamente: category -> subcategory -> assets"
    )
    total_assets: int = Field(..., description="Total de assets disponibles")


class PreviewResponse(BaseModel):
    """Response del preview de avatar."""

    preview_url: str = Field(..., description="URL del preview generado")
    layers_hash: str = Field(..., description="Hash de las capas para cache")
    from_cache: bool = Field(..., description="Si el preview vino del cache")


class UserAvatarResponse(BaseModel):
    """Response de avatar de usuario."""

    id: str = Field(..., description="ID único del avatar")
    user_id: str = Field(..., description="ID del usuario propietario")
    name: str = Field(..., description="Nombre del avatar")
    base_gender: str = Field(..., description="Género base del avatar")
    layers: List[LayerItem] = Field(..., description="Capas del avatar")
    image_url: str = Field(..., description="URL de la imagen final")
    layers_hash: str = Field(..., description="Hash de las capas")
    is_active: bool = Field(..., description="Si es el avatar activo")
    is_public: bool = Field(..., description="Si es público")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        from_attributes = True


class UserAvatarListResponse(BaseModel):
    """Response de lista de avatars de usuario."""

    avatars: List[UserAvatarResponse] = Field(..., description="Lista de avatars")
    total: int = Field(..., description="Total de avatars del usuario")
    has_active: bool = Field(..., description="Si el usuario tiene avatar activo")
    active_avatar_id: Optional[str] = Field(
        default=None, description="ID del avatar activo"
    )


class PopularAvatarResponse(BaseModel):
    """Response de avatar popular."""

    avatar: UserAvatarResponse = Field(..., description="Información del avatar")
    usage_count: int = Field(..., description="Número de usuarios que lo usan")
    layers_hash: str = Field(..., description="Hash de las capas")


class AvatarStatsResponse(BaseModel):
    """Response de estadísticas de avatars."""

    total_avatars: int = Field(..., description="Total de avatars en el sistema")
    total_users_with_avatars: int = Field(
        ..., description="Usuarios con al menos un avatar"
    )
    popular_avatars: List[PopularAvatarResponse] = Field(
        ..., description="Avatars más populares"
    )
    categories_stats: Dict[str, int] = Field(
        ..., description="Estadísticas por categoría"
    )


class UserStatsResponse(BaseModel):
    """Response de estadísticas de usuario."""

    total_avatars: int = Field(..., description="Total de avatars del usuario")
    public_avatars: int = Field(..., description="Avatars públicos")
    private_avatars: int = Field(..., description="Avatars privados")
    has_active_avatar: bool = Field(..., description="Si tiene avatar activo")
    active_avatar_id: Optional[str] = Field(
        default=None, description="ID del avatar activo"
    )


class CacheStatsResponse(BaseModel):
    """Response de estadísticas del cache."""

    compositions_cached: int = Field(..., description="Composiciones en cache")
    previews_cached: int = Field(..., description="Previews en cache")
    total_keys: int = Field(..., description="Total de claves en cache")
    memory_used: str = Field(..., description="Memoria usada")
    cache_ttl_hours: int = Field(..., description="TTL del cache en horas")


# ======================
# Error responses
# ======================


class ErrorResponse(BaseModel):
    """Response de error estándar."""

    error: str = Field(..., description="Mensaje de error")
    details: Optional[str] = Field(default=None, description="Detalles adicionales")
    error_code: Optional[str] = Field(default=None, description="Código de error")


class ValidationErrorResponse(BaseModel):
    """Response de error de validación."""

    error: str = Field(..., description="Mensaje de error")
    validation_errors: List[Dict[str, Any]] = Field(
        ..., description="Errores de validación"
    )


# ======================
# Exports
# ======================

__all__ = [
    # Layer components
    "LayerItem",
    # Requests
    "PreviewRequest",
    "SaveAvatarRequest",
    "UpdateAvatarRequest",
    # Responses
    "AssetInfo",
    "ManifestResponse",
    "PreviewResponse",
    "UserAvatarResponse",
    "UserAvatarListResponse",
    "PopularAvatarResponse",
    "AvatarStatsResponse",
    "UserStatsResponse",
    "CacheStatsResponse",
    # Errors
    "ErrorResponse",
    "ValidationErrorResponse",
]
