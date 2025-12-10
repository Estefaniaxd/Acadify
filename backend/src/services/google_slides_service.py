"""
Servicio de Google Slides para Acadify.

Este módulo maneja operaciones con Google Slides:
- Creación de presentaciones
- Agregar diapositivas
- Compartir con permisos

Principios SOLID:
- Single Responsibility: Solo operaciones de Slides
- Dependency Inversion: Depende de abstracciones (Credentials)
"""

import logging
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GooglePresentation:
    """Representa una presentación de Google Slides."""
    
    def __init__(self, presentation_data: dict[str, Any]):
        self.id: str = presentation_data.get('presentationId', '')
        self.title: str = presentation_data.get('title', '')
        self.web_view_link: str = f"https://docs.google.com/presentation/d/{self.id}/edit"
        self.slides: list[dict] = presentation_data.get('slides', [])
    
    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'id': self.id,
            'title': self.title,
            'web_view_link': self.web_view_link,
            'type': 'presentation',
            'slides_count': len(self.slides),
        }


class GoogleSlidesService:
    """Servicio para operaciones con Google Slides.
    
    Funcionalidades:
    - Crear presentaciones
    - Agregar diapositivas con layouts
    - Compartir con permisos
    
    Clean Code Principles:
    - Métodos pequeños y específicos
    - Nombres descriptivos
    - Manejo robusto de errores
    """
    
    def __init__(self):
        """Inicializa el servicio de Google Slides."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _get_slides_service(self, credentials: Credentials):
        """Crea un servicio de Slides con las credenciales proporcionadas."""
        return build('slides', 'v1', credentials=credentials)
    
    def _get_drive_service(self, credentials: Credentials):
        """Crea un servicio de Drive para operaciones de archivo."""
        return build('drive', 'v3', credentials=credentials)
    
    async def create_presentation(
        self,
        title: str,
        folder_id: str | None = None,
        credentials: Credentials = None,
    ) -> GooglePresentation:
        """Crea una nueva presentación de Google Slides.
        
        Args:
            title: Título de la presentación
            folder_id: ID de carpeta Drive donde guardar (opcional)
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GooglePresentation: Metadata de la presentación creada
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            slides_service = self._get_slides_service(credentials)
            
            # Crear presentación
            presentation = {
                'title': title
            }
            
            pres = slides_service.presentations().create(
                body=presentation
            ).execute()
            
            self.logger.info(
                f"Presentación creada: {pres.get('title')} "
                f"(ID: {pres.get('presentationId')})"
            )
            
            # Si hay carpeta, mover la presentación
            if folder_id:
                await self._move_to_folder(
                    file_id=pres.get('presentationId'),
                    folder_id=folder_id,
                    credentials=credentials
                )
            
            return GooglePresentation(pres)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al crear presentación: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al crear presentación: {e}")
            raise
    
    async def get_presentation(
        self,
        presentation_id: str,
        credentials: Credentials = None,
    ) -> GooglePresentation:
        """Obtiene metadata de una presentación.
        
        Args:
            presentation_id: ID de la presentación
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GooglePresentation: Metadata de la presentación
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            slides_service = self._get_slides_service(credentials)
            
            # Obtener presentación
            pres = slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            return GooglePresentation(pres)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al obtener presentación: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al obtener presentación: {e}")
            raise
    
    async def share_presentation(
        self,
        presentation_id: str,
        email: str,
        role: str = 'reader',
        credentials: Credentials = None,
    ) -> dict[str, Any]:
        """Comparte una presentación con un usuario.
        
        Args:
            presentation_id: ID de la presentación
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
                fileId=presentation_id,
                body=permission,
                fields='id, type, role, emailAddress',
                sendNotificationEmail=True,
            ).execute()
            
            self.logger.info(
                f"Presentación {presentation_id} compartida con {email} como {role}"
            )
            
            return result
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al compartir presentación: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al compartir presentación: {e}")
            raise
    
    async def _move_to_folder(
        self,
        file_id: str,
        folder_id: str,
        credentials: Credentials,
    ) -> None:
        """Mueve un archivo a una carpeta específica (método interno)."""
        try:
            drive_service = self._get_drive_service(credentials)
            
            # Obtener parents actuales
            file = drive_service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()
            
            previous_parents = ','.join(file.get('parents', []))
            
            # Mover a nueva carpeta
            drive_service.files().update(
                fileId=file_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            self.logger.info(f"Archivo {file_id} movido a carpeta {folder_id}")
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al mover archivo: {e}")
            raise


# Instancia global del servicio
google_slides_service = GoogleSlidesService()
