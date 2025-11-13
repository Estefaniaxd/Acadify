"""
Schemas para personalización de perfil (foto, banner, marco).
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from uuid import UUID


class FotoPerfilUpdate(BaseModel):
    """Schema para actualizar foto de perfil."""
    usa_foto_custom: bool = Field(..., description="True para foto custom, False para avatar")
    
    class Config:
        from_attributes = True


class BannerUpdate(BaseModel):
    """Schema para actualizar banner desde tienda."""
    banner_activo_id: Optional[UUID] = Field(None, description="ID del item de banner de la tienda (None para quitar)")
    
    class Config:
        from_attributes = True


class MarcoPerfilUpdate(BaseModel):
    """Schema para actualizar marco de perfil."""
    marco_perfil_id: Optional[UUID] = Field(None, description="ID del item de marco de la tienda (None para quitar)")
    
    class Config:
        from_attributes = True


class PerfilPersonalizacionResponse(BaseModel):
    """Respuesta con toda la personalización del perfil."""
    usuario_id: UUID
    
    # Foto de perfil
    usa_foto_custom: bool
    foto_perfil_custom_url: Optional[str] = None
    avatar_url: Optional[str] = None  # URL del avatar generado
    
    # Banner/Portada
    banner_url: Optional[str] = None  # Banner custom subido
    banner_activo_id: Optional[UUID] = None
    banner_activo_nombre: Optional[str] = None
    banner_activo_preview: Optional[str] = None
    
    # Marco
    marco_perfil_id: Optional[UUID] = None
    marco_perfil_nombre: Optional[str] = None
    marco_perfil_preview: Optional[str] = None
    
    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    """Respuesta después de subir una imagen."""
    success: bool
    url: str
    message: str = "Imagen subida correctamente"
    
    class Config:
        from_attributes = True
