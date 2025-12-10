"""
Servicio de Google Sheets para Acadify.

Este módulo maneja operaciones con Google Sheets:
- Creación de hojas de cálculo
- Definir estructura inicial (headers)
- Insertar datos
- Compartir con permisos

Principios SOLID:
- Single Responsibility: Solo operaciones de Sheets
- Dependency Inversion: Depende de abstracciones (Credentials)
"""

import logging
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleSpreadsheet:
    """Representa una hoja de cálculo de Google Sheets."""
    
    def __init__(self, sheet_data: dict[str, Any]):
        self.id: str = sheet_data.get('spreadsheetId', '')
        self.title: str = sheet_data.get('properties', {}).get('title', '')
        self.web_view_link: str = sheet_data.get('spreadsheetUrl', '')
        self.sheets: list[dict] = sheet_data.get('sheets', [])
    
    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'id': self.id,
            'title': self.title,
            'web_view_link': self.web_view_link,
            'type': 'spreadsheet',
            'sheets_count': len(self.sheets),
        }


class GoogleSheetsService:
    """Servicio para operaciones con Google Sheets.
    
    Funcionalidades:
    - Crear hojas de cálculo
    - Definir estructura inicial (headers)
    - Insertar datos
    - Compartir con permisos
    
    Clean Code Principles:
    - Métodos pequeños y específicos
    - Nombres descriptivos
    - Manejo robusto de errores
    """
    
    def __init__(self):
        """Inicializa el servicio de Google Sheets."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _get_sheets_service(self, credentials: Credentials):
        """Crea un servicio de Sheets con las credenciales proporcionadas."""
        return build('sheets', 'v4', credentials=credentials)
    
    def _get_drive_service(self, credentials: Credentials):
        """Crea un servicio de Drive para operaciones de archivo."""
        return build('drive', 'v3', credentials=credentials)
    
    async def create_spreadsheet(
        self,
        title: str,
        headers: list[str] | None = None,
        folder_id: str | None = None,
        credentials: Credentials = None,
    ) -> GoogleSpreadsheet:
        """Crea una nueva hoja de cálculo de Google Sheets.
        
        Args:
            title: Título de la hoja de cálculo
            headers: Lista de encabezados para la primera fila (opcional)
            folder_id: ID de carpeta Drive donde guardar (opcional)
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GoogleSpreadsheet: Metadata de la hoja creada
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            sheets_service = self._get_sheets_service(credentials)
            
            # Crear hoja de cálculo
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            sheet = sheets_service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId,properties,spreadsheetUrl,sheets'
            ).execute()
            
            self.logger.info(
                f"Hoja de cálculo creada: {sheet.get('properties', {}).get('title')} "
                f"(ID: {sheet.get('spreadsheetId')})"
            )
            
            # Si hay headers, insertarlos
            if headers:
                await self.insert_row(
                    sheet_id=sheet.get('spreadsheetId'),
                    values=[headers],
                    range_name='A1',
                    credentials=credentials
                )
            
            # Si hay carpeta, mover la hoja
            if folder_id:
                await self._move_to_folder(
                    file_id=sheet.get('spreadsheetId'),
                    folder_id=folder_id,
                    credentials=credentials
                )
            
            return GoogleSpreadsheet(sheet)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al crear hoja de cálculo: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al crear hoja de cálculo: {e}")
            raise
    
    async def insert_row(
        self,
        sheet_id: str,
        values: list[list[Any]],
        range_name: str = 'A1',
        credentials: Credentials = None,
    ) -> None:
        """Inserta filas en una hoja de cálculo.
        
        Args:
            sheet_id: ID de la hoja de cálculo
            values: Valores a insertar (lista de listas)
            range_name: Rango donde insertar (ej: 'A1', 'Sheet1!A1:C1')
            credentials: Credenciales OAuth del usuario
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            sheets_service = self._get_sheets_service(credentials)
            
            # Preparar datos
            body = {
                'values': values
            }
            
            # Insertar valores
            sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            self.logger.info(f"Datos insertados en hoja {sheet_id}, rango {range_name}")
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al insertar datos: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al insertar datos: {e}")
            raise
    
    async def get_spreadsheet(
        self,
        sheet_id: str,
        credentials: Credentials = None,
    ) -> GoogleSpreadsheet:
        """Obtiene metadata de una hoja de cálculo.
        
        Args:
            sheet_id: ID de la hoja de cálculo
            credentials: Credenciales OAuth del usuario
            
        Returns:
            GoogleSpreadsheet: Metadata de la hoja
            
        Raises:
            ValueError: Si las credenciales son inválidas
            HttpError: Si hay error en la API de Google
        """
        if not credentials:
            raise ValueError("Se requieren credenciales OAuth válidas")
        
        try:
            sheets_service = self._get_sheets_service(credentials)
            
            # Obtener hoja
            sheet = sheets_service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            return GoogleSpreadsheet(sheet)
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al obtener hoja: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al obtener hoja: {e}")
            raise
    
    async def share_spreadsheet(
        self,
        sheet_id: str,
        email: str,
        role: str = 'reader',
        credentials: Credentials = None,
    ) -> dict[str, Any]:
        """Comparte una hoja de cálculo con un usuario.
        
        Args:
            sheet_id: ID de la hoja de cálculo
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
                fileId=sheet_id,
                body=permission,
                fields='id, type, role, emailAddress',
                sendNotificationEmail=True,
            ).execute()
            
            self.logger.info(f"Hoja {sheet_id} compartida con {email} como {role}")
            
            return result
            
        except HttpError as e:
            self.logger.error(f"Error HTTP al compartir hoja: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al compartir hoja: {e}")
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
google_sheets_service = GoogleSheetsService()
