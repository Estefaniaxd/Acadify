"""
Tests de integración para los endpoints de OAuth.

Prueba el flujo completo de OAuth incluyendo:
- Inicio de login
- Callback
- Vinculación de cuentas
- Desvinculación
- Estado de vinculación
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from uuid import uuid4

from src.main import app
from src.models.users.oauth_provider import OAuthProvider
from src.models.users.usuario import Usuario


@pytest.fixture
def client():
    """Cliente de prueba para FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Usuario mock para pruebas."""
    user = MagicMock(spec=Usuario)
    user.usuario_id = uuid4()
    user.email = "test@example.com"
    user.nombre = "Test User"
    return user


class TestOAuthLoginEndpoint:
    """Tests para el endpoint de login."""

    @patch('src.api.routes.auth.oauth.settings')
    def test_login_oauth_disabled(self, mock_settings, client):
        """Verifica que falla cuando OAuth está deshabilitado."""
        mock_settings.ENABLE_OAUTH = False
        
        response = client.get("/api/v1/auth/google/login")
        
        assert response.status_code == 503
        assert "OAuth está deshabilitado" in response.json()['detail']

    @patch('src.api.routes.auth.oauth.google_oauth_service')
    @patch('src.api.routes.auth.oauth.settings')
    def test_login_success(self, mock_settings, mock_oauth_service, client):
        """Verifica el inicio exitoso del flujo OAuth."""
        mock_settings.ENABLE_OAUTH = True
        mock_oauth_service.get_authorization_url.return_value = (
            "https://accounts.google.com/o/oauth2/auth?client_id=...",
            "random_state"
        )
        
        response = client.get("/api/v1/auth/google/login", follow_redirects=False)
        
        assert response.status_code == 307  # Redirect
        assert "accounts.google.com" in response.headers['location']

    @patch('src.api.routes.auth.oauth.google_oauth_service')
    @patch('src.api.routes.auth.oauth.settings')
    def test_login_service_error(self, mock_settings, mock_oauth_service, client):
        """Verifica el manejo de errores del servicio."""
        mock_settings.ENABLE_OAUTH = True
        mock_oauth_service.get_authorization_url.side_effect = Exception("Service error")
        
        response = client.get("/api/v1/auth/google/login")
        
        assert response.status_code == 500
        assert "Error al iniciar OAuth" in response.json()['detail']


class TestOAuthCallbackEndpoint:
    """Tests para el endpoint de callback."""

    @patch('src.api.routes.auth.oauth.settings')
    def test_callback_oauth_disabled(self, mock_settings, client):
        """Verifica que falla cuando OAuth está deshabilitado."""
        mock_settings.ENABLE_OAUTH = False
        
        response = client.get("/api/v1/auth/google/callback?code=test_code")
        
        assert response.status_code == 503

    @patch('src.api.routes.auth.oauth.UsuarioCRUD')
    @patch('src.api.routes.auth.oauth.OAuthCRUD')
    @patch('src.api.routes.auth.oauth.google_oauth_service')
    @patch('src.api.routes.auth.oauth.settings')
    def test_callback_existing_oauth_user(
        self, mock_settings, mock_oauth_service, mock_oauth_crud, mock_user_crud, client
    ):
        """Verifica callback con usuario OAuth existente."""
        mock_settings.ENABLE_OAUTH = True
        
        # Mock del servicio OAuth
        mock_oauth_service.exchange_code_for_tokens.return_value = {
            'access_token': 'test_token',
            'refresh_token': 'refresh_token',
            'user_info': {
                'google_id': '123456',
                'email': 'test@example.com',
                'name': 'Test User'
            }
        }
        
        # Mock del CRUD - usuario ya existe con OAuth
        mock_oauth_provider = MagicMock(spec=OAuthProvider)
        mock_oauth_provider.provider_email = 'test@example.com'
        mock_oauth_crud.get_by_provider_and_user_id.return_value = mock_oauth_provider
        
        response = client.get("/api/v1/auth/google/callback?code=test_code")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['is_new_user'] is False
        assert data['user_email'] == 'test@example.com'

    @patch('src.api.routes.auth.oauth.UsuarioCRUD')
    @patch('src.api.routes.auth.oauth.OAuthCRUD')
    @patch('src.api.routes.auth.oauth.google_oauth_service')
    @patch('src.api.routes.auth.oauth.settings')
    def test_callback_new_user_no_account(
        self, mock_settings, mock_oauth_service, mock_oauth_crud, mock_user_crud, client
    ):
        """Verifica callback con usuario nuevo sin cuenta."""
        mock_settings.ENABLE_OAUTH = True
        
        # Mock del servicio OAuth
        mock_oauth_service.exchange_code_for_tokens.return_value = {
            'access_token': 'test_token',
            'refresh_token': 'refresh_token',
            'user_info': {
                'google_id': '123456',
                'email': 'newuser@example.com',
                'name': 'New User'
            }
        }
        
        # Mock del CRUD - usuario no existe
        mock_oauth_crud.get_by_provider_and_user_id.return_value = None
        mock_user_crud.get_by_email.return_value = None
        
        response = client.get("/api/v1/auth/google/callback?code=test_code")
        
        assert response.status_code == 404
        assert "No existe una cuenta" in response.json()['detail']


class TestOAuthLinkEndpoint:
    """Tests para el endpoint de vincular cuenta."""

    @patch('src.api.routes.auth.oauth.get_current_user')
    @patch('src.api.routes.auth.oauth.settings')
    def test_link_oauth_disabled(self, mock_settings, mock_get_user, client):
        """Verifica que falla cuando OAuth está deshabilitado."""
        mock_settings.ENABLE_OAUTH = False
        
        response = client.post("/api/v1/auth/google/link?code=test_code")
        
        assert response.status_code == 503

    @patch('src.api.routes.auth.oauth.OAuthCRUD')
    @patch('src.api.routes.auth.oauth.google_oauth_service')
    @patch('src.api.routes.auth.oauth.get_current_user')
    @patch('src.api.routes.auth.oauth.settings')
    def test_link_success(
        self, mock_settings, mock_get_user, mock_oauth_service, mock_oauth_crud, client, mock_user
    ):
        """Verifica vinculación exitosa."""
        mock_settings.ENABLE_OAUTH = True
        mock_get_user.return_value = mock_user
        
        # Mock del servicio OAuth
        mock_oauth_service.exchange_code_for_tokens.return_value = {
            'user_info': {
                'google_id': '123456',
                'email': 'test@example.com'
            }
        }
        
        # Mock del CRUD - no existe vinculación previa
        mock_oauth_crud.get_by_provider_and_user_id.return_value = None
        
        response = client.post("/api/v1/auth/google/link?code=test_code")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['provider'] == 'google'


class TestOAuthUnlinkEndpoint:
    """Tests para el endpoint de desvincular cuenta."""

    @patch('src.api.routes.auth.oauth.get_current_user')
    @patch('src.api.routes.auth.oauth.settings')
    def test_unlink_oauth_disabled(self, mock_settings, mock_get_user, client):
        """Verifica que falla cuando OAuth está deshabilitado."""
        mock_settings.ENABLE_OAUTH = False
        
        response = client.delete("/api/v1/auth/google/unlink")
        
        assert response.status_code == 503

    @patch('src.api.routes.auth.oauth.OAuthCRUD')
    @patch('src.api.routes.auth.oauth.get_current_user')
    @patch('src.api.routes.auth.oauth.settings')
    def test_unlink_success(
        self, mock_settings, mock_get_user, mock_oauth_crud, client, mock_user
    ):
        """Verifica desvinculación exitosa."""
        mock_settings.ENABLE_OAUTH = True
        mock_get_user.return_value = mock_user
        mock_oauth_crud.delete_by_usuario_and_provider.return_value = True
        
        response = client.delete("/api/v1/auth/google/unlink")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

    @patch('src.api.routes.auth.oauth.OAuthCRUD')
    @patch('src.api.routes.auth.oauth.get_current_user')
    @patch('src.api.routes.auth.oauth.settings')
    def test_unlink_not_linked(
        self, mock_settings, mock_get_user, mock_oauth_crud, client, mock_user
    ):
        """Verifica error cuando no hay vinculación."""
        mock_settings.ENABLE_OAUTH = True
        mock_get_user.return_value = mock_user
        mock_oauth_crud.delete_by_usuario_and_provider.return_value = False
        
        response = client.delete("/api/v1/auth/google/unlink")
        
        assert response.status_code == 404
        assert "No hay cuenta de Google vinculada" in response.json()['detail']


class TestOAuthStatusEndpoint:
    """Tests para el endpoint de estado."""

    @patch('src.api.routes.auth.oauth.OAuthCRUD')
    @patch('src.api.routes.auth.oauth.get_current_user')
    def test_status_linked(self, mock_get_user, mock_oauth_crud, client, mock_user):
        """Verifica estado cuando está vinculado."""
        mock_get_user.return_value = mock_user
        
        mock_oauth_provider = MagicMock(spec=OAuthProvider)
        mock_oauth_provider.provider_email = 'test@example.com'
        mock_oauth_provider.fecha_vinculacion = MagicMock()
        mock_oauth_provider.fecha_vinculacion.isoformat.return_value = '2025-11-22T20:00:00'
        mock_oauth_crud.get_by_usuario_and_provider.return_value = mock_oauth_provider
        
        response = client.get("/api/v1/auth/google/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data['is_linked'] is True
        assert data['provider'] == 'google'
        assert data['provider_email'] == 'test@example.com'

    @patch('src.api.routes.auth.oauth.OAuthCRUD')
    @patch('src.api.routes.auth.oauth.get_current_user')
    def test_status_not_linked(self, mock_get_user, mock_oauth_crud, client, mock_user):
        """Verifica estado cuando no está vinculado."""
        mock_get_user.return_value = mock_user
        mock_oauth_crud.get_by_usuario_and_provider.return_value = None
        
        response = client.get("/api/v1/auth/google/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data['is_linked'] is False
        assert data['provider'] == 'google'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
