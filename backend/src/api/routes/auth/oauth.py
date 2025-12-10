"""
Rutas de API para OAuth 2.0 con Google.

Endpoints para manejar el flujo de autenticación OAuth:
- Iniciar login con Google
- Callback de Google
- Vincular/desvincular cuenta de Google
- Verificar estado de vinculación
"""

import logging
from datetime import datetime, UTC
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.session import get_db
from src.services.google_oauth import google_oauth_service
from src.services.auth.redis_service import RedisService
from src.crud.auth.oauth_crud import OAuthCRUD
from src.crud.user.usuario import UsuarioCRUD
from src.api.deps import get_current_user
from src.models.users.usuario import Usuario
from src.services.auth.token_service import TokenService
from src.enums.users.usuario_enums import RolUsuario, EstadoCuentaUsuario
from pydantic import BaseModel, EmailStr


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/google", tags=["OAuth - Google"])


# ==================== Schemas ====================

class OAuthStatusResponse(BaseModel):
    """Respuesta del estado de OAuth."""
    is_linked: bool
    provider: str
    provider_email: str | None = None
    linked_at: str | None = None
    expires_at: str | None = None
    has_credentials: bool = False
    needs_relink: bool = False


class OAuthLinkResponse(BaseModel):
    """Respuesta al vincular OAuth."""
    success: bool
    message: str
    provider: str
    provider_email: str


class OAuthCallbackResponse(BaseModel):
    """Respuesta del callback de OAuth."""
    success: bool
    message: str
    user_email: str
    is_new_user: bool = False
    access_token: str
    token_type: str = "bearer"

def _parse_expiry(value: str | datetime | None) -> datetime | None:
    """Convierte el valor de expiración a datetime con zona horaria."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


# ==================== Endpoints ====================

@router.get("/login", summary="Iniciar login con Google")
async def google_login(
    redirect_url: str | None = Query(None, description="URL de redirección después del login")
):
    """
    Inicia el flujo de OAuth con Google.
    
    Genera una URL de autorización y redirige al usuario a Google
    para que autorice la aplicación.
    
    Args:
        redirect_url: URL opcional para redirigir después del login exitoso
        
    Returns:
        RedirectResponse: Redirección a la página de autorización de Google
    """
    if not settings.ENABLE_OAUTH:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth está deshabilitado en la configuración"
        )
    
    try:
        # Generar URL de autorización
        # El state puede incluir la redirect_url si es necesario
        authorization_url, state = google_oauth_service.get_authorization_url()
        
        # TODO: Guardar el state en Redis/sesión para validación CSRF
        
        return RedirectResponse(url=authorization_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar OAuth: {str(e)}"
        )


@router.get("/callback", summary="Callback de Google OAuth")
async def google_callback(
    code: str = Query(..., description="Código de autorización de Google"),
    state: str | None = Query(None, description="Estado para validación CSRF"),
    db: Session = Depends(get_db)
):
    """
    Maneja el callback de Google después de la autorización.
    
    Intercambia el código de autorización por tokens de acceso,
    obtiene la información del usuario de Google, y crea o vincula
    la cuenta en Acadify.
    
    Args:
        code: Código de autorización de Google
        state: Estado para validación CSRF
        db: Sesión de base de datos
        
    Returns:
        OAuthCallbackResponse: Información del resultado del callback
    """
    if not settings.ENABLE_OAUTH:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth está deshabilitado"
        )
    
    try:
        # TODO: Validar state contra el guardado en Redis/sesión
        
        # Intercambiar código por tokens
        token_data = google_oauth_service.exchange_code_for_tokens(code)
        user_info = token_data['user_info']
        
        # Buscar si ya existe un usuario con este proveedor OAuth
        oauth_provider = OAuthCRUD.get_by_provider_and_user_id(
            db=db,
            provider='google',
            provider_user_id=user_info['google_id']
        )
        
        if oauth_provider:
            # Usuario ya existe y tiene vinculado Google - generar JWT
            usuario = UsuarioCRUD.get(db, id=oauth_provider.usuario_id)
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Generar token de acceso
            redis_service = RedisService()
            token_service = TokenService(redis_service)
            access_token, _ = token_service.create_access_token(
                user_id=str(usuario.usuario_id),
                roles=[usuario.rol.value],
                email=usuario.correo_institucional,
                username=f"{usuario.nombres} {usuario.apellidos}"
            )
            
            # Actualizar último acceso
            UsuarioCRUD.update_last_access(db, user_id=usuario.usuario_id)
            
            # Redirigir al frontend con el token
            frontend_url = "http://localhost:5173"
            redirect_url = f"{frontend_url}/auth/google/callback?token={access_token}&email={oauth_provider.provider_email}&new_user=false"
            return RedirectResponse(url=redirect_url)
        
        # Buscar si existe un usuario con el mismo email
        usuario = UsuarioCRUD.get_by_email(db, email=user_info['email'])
        
        if usuario:
            # Usuario existe pero no tiene vinculado Google - vincular automáticamente
            logger.info(f"VINCULANDO USUARIO EXISTENTE: {usuario.usuario_id}")
            logger.info(f"Token Data Keys: {token_data.keys()}")
            logger.info(f"Access Token: {token_data.get('access_token')[:10] if token_data.get('access_token') else 'None'}...")
            logger.info(f"Refresh Token: {token_data.get('refresh_token')[:10] if token_data.get('refresh_token') else 'None'}...")
            
            OAuthCRUD.create_or_update(
                db=db,
                usuario_id=usuario.usuario_id,
                provider='google',
                provider_user_id=user_info['google_id'],
                provider_email=user_info['email'],
                access_token=token_data.get('access_token'),
                refresh_token=token_data.get('refresh_token'),
                token_expiry=_parse_expiry(token_data.get('expiry'))  # Fixed key from expires_at to expiry
            )
            
            # Generar token de acceso
            redis_service = RedisService()
            token_service = TokenService(redis_service)
            access_token, _ = token_service.create_access_token(
                user_id=str(usuario.usuario_id),
                roles=[usuario.rol.value],
                email=usuario.correo_institucional,
                username=f"{usuario.nombres} {usuario.apellidos}"
            )
            
            # Actualizar último acceso
            UsuarioCRUD.update_last_access(db, user_id=usuario.usuario_id)
            
            # Redirigir al frontend con el token
            frontend_url = "http://localhost:5173"
            redirect_url = f"{frontend_url}/auth/google/callback?token={access_token}&email={usuario.correo_institucional}&new_user=false"
            return RedirectResponse(url=redirect_url)
        
        # Usuario no existe - crear nuevo usuario automáticamente
        try:
            # Crear usuario con datos de Google
            nuevo_usuario = UsuarioCRUD.create(db, obj_in={
                "correo_institucional": user_info['email'],
                "nombres": user_info.get('given_name', user_info['name'].split()[0] if user_info.get('name') else 'Usuario'),
                "apellidos": user_info.get('family_name', user_info['name'].split()[-1] if user_info.get('name') and len(user_info['name'].split()) > 1 else 'Google'),
                "rol": RolUsuario.estudiante,  # Por defecto estudiante
                "estado_cuenta": EstadoCuentaUsuario.activo,
                "email_verified": True,  # Email ya verificado por Google
                "password_hash": "",  # No necesita contraseña, usa OAuth
                "tipo_documento": "cc",  # Valor por defecto
                "numero_documento": f"GOOGLE_{user_info['google_id'][:10]}",  # Documento temporal
            })
            
            # Vincular cuenta de Google
            logger.info(f"VINCULANDO NUEVO USUARIO: {nuevo_usuario.usuario_id}")
            logger.info(f"Token Data Keys: {token_data.keys()}")
            logger.info(f"Access Token: {token_data.get('access_token')[:10] if token_data.get('access_token') else 'None'}...")
            logger.info(f"Refresh Token: {token_data.get('refresh_token')[:10] if token_data.get('refresh_token') else 'None'}...")

            OAuthCRUD.create_or_update(
                db=db,
                usuario_id=nuevo_usuario.usuario_id,
                provider='google',
                provider_user_id=user_info['google_id'],
                provider_email=user_info['email'],
                access_token=token_data.get('access_token'),
                refresh_token=token_data.get('refresh_token'),
                token_expiry=_parse_expiry(token_data.get('expiry'))  # Fixed key
            )
            
            # Generar token de acceso
            redis_service = RedisService()
            token_service = TokenService(redis_service)
            access_token, _ = token_service.create_access_token(
                user_id=str(nuevo_usuario.usuario_id),
                roles=[nuevo_usuario.rol.value],
                email=nuevo_usuario.correo_institucional,
                username=f"{nuevo_usuario.nombres} {nuevo_usuario.apellidos}"
            )
            
            # Redirigir al frontend con el token
            frontend_url = "http://localhost:5173"
            redirect_url = f"{frontend_url}/auth/google/callback?token={access_token}&email={nuevo_usuario.correo_institucional}&new_user=true"
            return RedirectResponse(url=redirect_url)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear usuario: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el callback de OAuth: {str(e)}"
        )


@router.post("/link", response_model=OAuthLinkResponse, summary="Vincular cuenta de Google")
async def link_google_account(
    code: str = Query(..., description="Código de autorización de Google"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vincula una cuenta de Google a un usuario existente de Acadify.
    
    El usuario debe estar autenticado en Acadify para usar este endpoint.
    
    Args:
        code: Código de autorización de Google
        current_user: Usuario actual autenticado
        db: Sesión de base de datos
        
    Returns:
        OAuthLinkResponse: Información del resultado de la vinculación
    """
    if not settings.ENABLE_OAUTH:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth está deshabilitado"
        )
    
    try:
        # Intercambiar código por tokens
        token_data = google_oauth_service.exchange_code_for_tokens(code)
        user_info = token_data['user_info']
        
        # Verificar si ya está vinculado a otro usuario
        existing = OAuthCRUD.get_by_provider_and_user_id(
            db=db,
            provider='google',
            provider_user_id=user_info['google_id']
        )
        
        if existing and existing.usuario_id != current_user.usuario_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta cuenta de Google ya está vinculada a otro usuario"
            )
        
        # Crear o actualizar vinculación
        OAuthCRUD.create_or_update(
            db=db,
            usuario_id=current_user.usuario_id,
            provider='google',
            provider_user_id=user_info['google_id'],
            provider_email=user_info['email'],
            access_token=token_data.get('access_token'),
            refresh_token=token_data.get('refresh_token'),
            token_expiry=_parse_expiry(token_data.get('expiry'))
        )
        
        return OAuthLinkResponse(
            success=True,
            message="Cuenta de Google vinculada exitosamente",
            provider="google",
            provider_email=user_info['email']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al vincular cuenta de Google: {str(e)}"
        )


@router.delete("/unlink", summary="Desvincular cuenta de Google")
async def unlink_google_account(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Desvincula la cuenta de Google del usuario actual.
    
    Args:
        current_user: Usuario actual autenticado
        db: Sesión de base de datos
        
    Returns:
        dict: Mensaje de confirmación
    """
    if not settings.ENABLE_OAUTH:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth está deshabilitado"
        )
    
    try:
        # Eliminar vinculación
        deleted = OAuthCRUD.delete_by_usuario_and_provider(
            db=db,
            usuario_id=current_user.usuario_id,
            provider='google'
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay cuenta de Google vinculada"
            )
        
        return {
            "success": True,
            "message": "Cuenta de Google desvinculada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desvincular cuenta de Google: {str(e)}"
        )


@router.get("/status", response_model=OAuthStatusResponse, summary="Estado de vinculación")
async def get_oauth_status(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado de vinculación de Google del usuario actual.
    
    Args:
        current_user: Usuario actual autenticado
        db: Sesión de base de datos
        
    Returns:
        OAuthStatusResponse: Estado de la vinculación
    """
    try:
        oauth_provider = OAuthCRUD.get_by_usuario_and_provider(
            db=db,
            usuario_id=current_user.usuario_id,
            provider='google'
        )
        
        if oauth_provider:
            has_credentials = bool(oauth_provider.access_token and oauth_provider.refresh_token)
            needs_relink = oauth_provider.refresh_token is None
            expires_at = oauth_provider.token_expiry.isoformat() if oauth_provider.token_expiry else None
            return OAuthStatusResponse(
                is_linked=True,
                provider='google',
                provider_email=oauth_provider.provider_email,
                linked_at=oauth_provider.fecha_vinculacion.isoformat(),
                expires_at=expires_at,
                has_credentials=has_credentials,
                needs_relink=needs_relink
            )
        
        return OAuthStatusResponse(
            is_linked=False,
            provider='google'
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estado de OAuth: {str(e)}"
        )
