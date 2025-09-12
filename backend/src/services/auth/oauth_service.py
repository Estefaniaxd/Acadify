import secrets
import httpx
from typing import Dict, Any, Optional
from authlib.integrations.httpx_client import AsyncOAuth2Client
from src.core.config import settings
from src.services.auth.redis_service import RedisService


class OAuthService:
    """Servicio para manejo de OAuth2 providers"""

    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        self.google_client_id = settings.GOOGLE_CLIENT_ID
        self.google_client_secret = settings.GOOGLE_CLIENT_SECRET
        self.google_redirect_uri = settings.GOOGLE_REDIRECT_URI

    # === GOOGLE OAUTH2 ===

    async def get_google_authorization_url(self) -> tuple[str, str]:
        """
        Generar URL de autorización de Google OAuth2

        Returns:
            tuple: (authorization_url, state)
        """
        # Generar estado único para CSRF protection
        state = secrets.token_urlsafe(32)

        # Almacenar estado en Redis
        await self.redis_service.store_oauth_state(
            state=state,
            provider="google",
            redirect_uri=self.google_redirect_uri,
            ttl_minutes=5,
        )

        client = AsyncOAuth2Client(
            client_id=self.google_client_id, redirect_uri=self.google_redirect_uri
        )

        authorization_url, _ = client.create_authorization_url(
            "https://accounts.google.com/o/oauth2/auth",
            scope="openid email profile",
            state=state,
        )

        return authorization_url, state

    async def handle_google_callback(self, code: str, state: str) -> Dict[str, Any]:
        """
        Manejar callback de Google OAuth2

        Args:
            code: Authorization code de Google
            state: Estado para validación CSRF

        Returns:
            Dict con información del usuario de Google

        Raises:
            ValueError: Si el estado es inválido o el código no se puede intercambiar
        """
        # Verificar estado CSRF
        oauth_data = await self.redis_service.verify_and_consume_oauth_state(state)
        if not oauth_data or oauth_data["provider"] != "google":
            raise ValueError("Estado OAuth inválido o expirado")

        # Intercambiar code por tokens
        client = AsyncOAuth2Client(
            client_id=self.google_client_id,
            client_secret=self.google_client_secret,
            redirect_uri=self.google_redirect_uri,
        )

        token_data = await client.fetch_token(
            "https://oauth2.googleapis.com/token", code=code
        )

        # Obtener información del usuario
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            response.raise_for_status()
            user_info = response.json()

        # Validar que el email esté verificado
        if not user_info.get("verified_email", False):
            raise ValueError("El email de Google no está verificado")

        return {
            "provider": "google",
            "provider_user_id": user_info["id"],
            "email": user_info["email"],
            "verified_email": user_info.get("verified_email", False),
            "name": user_info.get("name", ""),
            "given_name": user_info.get("given_name", ""),
            "family_name": user_info.get("family_name", ""),
            "picture": user_info.get("picture", ""),
            "locale": user_info.get("locale", ""),
        }
