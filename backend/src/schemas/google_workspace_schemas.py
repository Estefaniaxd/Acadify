"""
Schemas para Google Workspace Resources.

Define los DTOs (Data Transfer Objects) para operaciones con Google Workspace.

Principios SOLID:
- Interface Segregation: Schemas específicos por operación
- Single Responsibility: Cada schema tiene un propósito claro
"""

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, HttpUrl, Field


class GoogleResourceType(str, Enum):
    """Tipos de recursos de Google Workspace."""
    
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    DRAWING = "drawing"
    FORM = "form"
    DRIVE_FILE = "drive_file"
    DRIVE_FOLDER = "drive_folder"


class GooglePermissionRole(str, Enum):
    """Roles de permisos en Google Workspace."""
    
    READER = "reader"
    WRITER = "writer"
    COMMENTER = "commenter"


class GoogleResourceCreate(BaseModel):
    """Schema para crear un recurso de Google Workspace.
    
    Usado cuando un estudiante crea un nuevo documento, hoja, etc.
    """
    
    type: GoogleResourceType = Field(
        ...,
        description="Tipo de recurso a crear"
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Título del recurso"
    )
    folder_id: str | None = Field(
        None,
        description="ID de carpeta Drive donde guardar (opcional)"
    )
    initial_content: str | None = Field(
        None,
        description="Contenido inicial para documentos (opcional)"
    )
    headers: list[str] | None = Field(
        None,
        description="Encabezados para hojas de cálculo (opcional)"
    )
    description: str | None = Field(
        None,
        description="Descripción para formularios (opcional)"
    )
    share_with_teacher: bool = Field(
        default=True,
        description="Si se debe compartir automáticamente con el docente"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "document",
                "title": "Mi Ensayo - Historia",
                "initial_content": "Introducción...",
                "share_with_teacher": True
            }
        }


class GoogleResourceResponse(BaseModel):
    """Schema de respuesta para un recurso de Google Workspace.
    
    Retornado después de crear o consultar un recurso.
    """
    
    id: str = Field(..., description="ID del recurso en Google")
    type: GoogleResourceType = Field(..., description="Tipo de recurso")
    name: str = Field(..., description="Nombre del recurso")
    url: str = Field(..., description="URL para ver/editar el recurso")
    web_view_link: str | None = Field(None, description="Link de visualización web")
    created_at: datetime | None = Field(None, description="Fecha de creación")
    permissions: list[str] = Field(
        default_factory=list,
        description="Lista de permisos aplicados"
    )
    metadata: dict[str, Any] | None = Field(
        None,
        description="Metadata adicional específica del tipo"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
                "type": "document",
                "name": "Mi Ensayo - Historia",
                "url": "https://docs.google.com/document/d/1Bxi.../edit",
                "web_view_link": "https://docs.google.com/document/d/1Bxi.../edit",
                "created_at": "2025-11-23T10:00:00Z",
                "permissions": ["reader", "writer"],
                "metadata": {
                    "revision_id": "ALm37BWO8kfJZo8RgPmPpJNW"
                }
            }
        }


class GoogleResourceLink(BaseModel):
    """Schema para vincular un recurso Google existente a una entrega.
    
    Usado cuando un estudiante vincula un archivo que ya existe en su Drive.
    """
    
    resource_id: str = Field(..., description="ID del recurso en Google")
    resource_type: GoogleResourceType = Field(..., description="Tipo de recurso")
    share_with_teacher: bool = Field(
        default=True,
        description="Si se debe compartir con el docente"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "resource_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
                "resource_type": "spreadsheet",
                "share_with_teacher": True
            }
        }


class GoogleResourceShare(BaseModel):
    """Schema para compartir un recurso con un usuario.
    
    Usado para gestionar permisos de recursos Google.
    """
    
    email: str = Field(..., description="Email del usuario con quien compartir")
    role: GooglePermissionRole = Field(
        default=GooglePermissionRole.READER,
        description="Rol del usuario"
    )
    send_notification: bool = Field(
        default=True,
        description="Si se debe enviar notificación por email"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "profesor@acadify.com",
                "role": "writer",
                "send_notification": True
            }
        }


class GoogleResourceMetadata(BaseModel):
    """Schema para metadata de un recurso Google.
    
    Usado para almacenar información del recurso en la BD.
    """
    
    id: str
    type: GoogleResourceType
    name: str
    url: str
    created_at: datetime
    shared_with: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
                "type": "document",
                "name": "Mi Ensayo",
                "url": "https://docs.google.com/document/d/1Bxi.../edit",
                "created_at": "2025-11-23T10:00:00Z",
                "shared_with": ["profesor@acadify.com"],
                "permissions": ["reader", "writer"]
            }
        }


class GoogleFileUpload(BaseModel):
    """Schema para subir archivo a Google Drive.
    
    Metadata que acompaña la subida de un archivo.
    """
    
    folder_id: str | None = Field(
        None,
        description="ID de carpeta Drive donde guardar"
    )
    share_with_teacher: bool = Field(
        default=True,
        description="Si se debe compartir con el docente"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "folder_id": "1dyC0jHv4F_W8qRgoPOHN3VLw",
                "share_with_teacher": True
            }
        }


class GoogleResourceList(BaseModel):
    """Schema para lista de recursos Google.
    
    Usado para retornar múltiples recursos.
    """
    
    resources: list[GoogleResourceResponse] = Field(
        default_factory=list,
        description="Lista de recursos"
    )
    total: int = Field(default=0, description="Total de recursos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "resources": [
                    {
                        "id": "1Bxi...",
                        "type": "document",
                        "name": "Ensayo 1",
                        "url": "https://docs.google.com/...",
                        "web_view_link": "https://docs.google.com/...",
                        "created_at": "2025-11-23T10:00:00Z",
                        "permissions": ["reader"]
                    }
                ],
                "total": 1
            }
        }


class GoogleFormResponses(BaseModel):
    """Schema para respuestas de Google Forms.
    
    Usado para obtener respuestas de formularios.
    """
    
    form_id: str = Field(..., description="ID del formulario")
    responses: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de respuestas"
    )
    total_responses: int = Field(default=0, description="Total de respuestas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "form_id": "1FAIpQLSe...",
                "responses": [
                    {
                        "responseId": "ACYDBNj...",
                        "createTime": "2025-11-23T10:00:00Z",
                        "answers": {}
                    }
                ],
                "total_responses": 1
            }
        }
