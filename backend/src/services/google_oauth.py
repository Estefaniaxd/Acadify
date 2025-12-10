"""
Servicio de OAuth 2.0 para Google.

Este módulo maneja la autenticación OAuth con Google, incluyendo:
- Generación de URLs de autorización
- Intercambio de códigos por tokens
- Actualización de tokens
- Validación de tokens
"""

from typing import Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

from src.core.config import settings


class GoogleOAuthService:
    """Servicio para manejar OAuth 2.0 con Google."""

    # Scopes necesarios para acceder a Google Workspace completo
    SCOPES = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/drive.file',  # Acceso a archivos creados por la app
        'https://www.googleapis.com/auth/drive.readonly',  # Lectura de Drive
        'https://www.googleapis.com/auth/documents',  # Google Docs
        'https://www.googleapis.com/auth/spreadsheets',  # Google Sheets
        'https://www.googleapis.com/auth/presentations',  # Google Slides
        'https://www.googleapis.com/auth/forms',  # Google Forms
        'openid'
    ]

    def __init__(self):
        """Inicializa el servicio de Google OAuth."""
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError(
                "GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET deben estar configurados"
            )
        
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET

    @property
    def redirect_uri(self) -> str:
        """Obtiene la URI de redirección desde la configuración actual."""
        return settings.GOOGLE_REDIRECT_URI or "http://localhost:8000/api/v1/auth/google/callback"

    def _create_flow(self) -> Flow:
        """
        Crea un objeto Flow para el flujo OAuth.
        
        Returns:
            Flow: Objeto Flow configurado para OAuth
        """
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri],
            }
        }
        
        flow = Flow.from_client_config(
            client_config=client_config,
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        return flow

    def get_authorization_url(self, state: str | None = None) -> tuple[str, str]:
        """
        Genera la URL de autorización de Google.
        
        Args:
            state: Estado opcional para prevenir CSRF
            
        Returns:
            tuple: (authorization_url, state)
        """
        flow = self._create_flow()
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',  # Para obtener refresh token
            include_granted_scopes='true',
            prompt='consent'  # Forzar pantalla de consentimiento
        )
        
        return authorization_url, state

    def exchange_code_for_tokens(self, code: str) -> dict[str, Any]:
        """
        Intercambia el código de autorización por tokens de acceso.
        
        Args:
            code: Código de autorización de Google
            
        Returns:
            dict: Información de tokens y usuario
            
        Raises:
            Exception: Si hay error en el intercambio
        """
        flow = self._create_flow()
        
        # Intercambiar código por tokens
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Obtener información del usuario
        user_info = self._get_user_info(credentials)
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
            'user_info': user_info
        }

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """
        Refresca el token de acceso usando el refresh token.
        
        Args:
            refresh_token: Token de actualización
            
        Returns:
            dict: Nuevos tokens
            
        Raises:
            Exception: Si hay error al refrescar
        """
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        # Refrescar el token
        request = Request()
        credentials.refresh(request)
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token or refresh_token,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }

    def _get_user_info(self, credentials: Credentials) -> dict[str, Any]:
        """
        Obtiene información del usuario desde Google.
        
        Args:
            credentials: Credenciales de OAuth
            
        Returns:
            dict: Información del usuario
        """
        try:
            # Usar la API de OAuth2 para obtener info del usuario
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            
            return {
                'google_id': user_info.get('id'),
                'email': user_info.get('email'),
                'verified_email': user_info.get('verified_email'),
                'name': user_info.get('name'),
                'given_name': user_info.get('given_name'),
                'family_name': user_info.get('family_name'),
                'picture': user_info.get('picture'),
                'locale': user_info.get('locale')
            }
        except Exception as e:
            raise Exception(f"Error obteniendo información del usuario: {str(e)}")

    def validate_token(self, access_token: str) -> bool:
        """
        Valida si un token de acceso es válido.
        
        Args:
            access_token: Token de acceso a validar
            
        Returns:
            bool: True si el token es válido
        """
        try:
            credentials = Credentials(token=access_token)
            service = build('oauth2', 'v2', credentials=credentials)
            service.userinfo().get().execute()
            return True
        except Exception:
            return False

    def get_drive_service(self, access_token: str, refresh_token: str | None = None):
        """
        Crea un servicio de Google Drive con las credenciales proporcionadas.
        
        Args:
            access_token: Token de acceso
            refresh_token: Token de actualización (opcional)
            
        Returns:
            Resource: Servicio de Google Drive
        """
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        return build('drive', 'v3', credentials=credentials)


# Instancia global del servicio
google_oauth_service = GoogleOAuthService()
