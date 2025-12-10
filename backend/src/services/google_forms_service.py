"""
Servicio de Google Forms para Acadify.

Este módulo maneja operaciones con Google Forms:
- Creación de formularios
- Agregar preguntas
- Compartir con permisos
- Obtener respuestas

Principios SOLID:
- Single Responsibility: Solo operaciones de Forms
- Dependency Inversion: Depende de abstracciones (Credentials)
"""

import logging
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleForm:
    """Representa un formulario de Google Forms."""
    
    def __init__(self, form_data: dict[str, Any]):
        self.id: str = form_data.get('formId', '')
        self.title: str = form_data.get('info', {}).get('title', '')
        self.web_view_link: str = form_data.get('responderUri', '')
        self.edit_link: str = f"https://docs.google.com/forms/d/{self.id}/edit"
    
    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'id': self.id,
            'title': self.title,
            'web_view_link': self.web_view_link,
            'edit_link': self.edit_link,
            'type': 'form',
        }


class GoogleFormsService:
    """Servicio para operaciones con Google Forms.
    
    Funcionalidades:
    - Crear formularios
    - Agregar preguntas
    - Compartir con permisos
    - Obtener respuestas
    
    Clean Code Principles:
    - Métodos pequeños y específicos
    - Nombres descriptivos
    - Manejo robusto de errores
    """
    
    def __init__(self):
        """Inicializa el servicio de Google Forms."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _get_forms_service(self, credentials: Credentials):
        """Crea un servicio de Forms con las credenciales proporcionadas."""
        return build('forms', 'v1', credentials=credentials)
    
    def _get_drive_service(self, credentials: Credentials):
        """Crea un servicio de Drive para operaciones de archivo."""
        return build('drive', 'v3', credentials=credentials)
    
    async def create_form(
        self,
        title: str,
        description: str | None = None,
        folder_id: str | None = None,
        credentials: Credentials = None,
    ) -> GoogleForm:
        """Crea un nuevo formulario de Google Forms.
        
        Args:
            title: Título del formulario
            description: Descripción del formulario (opcional)
            folder_id: ID de carpeta Drive donde guardar (opcional)
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GoogleForm: Metadata del formulario creado
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            forms_service = self._get_forms_service(credentials)
            
            # Crear formulario
            form = {
                'info': {
                    'title': title,
                }
            }
            
            if description:
                form['info']['documentTitle'] = description
            
            created_form = forms_service.forms().create(body=form).execute()
            
            self.logger.info(
                f"Formulario creado: {created_form.get('info', {}).get('title')} "
                f"(ID: {created_form.get('formId')})"
            )
            
            # Si hay carpeta, mover el formulario
            if folder_id:
                await self._move_to_folder(
                    file_id=created_form.get('formId'),
                    folder_id=folder_id,
                    credentials=credentials
                )
            
            return GoogleForm(created_form)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al crear formulario: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al crear formulario: {e}")
            raise
    
    async def get_form(
        self,
        form_id: str,
        credentials: Credentials = None,
    ) -> GoogleForm:
        """Obtiene metadata de un formulario.
        
        Args:
            form_id: ID del formulario
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GoogleForm: Metadata del formulario
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            forms_service = self._get_forms_service(credentials)
            
            # Obtener formulario
            form = forms_service.forms().get(formId=form_id).execute()
            
            return GoogleForm(form)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al obtener formulario: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al obtener formulario: {e}")
            raise
    
    async def get_responses(
        self,
        form_id: str,
        credentials: Credentials = None,
    ) -> list[dict[str, Any]]:
        """Obtiene respuestas de un formulario.
        
        Args:
            form_id: ID del formulario
            credentials: Credenciales OAuth del usuario
            
        Returns:
            list[dict]: Lista de respuestas
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            forms_service = self._get_forms_service(credentials)
            
            # Obtener respuestas
            result = forms_service.forms().responses().list(formId=form_id).execute()
            
            responses = result.get('responses', [])
            
            self.logger.info(
                f"Obtenidas {len(responses)} respuestas del formulario {form_id}"
            )
            
            return responses
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al obtener respuestas: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al obtener respuestas: {e}")
            raise
    
    async def share_form(
        self,
        form_id: str,
        email: str,
        role: str = 'reader',
        credentials: Credentials = None,
    ) -> dict[str, Any]:
        """Comparte un formulario con un usuario.
        
        Args:
            form_id: ID del formulario
            email: Email del usuario con quien compartir
            role: Rol del usuario ('reader', 'writer')
            credentials: Credenciales OAuth del usuario
            
        Returns:
            dict: Información del permiso creado
            
        Raises:
            ValueError: Si las credenciales o parámetros son inválidos
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        if role not in ['reader', 'writer']:
            raise ValueError(f"Rol inválido: {role}. Forms solo soporta 'reader' o 'writer'")
        
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
                fileId=form_id,
                body=permission,
                fields='id, type, role, emailAddress',
                sendNotificationEmail=True,
            ).execute()
            
            self.logger.info(
                f"Formulario {form_id} compartido con {email} como {role}"
            )
            
            return result
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al compartir formulario: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al compartir formulario: {e}")
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
google_forms_service = GoogleFormsService()
