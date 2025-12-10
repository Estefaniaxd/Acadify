"""
Manager centralizado para Google Workspace.

Este módulo orquesta todos los servicios de Google Workspace:
- Drive, Docs, Sheets, Slides, Drawings, Forms
- Factory pattern para creación de recursos
- Gestión centralizada de credenciales

Principios SOLID:
- Facade Pattern: Simplifica acceso a múltiples servicios
- Single Responsibility: Orquestación y coordinación
- Open/Closed: Extensible para nuevos servicios
"""

import logging
from enum import Enum
from typing import Any

from fastapi import UploadFile
from google.oauth2.credentials import Credentials

from src.services.google_drive_service import (
    GoogleDriveService,
    GoogleDriveFile,
    GoogleDriveFolder,
)
from src.services.google_docs_service import GoogleDocsService, GoogleDocument
from src.services.google_sheets_service import GoogleSheetsService, GoogleSpreadsheet
from src.services.google_slides_service import GoogleSlidesService, GooglePresentation
from src.services.google_drawings_service import GoogleDrawingsService, GoogleDrawing
from src.services.google_forms_service import GoogleFormsService, GoogleForm

logger = logging.getLogger(__name__)


class GoogleResourceType(str, Enum):
    """Tipos de recursos de Google Workspace."""
    
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    DRAWING = "drawing"
    FORM = "form"
    DRIVE_FILE = "drive_file"
    DRIVE_FOLDER = "drive_folder"


class GoogleWorkspaceManager:
    """Manager centralizado para Google Workspace.
    
    Aplica Facade Pattern para simplificar acceso a servicios Google.
    
    Responsabilidades:
    - Orquestar servicios individuales
    - Factory method para crear recursos
    - Gestión unificada de errores
    - Logging centralizado
    
    Clean Code Principles:
    - Nombres descriptivos
    - Métodos pequeños y específicos
    - Separación de responsabilidades
    """
    
    def __init__(self):
        """Inicializa el manager con todos los servicios."""
        self.drive = GoogleDriveService()
        self.docs = GoogleDocsService()
        self.sheets = GoogleSheetsService()
        self.slides = GoogleSlidesService()
        self.drawings = GoogleDrawingsService()
        self.forms = GoogleFormsService()
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create_resource(
        self,
        resource_type: GoogleResourceType,
        title: str,
        credentials: Credentials,
        **kwargs
    ) -> dict[str, Any]:
        """Factory method para crear recursos Google.
        
        Args:
            resource_type: Tipo de recurso a crear
            title: Título del recurso
            credentials: Credenciales OAuth del usuario
            **kwargs: Argumentos adicionales específicos del tipo
            
        Returns:
            dict: Metadata del recurso creado
            
        Raises:
            ValueError: Si el tipo de recurso es inválido
            Exception: Si hay error al crear el recurso
        """
        self.logger.info(f"Creando recurso tipo {resource_type}: {title}")
        
        try:
            if resource_type == GoogleResourceType.DOCUMENT:
                doc = await self.docs.create_document(
                    title=title,
                    initial_content=kwargs.get('initial_content'),
                    folder_id=kwargs.get('folder_id'),
                    credentials=credentials
                )
                return doc.to_dict()
            
            elif resource_type == GoogleResourceType.SPREADSHEET:
                sheet = await self.sheets.create_spreadsheet(
                    title=title,
                    headers=kwargs.get('headers'),
                    folder_id=kwargs.get('folder_id'),
                    credentials=credentials
                )
                return sheet.to_dict()
            
            elif resource_type == GoogleResourceType.PRESENTATION:
                pres = await self.slides.create_presentation(
                    title=title,
                    folder_id=kwargs.get('folder_id'),
                    credentials=credentials
                )
                return pres.to_dict()
            
            elif resource_type == GoogleResourceType.DRAWING:
                drawing = await self.drawings.create_drawing(
                    title=title,
                    folder_id=kwargs.get('folder_id'),
                    credentials=credentials
                )
                return drawing.to_dict()
            
            elif resource_type == GoogleResourceType.FORM:
                form = await self.forms.create_form(
                    title=title,
                    description=kwargs.get('description'),
                    folder_id=kwargs.get('folder_id'),
                    credentials=credentials
                )
                return form.to_dict()
            
            elif resource_type == GoogleResourceType.DRIVE_FOLDER:
                folder = await self.drive.create_folder(
                    name=title,
                    parent_id=kwargs.get('parent_id'),
                    credentials=credentials
                )
                return folder.to_dict()
            
            else:
                raise ValueError(f"Tipo de recurso no soportado: {resource_type}")
        
        except Exception as e:
            self.logger.error(
                f"Error al crear recurso {resource_type}: {e}",
                exc_info=True
            )
            raise
    
    async def upload_file(
        self,
        file: UploadFile,
        folder_id: str | None,
        credentials: Credentials,
    ) -> dict[str, Any]:
        """Sube un archivo a Google Drive.
        
        Args:
            file: Archivo a subir
            folder_id: ID de carpeta destino (opcional)
            credentials: Credenciales OAuth del usuario
            
        Returns:
            dict: Metadata del archivo subido
        """
        self.logger.info(f"Subiendo archivo: {file.filename}")
        
        try:
            drive_file = await self.drive.upload_file(
                file=file,
                folder_id=folder_id,
                credentials=credentials
            )
            return drive_file.to_dict()
        
        except Exception as e:
            self.logger.error(f"Error al subir archivo: {e}", exc_info=True)
            raise
    
    async def share_resource(
        self,
        resource_id: str,
        resource_type: GoogleResourceType,
        email: str,
        role: str,
        credentials: Credentials,
    ) -> dict[str, Any]:
        """Comparte un recurso con un usuario.
        
        Args:
            resource_id: ID del recurso
            resource_type: Tipo de recurso
            email: Email del usuario con quien compartir
            role: Rol del usuario ('reader', 'writer', 'commenter')
            credentials: Credenciales OAuth del usuario
            
        Returns:
            dict: Información del permiso creado
        """
        self.logger.info(
            f"Compartiendo {resource_type} {resource_id} con {email} como {role}"
        )
        
        try:
            if resource_type == GoogleResourceType.DOCUMENT:
                return await self.docs.share_document(
                    doc_id=resource_id,
                    email=email,
                    role=role,
                    credentials=credentials
                )
            
            elif resource_type == GoogleResourceType.SPREADSHEET:
                return await self.sheets.share_spreadsheet(
                    sheet_id=resource_id,
                    email=email,
                    role=role,
                    credentials=credentials
                )
            
            elif resource_type == GoogleResourceType.PRESENTATION:
                return await self.slides.share_presentation(
                    presentation_id=resource_id,
                    email=email,
                    role=role,
                    credentials=credentials
                )
            
            elif resource_type == GoogleResourceType.DRAWING:
                return await self.drawings.share_drawing(
                    drawing_id=resource_id,
                    email=email,
                    role=role,
                    credentials=credentials
                )
            
            elif resource_type == GoogleResourceType.FORM:
                return await self.forms.share_form(
                    form_id=resource_id,
                    email=email,
                    role=role,
                    credentials=credentials
                )
            
            elif resource_type in [GoogleResourceType.DRIVE_FILE, GoogleResourceType.DRIVE_FOLDER]:
                return await self.drive.share_with_user(
                    file_id=resource_id,
                    email=email,
                    role=role,
                    credentials=credentials
                )
            
            else:
                raise ValueError(f"Tipo de recurso no soportado: {resource_type}")
        
        except Exception as e:
            self.logger.error(f"Error al compartir recurso: {e}", exc_info=True)
            raise
    
    async def get_resource_metadata(
        self,
        resource_id: str,
        resource_type: GoogleResourceType,
        credentials: Credentials,
    ) -> dict[str, Any]:
        """Obtiene metadata de un recurso.
        
        Args:
            resource_id: ID del recurso
            resource_type: Tipo de recurso
            credentials: Credenciales OAuth del usuario
            
        Returns:
            dict: Metadata del recurso
        """
        self.logger.info(f"Obteniendo metadata de {resource_type} {resource_id}")
        
        try:
            if resource_type == GoogleResourceType.DOCUMENT:
                doc = await self.docs.get_document(
                    doc_id=resource_id,
                    credentials=credentials
                )
                return doc.to_dict()
            
            elif resource_type == GoogleResourceType.SPREADSHEET:
                sheet = await self.sheets.get_spreadsheet(
                    sheet_id=resource_id,
                    credentials=credentials
                )
                return sheet.to_dict()
            
            elif resource_type == GoogleResourceType.PRESENTATION:
                pres = await self.slides.get_presentation(
                    presentation_id=resource_id,
                    credentials=credentials
                )
                return pres.to_dict()
            
            elif resource_type == GoogleResourceType.DRAWING:
                drawing = await self.drawings.get_drawing(
                    drawing_id=resource_id,
                    credentials=credentials
                )
                return drawing.to_dict()
            
            elif resource_type == GoogleResourceType.FORM:
                form = await self.forms.get_form(
                    form_id=resource_id,
                    credentials=credentials
                )
                return form.to_dict()
            
            elif resource_type in [GoogleResourceType.DRIVE_FILE, GoogleResourceType.DRIVE_FOLDER]:
                file = await self.drive.get_file_metadata(
                    file_id=resource_id,
                    credentials=credentials
                )
                return file.to_dict()
            
            else:
                raise ValueError(f"Tipo de recurso no soportado: {resource_type}")
        
        except Exception as e:
            self.logger.error(f"Error al obtener metadata: {e}", exc_info=True)
            raise
    
    async def delete_resource(
        self,
        resource_id: str,
        credentials: Credentials,
    ) -> bool:
        """Elimina un recurso de Google Drive.
        
        Nota: Todos los recursos de Workspace se eliminan via Drive API.
        
        Args:
            resource_id: ID del recurso
            credentials: Credenciales OAuth del usuario
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        self.logger.info(f"Eliminando recurso {resource_id}")
        
        try:
            return await self.drive.delete_file(
                file_id=resource_id,
                credentials=credentials
            )
        
        except Exception as e:
            self.logger.error(f"Error al eliminar recurso: {e}", exc_info=True)
            raise


# Instancia global del manager
google_workspace_manager = GoogleWorkspaceManager()
