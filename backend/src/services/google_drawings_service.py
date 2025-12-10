"""
Servicio de Google Drawings para Acadify.

Este módulo maneja operaciones con Google Drawings:
- Creación de dibujos
- Compartir con permisos

Nota: Google Drawings no tiene API dedicada, se maneja via Drive API.

Principios SOLID:
- Single Responsibility: Solo operaciones de Drawings
- Dependency Inversion: Depende de abstracciones (Credentials)
"""

import logging
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleDrawing:
    """Representa un dibujo de Google Drawings."""
    
    def __init__(self, drawing_data: dict[str, Any]):
        self.id: str = drawing_data.get('id', '')
        self.name: str = drawing_data.get('name', '')
        self.web_view_link: str = drawing_data.get('webViewLink', '')
        self.created_time: str = drawing_data.get('createdTime', '')
    
    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'id': self.id,
            'name': self.name,
            'web_view_link': self.web_view_link,
            'type': 'drawing',
            'created_time': self.created_time,
        }


class GoogleDrawingsService:
    """Servicio para operaciones con Google Drawings.
    
    Funcionalidades:
    - Crear dibujos
    - Compartir con permisos
    
    Nota: Google Drawings se crea via Drive API con MIME type específico.
    
    Clean Code Principles:
    - Métodos pequeños y específicos
    - Nombres descriptivos
    - Manejo robusto de errores
    """
    
    DRAWING_MIME_TYPE = 'application/vnd.google-apps.drawing'
    
    def __init__(self):
        """Inicializa el servicio de Google Drawings."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _get_drive_service(self, credentials: Credentials):
        """Crea un servicio de Drive con las credenciales proporcionadas."""
        return build('drive', 'v3', credentials=credentials)
    
    async def create_drawing(
        self,
        title: str,
        folder_id: str | None = None,
        credentials: Credentials = None,
    ) -> GoogleDrawing:
        """Crea un nuevo dibujo de Google Drawings.
        
        Args:
            title: Título del dibujo
            folder_id: ID de carpeta Drive donde guardar (opcional)
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GoogleDrawing: Metadata del dibujo creado
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            drive_service = self._get_drive_service(credentials)
            
            # Metadata del dibujo
            file_metadata = {
                'name': title,
                'mimeType': self.DRAWING_MIME_TYPE,
            }
            
            # Si hay carpeta, agregar como parent
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Crear dibujo
            drawing = drive_service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink, createdTime'
            ).execute()
            
            self.logger.info(
                f"Dibujo creado: {drawing.get('name')} "
                f"(ID: {drawing.get('id')})"
            )
            
            return GoogleDrawing(drawing)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al crear dibujo: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al crear dibujo: {e}")
            raise
    
    async def get_drawing(
        self,
        drawing_id: str,
        credentials: Credentials = None,
    ) -> GoogleDrawing:
        """Obtiene metadata de un dibujo.
        
        Args:
            drawing_id: ID del dibujo
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GoogleDrawing: Metadata del dibujo
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            drive_service = self._get_drive_service(credentials)
            
            # Obtener dibujo
            drawing = drive_service.files().get(
                fileId=drawing_id,
                fields='id, name, webViewLink, createdTime'
            ).execute()
            
            return GoogleDrawing(drawing)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al obtener dibujo: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al obtener dibujo: {e}")
            raise
    
    async def share_drawing(
        self,
        drawing_id: str,
        email: str,
        role: str = 'reader',
        credentials: Credentials = None,
    ) -> dict[str, Any]:
        """Comparte un dibujo con un usuario.
        
        Args:
            drawing_id: ID del dibujo
            email: Email del usuario con quien compartir
            role: Rol del usuario ('reader', 'writer', 'commenter')
            credentials: Credenciales OAuth del usuario
            
        Returns:
            dict: Información del permiso creado
            
        Raises:
            ValueError: Si las credenciales o parámetros son inválidos
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        if role not in ['reader', 'writer', 'commenter']:
            raise ValueError(f"Rol inválido: {role}")
        
        try:
            drive_service = self._get_drive_service(credentials)
            
            # Crear permiso
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email,
            }
            
            # Aplicar permiso
            result = drive_service.permissions().create(
                fileId=drawing_id,
                body=permission,
                fields='id, type, role, emailAddress',
                sendNotificationEmail=True,
            ).execute()
            
            self.logger.info(
                f"Dibujo {drawing_id} compartido con {email} como {role}"
            )
            
            return result
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al compartir dibujo: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al compartir dibujo: {e}")
            raise


# Instancia global del servicio
google_drawings_service = GoogleDrawingsService()
