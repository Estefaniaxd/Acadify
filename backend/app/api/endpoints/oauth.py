# backend/app/api/endpoints/oauth.py
"""
Endpoints para OAuth2.0 con Google y otros proveedores
Implementa flujo completo Authorization Code + PKCE
"""
import secrets
import hashlib
import base64
from typing import Dict, Any, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Request, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
from jose import jwt as jose_jwt  # jose es más compatible con FastAPI

from app.core.config import settings
from backend.app.database import get_database_session
from app.core.security import create_access_token, create_refresh_token
from app.crud.user import user_crud
from app.models.user import UserRole, DocumentType
from app.schemas.user import UserCreate
from app.utils.exceptions import AcadifyException
from app.utils.validators import validate_institutional_email

router = APIRouter()

# Configuración OAuth2
OAUTH_PROVIDERS = {
    "google": {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": ["openid", "email", "profile"],
        "redirect_uri": f"{settings.FRONTEND_URL}/auth/google/callback"
    },
    # Se puede agregar GitHub o Microsoft aquí de manera similar
}

class OAuth2Service:
    """Servicio para manejar OAuth2 con múltiples proveedores"""
    
    def __init__(self):
        self.session_storage: Dict[str, Dict[str, Any]] = {}  # En producción usar Redis

    def generate_pkce_pair(self) -> Dict[str, str]:
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip("=")
        code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode('utf-8').rstrip("=")
        return {"code_verifier": code_verifier, "code_challenge": code_challenge}

    def generate_state(self) -> str:
        return secrets.token_urlsafe(32)

    def store_oauth_session(self, state: str, code_verifier: str, provider: str, redirect_url: Optional[str] = None):
        self.session_storage[state] = {
            "code_verifier": code_verifier,
            "provider": provider,
            "redirect_url": redirect_url
        }

    def get_oauth_session(self, state: str) -> Optional[Dict[str, Any]]:
        return self.session_storage.get(state)

    def clear_oauth_session(self, state: str):
        self.session_storage.pop(state, None)

    async def exchange_code_for_tokens(self, provider: str, authorization_code: str, code_verifier: str) -> Dict[str, Any]:
        if provider not in OAUTH_PROVIDERS:
            raise AcadifyException("Proveedor no soportado", 400)
        
        config = OAUTH_PROVIDERS[provider]

        token_data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": config["redirect_uri"],
            "code_verifier": code_verifier
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(config["token_url"], data=token_data, headers={"Accept": "application/json"})
            if response.status_code != 200:
                raise AcadifyException("Error intercambiando código por tokens", 400)
            tokens = response.json()
            if "access_token" not in tokens:
                raise AcadifyException("No se recibió access_token", 400)
            return tokens

    async def get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        config = OAUTH_PROVIDERS[provider]
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(config["userinfo_url"], headers=headers)
            if response.status_code != 200:
                raise AcadifyException("Error obteniendo info de usuario", 400)
            return self._normalize_user_info(provider, response.json())

    def _normalize_user_info(self, provider: str, raw_info: Dict[str, Any]) -> Dict[str, Any]:
        if provider == "google":
            return {
                "email": raw_info.get("email"),
                "first_name": raw_info.get("given_name"),
                "last_name": raw_info.get("family_name"),
                "name": raw_info.get("name"),
                "picture": raw_info.get("picture"),
                "provider_id": raw_info.get("id"),
                "verified_email": raw_info.get("verified_email", False)
            }
        return raw_info

    def validate_id_token(self, provider: str, id_token: str) -> Dict[str, Any]:
        if provider != "google":
            return {}
        try:
            payload = jose_jwt.get_unverified_claims(id_token)
            if payload.get("aud") != OAUTH_PROVIDERS["google"]["client_id"]:
                raise ValueError("Audience inválida")
            return payload
        except Exception:
            return {}

oauth2_service = OAuth2Service()

@router.get("/{provider}/login")
async def oauth_login(provider: str, request: Request, redirect_url: Optional[str] = Query(None)):
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(400, "Proveedor no soportado")
    
    pkce_pair = oauth2_service.generate_pkce_pair()
    state = oauth2_service.generate_state()
    oauth2_service.store_oauth_session(state, pkce_pair["code_verifier"], provider, redirect_url)
    
    config = OAUTH_PROVIDERS[provider]
    params = {
        "client_id": config["client_id"],
        "response_type": "code",
        "scope": " ".join(config["scopes"]),
        "redirect_uri": config["redirect_uri"],
        "state": state,
        "code_challenge": pkce_pair["code_challenge"],
        "code_challenge_method": "S256",
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = f"{config['authorization_url']}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@router.get("/{provider}/callback")
async def oauth_callback(provider: str, request: Request, code: Optional[str] = Query(None), state: Optional[str] = Query(None), db: Session = Depends(get_database_session)):
    if not code or not state:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=invalid_request")

    session_data = oauth2_service.get_oauth_session(state)
    if not session_data or session_data["provider"] != provider:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=invalid_state")

    tokens = await oauth2_service.exchange_code_for_tokens(provider, code, session_data["code_verifier"])
    user_info = await oauth2_service.get_user_info(provider, tokens["access_token"])

    if "id_token" in tokens:
        payload = oauth2_service.validate_id_token(provider, tokens["id_token"])
        user_info.update(payload)

    email = user_info.get("email")
    if not validate_institutional_email(email):
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=invalid_email")

    # Buscar o crear usuario
    user = user_crud.get_by_email(db, email=email)
    if not user:
        user_data = UserCreate(
            institutional_email=email,
            first_names=user_info.get("first_name", "Usuario"),
            last_names=user_info.get("last_name", "OAuth"),
            document_type=DocumentType.CE,
            document_number=f"OAUTH_{secrets.token_hex(4)}",
            role=UserRole.STUDENT,
            password=secrets.token_urlsafe(32)
        )
        user = user_crud.create(db, obj_in=user_data)

    # Crear tokens internos
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role.value})

    oauth2_service.clear_oauth_session(state)
    redirect_url = session_data.get("redirect_url") or f"{settings.FRONTEND_URL}/dashboard"
    return RedirectResponse(url=f"{redirect_url}?access_token={access_token}&refresh_token={refresh_token}")
