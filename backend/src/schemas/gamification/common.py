"""
Schemas comunes compartidos entre módulos de gamificación.

Este módulo define schemas base y de utilidad que se reutilizan
en múltiples partes del sistema.

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional


class PaginationParams(BaseModel):
    """
    Parámetros de paginación estándar.
    
    Attributes:
        limit: Cantidad máxima de resultados (1-200)
        offset: Número de resultados a saltar (para paginación)
    
    Example:
        >>> params = PaginationParams(limit=50, offset=0)
        >>> params.limit
        50
    """
    limit: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Cantidad máxima de resultados a retornar"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Número de resultados a saltar (paginación)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "limit": 50,
                "offset": 0
            }
        }


class BaseResponse(BaseModel):
    """
    Respuesta base para operaciones exitosas.
    
    Attributes:
        success: Indica si la operación fue exitosa
        message: Mensaje descriptivo opcional
    
    Example:
        >>> response = BaseResponse(success=True, message="Operación completada")
        >>> response.success
        True
    """
    success: bool = Field(
        default=True,
        description="Indica si la operación fue exitosa"
    )
    message: Optional[str] = Field(
        default=None,
        description="Mensaje descriptivo de la operación"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operación completada exitosamente"
            }
        }


class ErrorResponse(BaseModel):
    """
    Respuesta para operaciones fallidas.
    
    Attributes:
        success: Siempre False para errores
        error: Mensaje de error principal
        details: Detalles adicionales del error (opcional)
    
    Example:
        >>> error = ErrorResponse(
        ...     error="Puntos insuficientes",
        ...     details={"puntos_requeridos": 500, "puntos_actuales": 200}
        ... )
        >>> error.success
        False
    """
    success: bool = Field(
        default=False,
        description="Siempre False para respuestas de error"
    )
    error: str = Field(
        ...,
        description="Mensaje de error principal"
    )
    details: Optional[dict] = Field(
        default=None,
        description="Detalles adicionales del error"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Puntos insuficientes",
                "details": {
                    "puntos_requeridos": 500,
                    "puntos_actuales": 200
                }
            }
        }


class SuccessMessageResponse(BaseResponse):
    """
    Respuesta simple con mensaje de éxito.
    
    Hereda de BaseResponse y es útil para operaciones
    que solo necesitan confirmar éxito con un mensaje.
    
    Example:
        >>> response = SuccessMessageResponse(message="Item equipado correctamente")
        >>> response.success
        True
    """
    message: str = Field(
        ...,
        description="Mensaje de éxito"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operación completada exitosamente"
            }
        }
