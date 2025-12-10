"""
Servicio de Google Docs para Acadify.

Este módulo maneja operaciones con Google Docs:
- Creación de documentos
- Inserción de contenido inicial
- Compartir documentos con permisos
- Obtener metadata y contenido

Principios SOLID:
- Single Responsibility: Solo operaciones de Docs
- Dependency Inversion: Depende de abstracciones (Credentials)
"""

import logging
from typing import Any
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleDocument:
    """Representa un documento de Google Docs."""
    
    def __init__(self, doc_data: dict[str, Any]):
        self.id: str = doc_data.get('documentId', '')
        self.title: str = doc_data.get('title', '')
        self.revision_id: str = doc_data.get('revisionId', '')
        self.web_view_link: str = f"https://docs.google.com/document/d/{self.id}/edit"
    
    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'id': self.id,
            'title': self.title,
            'revision_id': self.revision_id,
            'web_view_link': self.web_view_link,
            'type': 'document',
        }


class GoogleDocsService:
    """Servicio para operaciones con Google Docs.
    
    Funcionalidades:
    - Crear documentos con plantillas
    - Insertar contenido inicial
    - Compartir con permisos específicos
    - Obtener contenido del documento
    
    Clean Code Principles:
    - Métodos pequeños y específicos
    - Nombres descriptivos
    - Manejo robusto de errores
    """
    
    def __init__(self):
        """Inicializa el servicio de Google Docs."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _get_docs_service(self, credentials: Credentials):
        """Crea un servicio de Docs con las credenciales proporcionadas."""
        return build('docs', 'v1', credentials=credentials)
    
    def _get_drive_service(self, credentials: Credentials):
        """Crea un servicio de Drive para operaciones de archivo."""
        return build('drive', 'v3', credentials=credentials)
    
    async def create_document(
        self,
        title: str,
        initial_content: str | None = None,
        folder_id: str | None = None,
        credentials: Credentials = None,
    ) -> GoogleDocument:
        """Crea un nuevo documento de Google Docs.
        
        Args:
            title: Título del documento
            initial_content: Contenido inicial (opcional)
            folder_id: ID de carpeta Drive donde guardar (opcional)
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GoogleDocument: Metadata del documento creado
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            docs_service = self._get_docs_service(credentials)
            
            # Crear documento vacío
            doc = docs_service.documents().create(
                body={'title': title}
            ).execute()
            
            self.logger.info(
                f"Documento creado: {doc.get('title')} (ID: {doc.get('documentId')})"
            )
            
            # Si hay contenido inicial, insertarlo
            if initial_content:
                await self.insert_content(
                    doc_id=doc.get('documentId'),
                    content=initial_content,
                    index=1,
                    credentials=credentials
                )
            
            # Si hay carpeta, mover el documento
            if folder_id:
                await self._move_to_folder(
                    file_id=doc.get('documentId'),
                    folder_id=folder_id,
                    credentials=credentials
                )
            
            return GoogleDocument(doc)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al crear documento: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al crear documento: {e}")
            raise
    
    async def insert_content(
        self,
        doc_id: str,
        content: str,
        index: int = 1,
        credentials: Credentials = None,
    ) -> None:
        """Inserta contenido en un documento.
        
        Args:
            doc_id: ID del documento
            content: Contenido a insertar
            index: Posición donde insertar (default: 1, inicio)
            credentials: Credenciales OAuth del usuario
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            docs_service = self._get_docs_service(credentials)
            
            # Request para insertar texto
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': index,
                        },
                        'text': content
                    }
                }
            ]
            
            # Ejecutar batch update
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            self.logger.info(f"Contenido insertado en documento {doc_id}")
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al insertar contenido: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al insertar contenido: {e}")
            raise
    
    async def get_document(
        self,
        doc_id: str,
        credentials: Credentials = None,
    ) -> GoogleDocument:
        """Obtiene metadata de un documento.
        
        Args:
            doc_id: ID del documento
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GoogleDocument: Metadata del documento
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            docs_service = self._get_docs_service(credentials)
            
            # Obtener documento
            doc = docs_service.documents().get(documentId=doc_id).execute()
            
            return GoogleDocument(doc)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al obtener documento: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al obtener documento: {e}")
            raise
    
    async def share_document(
        self,
        doc_id: str,
        email: str,
        role: str = 'reader',
        credentials: Credentials = None,
    ) -> dict[str, Any]:
        """Comparte un documento con un usuario.
        
        Args:
            doc_id: ID del documento
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
                fileId=doc_id,
                body=permission,
                fields='id, type, role, emailAddress',
                sendNotificationEmail=True,
            ).execute()
            
            self.logger.info(f"Documento {doc_id} compartido con {email} como {role}")
            
            return result
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al compartir documento: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al compartir documento: {e}")
            raise
    
    async def _move_to_folder(
        self,
        file_id: str,
        folder_id: str,
        credentials: Credentials,
    ) -> None:
        """Mueve un archivo a una carpeta específica (método interno).
        
        Args:
            file_id: ID del archivo
            folder_id: ID de la carpeta destino
            credentials: Credenciales OAuth del usuario
        """
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
google_docs_service = GoogleDocsService()
