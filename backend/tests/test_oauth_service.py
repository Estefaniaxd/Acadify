"""
Tests para el servicio de Google OAuth.

Prueba las funcionalidades principales del servicio OAuth:
- Generación de URLs de autorización
- Validación de configuración
- Manejo de errores
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.services.google_oauth import GoogleOAuthService, google_oauth_service
from src.core.config import settings


class TestGoogleOAuthService:
    """Tests para GoogleOAuthService."""

    def test_service_initialization(self):
        """Verifica que el servicio se inicializa correctamente."""
        service = GoogleOAuthService()
        
        assert service.client_id == settings.GOOGLE_CLIENT_ID
        assert service.client_secret == settings.GOOGLE_CLIENT_SECRET
        assert service.redirect_uri is not None

    def test_service_initialization_without_credentials(self):
        """Verifica que falla sin credenciales."""
        with patch('src.services.google_oauth.settings') as mock_settings:
            mock_settings.GOOGLE_CLIENT_ID = None
            mock_settings.GOOGLE_CLIENT_SECRET = None
            
            with pytest.raises(ValueError) as exc_info:
                GoogleOAuthService()
            
            assert "GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET" in str(exc_info.value)

    def test_get_authorization_url(self):
        """Verifica la generación de URL de autorización."""
        service = GoogleOAuthService()
        
        auth_url, state = service.get_authorization_url()
        
        # Verificar que la URL contiene elementos esperados
        assert "accounts.google.com" in auth_url
        assert "oauth2" in auth_url
        assert state is not None
        assert len(state) > 0

    def test_scopes_configuration(self):
        """Verifica que los scopes están correctamente configurados."""
        expected_scopes = [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.readonly',
            'openid'
        ]
        
        assert GoogleOAuthService.SCOPES == expected_scopes

    @patch('src.services.google_oauth.Flow')
    def test_create_flow(self, mock_flow_class):
        """Verifica la creación del objeto Flow."""
        service = GoogleOAuthService()
        mock_flow = MagicMock()
        mock_flow_class.from_client_config.return_value = mock_flow
        
        flow = service._create_flow()
        
        # Verificar que se llamó con los parámetros correctos
        mock_flow_class.from_client_config.assert_called_once()
        call_args = mock_flow_class.from_client_config.call_args
        
        assert 'client_config' in call_args.kwargs
        assert 'scopes' in call_args.kwargs
        assert 'redirect_uri' in call_args.kwargs

    @patch('src.services.google_oauth.build')
    @patch('src.services.google_oauth.Credentials')
    def test_validate_token_valid(self, mock_credentials, mock_build):
        """Verifica la validación de un token válido."""
        service = GoogleOAuthService()
        
        # Mock del servicio de Google
        mock_service = MagicMock()
        mock_userinfo = MagicMock()
        mock_userinfo.get.return_value.execute.return_value = {'email': 'test@example.com'}
        mock_service.userinfo.return_value = mock_userinfo
        mock_build.return_value = mock_service
        
        result = service.validate_token('valid_token')
        
        assert result is True

    @patch('src.services.google_oauth.build')
    @patch('src.services.google_oauth.Credentials')
    def test_validate_token_invalid(self, mock_credentials, mock_build):
        """Verifica la validación de un token inválido."""
        service = GoogleOAuthService()
        
        # Mock que lanza excepción
        mock_build.side_effect = Exception("Invalid token")
        
        result = service.validate_token('invalid_token')
        
        assert result is False

    @patch('src.services.google_oauth.build')
    def test_get_drive_service(self, mock_build):
        """Verifica la creación del servicio de Drive."""
        service = GoogleOAuthService()
        
        mock_drive_service = MagicMock()
        mock_build.return_value = mock_drive_service
        
        drive_service = service.get_drive_service(
            access_token='test_token',
            refresh_token='refresh_token'
        )
        
        # Verificar que se llamó build con los parámetros correctos
        mock_build.assert_called_once()
        call_args = mock_build.call_args
        assert call_args.args[0] == 'drive'
        assert call_args.args[1] == 'v3'


class TestGoogleOAuthServiceIntegration:
    """Tests de integración para GoogleOAuthService."""

    def test_global_service_instance(self):
        """Verifica que la instancia global está disponible."""
        assert google_oauth_service is not None
        assert isinstance(google_oauth_service, GoogleOAuthService)

    def test_authorization_url_format(self):
        """Verifica el formato de la URL de autorización."""
        auth_url, state = google_oauth_service.get_authorization_url()
        
        # Verificar componentes de la URL
        assert auth_url.startswith('https://')
        assert 'client_id=' in auth_url
        assert 'redirect_uri=' in auth_url
        assert 'scope=' in auth_url
        assert 'response_type=code' in auth_url
        assert 'access_type=offline' in auth_url


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
