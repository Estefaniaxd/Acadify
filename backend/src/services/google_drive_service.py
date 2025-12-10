"""
Servicio de Google Drive para Acadify.

Este módulo maneja todas las operaciones con Google Drive:
- Subida de archivos
- Creación de carpetas organizadas
- Gestión de permisos compartidos
- Metadata de archivos

Principios SOLID:
- Single Responsibility: Solo operaciones de Drive
- Open/Closed: Extensible para nuevas operaciones
- Dependency Inversion: Depende de abstracciones (Credentials)
"""

import logging
from typing import Any
from datetime import datetime
from io import BytesIO

from fastapi import UploadFile
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleDriveFile:
    """Representa un archivo en Google Drive."""
    
    def __init__(self, file_data: dict[str, Any]):
        self.id: str = file_data.get('id', '')
        self.name: str = file_data.get('name', '')
        self.mime_type: str = file_data.get('mimeType', '')
        self.web_view_link: str = file_data.get('webViewLink', '')
        self.web_content_link: str = file_data.get('webContentLink', '')
        self.created_time: str = file_data.get('createdTime', '')
        self.modified_time: str = file_data.get('modifiedTime', '')
        self.size: int = int(file_data.get('size', 0)) if file_data.get('size') else 0
        self.owners: list[dict] = file_data.get('owners', [])
        self.permissions: list[dict] = file_data.get('permissions', [])
    
    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'id': self.id,
            'name': self.name,
            'mime_type': self.mime_type,
            'web_view_link': self.web_view_link,
            'web_content_link': self.web_content_link,
            'created_time': self.created_time,
            'modified_time': self.modified_time,
            'size': self.size,
            'owners': self.owners,
        }


class GoogleDriveFolder:
    """Representa una carpeta en Google Drive."""
    
    def __init__(self, folder_data: dict[str, Any]):
        self.id: str = folder_data.get('id', '')
        self.name: str = folder_data.get('name', '')
        self.web_view_link: str = folder_data.get('webViewLink', '')
        self.created_time: str = folder_data.get('createdTime', '')
    
    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'id': self.id,
            'name': self.name,
            'web_view_link': self.web_view_link,
            'created_time': self.created_time,
        }


class GoogleDriveService:
    """Servicio para operaciones con Google Drive.
    
    Funcionalidades:
    - Subir archivos a Drive
    - Crear carpetas organizadas por tarea
    - Gestionar permisos (compartir con docente)
    - Obtener metadata de archivos
    - Eliminar archivos
    
    Clean Code Principles:
    - Métodos pequeños con una sola responsabilidad
    - Nombres descriptivos y específicos
    - Type hints completos
    - Manejo robusto de errores
    """
    
    FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'
    
    def __init__(self):
        """Inicializa el servicio de Google Drive."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _get_drive_service(self, credentials: Credentials):
        """Crea un servicio de Drive con las credenciales proporcionadas.
        
        Args:
            credentials: Credenciales OAuth del usuario
            
        Returns:
            Resource: Servicio de Google Drive
        """
        return build('drive', 'v3', credentials=credentials)
    
    async def upload_file(
        self,
        file: UploadFile,
        folder_id: str | None = None,
        credentials: Credentials = None,
    ) -> GoogleDriveFile:
        """Sube un archivo a Google Drive.
        
        Args:
            file: Archivo a subir (FastAPI UploadFile)
            folder_id: ID de la carpeta destino (opcional)
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GoogleDriveFile: Metadata del archivo subido
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            service = self._get_drive_service(credentials)
            
            # Leer contenido del archivo
            file_content = await file.read()
            file_stream = BytesIO(file_content)
            
            # Metadata del archivo
            file_metadata = {
                'name': file.filename,
            }
            
            # Si hay carpeta, agregar como parent
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Media upload
            media = MediaIoBaseUpload(
                file_stream,
                mimetype=file.content_type or 'application/octet-stream',
                resumable=True
            )
            
            # Subir archivo
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, webViewLink, webContentLink, createdTime, modifiedTime, size, owners'
            ).execute()
            
            self.logger.info(
                f"Archivo subido exitosamente a Drive: {uploaded_file.get('name')} "
                f"(ID: {uploaded_file.get('id')})"
            )
            
            return GoogleDriveFile(uploaded_file)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al subir archivo a Drive: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al subir archivo: {e}")
            raise
    
    async def create_folder(
        self,
        name: str,
        parent_id: str | None = None,
        credentials: Credentials = None,
    ) -> GoogleDriveFolder:
        """Crea una carpeta en Google Drive.
        
        Args:
            name: Nombre de la carpeta
            parent_id: ID de la carpeta padre (opcional)
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GoogleDriveFolder: Metadata de la carpeta creada
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            service = self._get_drive_service(credentials)
            
            # Metadata de la carpeta
            folder_metadata = {
                'name': name,
                'mimeType': self.FOLDER_MIME_TYPE,
            }
            
            # Si hay carpeta padre, agregar como parent
            if parent_id:
                folder_metadata['parents'] = [parent_id]
            
            # Crear carpeta
            folder = service.files().create(
                body=folder_metadata,
                fields='id, name, webViewLink, createdTime'
            ).execute()
            
            self.logger.info(
                f"Carpeta creada exitosamente en Drive: {folder.get('name')} "
                f"(ID: {folder.get('id')})"
            )
            
            return GoogleDriveFolder(folder)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al crear carpeta en Drive: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al crear carpeta: {e}")
            raise
    
    async def share_with_user(
        self,
        file_id: str,
        email: str,
        role: str = 'reader',
        credentials: Credentials = None,
    ) -> dict[str, Any]:
        """Comparte un archivo/carpeta con un usuario específico.
        
        Args:
            file_id: ID del archivo/carpeta a compartir
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
            raise ValueError(f"Rol inválido: {role}. Debe ser 'reader', 'writer' o 'commenter'")
        
        try:
            service = self._get_drive_service(credentials)
            
            # Crear permiso
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email,
            }
            
            # Aplicar permiso
            result = service.permissions().create(
                fileId=file_id,
                body=permission,
                fields='id, type, role, emailAddress',
                sendNotificationEmail=True,
            ).execute()
            
            self.logger.info(
                f"Archivo {file_id} compartido con {email} como {role}"
            )
            
            return result
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al compartir archivo: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al compartir archivo: {e}")
            raise
    
    async def get_file_metadata(
        self,
        file_id: str,
        credentials: Credentials = None,
    ) -> GoogleDriveFile:
        """Obtiene metadata de un archivo.
        
        Args:
            file_id: ID del archivo
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GoogleDriveFile: Metadata del archivo
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            service = self._get_drive_service(credentials)
            
            # Obtener metadata
            file_data = service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, webViewLink, webContentLink, createdTime, modifiedTime, size, owners, permissions'
            ).execute()
            
            return GoogleDriveFile(file_data)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al obtener metadata: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al obtener metadata: {e}")
            raise
    
    async def delete_file(
        self,
        file_id: str,
        credentials: Credentials = None,
    ) -> bool:
        """Elimina un archivo de Google Drive.
        
        Args:
            file_id: ID del archivo a eliminar
            credentials: Credenciales OAuth del usuario
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            service = self._get_drive_service(credentials)
            
            # Eliminar archivo
            service.files().delete(fileId=file_id).execute()
            
            self.logger.info(f"Archivo eliminado exitosamente: {file_id}")
            
            return True
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al eliminar archivo: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al eliminar archivo: {e}")
            raise
    
    async def list_files_in_folder(
        self,
        folder_id: str,
        credentials: Credentials = None,
        page_size: int = 100,
    ) -> list[GoogleDriveFile]:
        """Lista archivos en una carpeta específica.
        
        Args:
            folder_id: ID de la carpeta
            credentials: Credenciales OAuth del usuario
            page_size: Número máximo de archivos a retornar
            
        Returns:
            list[GoogleDriveFile]: Lista de archivos en la carpeta
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            service = self._get_drive_service(credentials)
            
            # Query para archivos en carpeta específica
            query = f"'{folder_id}' in parents and trashed=false"
            
            # Listar archivos
            results = service.files().list(
                q=query,
                pageSize=page_size,
                fields='files(id, name, mimeType, webViewLink, createdTime, modifiedTime, size)'
            ).execute()
            
            files = results.get('files', [])
            
            return [GoogleDriveFile(file_data) for file_data in files]
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al listar archivos: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al listar archivos: {e}")
            raise


# Instancia global del servicio
google_drive_service = GoogleDriveService()
