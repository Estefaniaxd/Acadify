from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid
import httpx

# Importaciones de tu proyecto
from src.services.auth import email_service, oauth_service
from src.schemas.auth import auth_schemas
from src.schemas.users import usuario as usuario_schemas
from src.crud.auth import UserCRUD
from src.services.auth.password_service import PasswordService
from src.services.auth.redis_service import RedisService
from src.services.auth.token_service import TokenService
from src.core.config import settings
from src.utils.security import verify_password
from src.db.session import get_db


# Instancias globales de servicios
password_service = PasswordService()
redis_service = RedisService()
token_service = TokenService(redis_service)
crud_usuario = UserCRUD(password_service)

router = APIRouter()

# Endpoint temporal para depuración de tokens
import logging
logger = logging.getLogger("auth-debug")
logging.basicConfig(level=logging.INFO)


@router.post("/debug/token")
async def debug_token(token: str):
    """Endpoint temporal para depurar el contenido de un token JWT"""
    try:
        payload = await token_service.decode_token(token)
        logger.info(f"Payload decodificado: {payload}")
        return {"payload": payload}
    except Exception as e:
        logger.error(f"Error al decodificar token: {e}")
        return {"error": str(e)}


@router.post("/login", response_model=auth_schemas.TokenResponse,
             summary="Iniciar sesión con credenciales",
             description="Autentica a un usuario y retorna los tokens de acceso y refresco.")
async def login(
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):

    # Primero intenta buscar por username (para administradores)
    usuario = crud_usuario.get_by_username(db, form_data.username)
    if not usuario:
        # Si no existe username, intenta buscar por correo institucional
        usuario = crud_usuario.get_by_email(db, email=form_data.username)

    if not usuario or not password_service.verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=60)
    refresh_token_expires = timedelta(days=7)

    access_token, _ = token_service.create_access_token(
        user_id=str(usuario.usuario_id),
        roles=[usuario.rol],
        expires_delta=access_token_expires
    )
    refresh_token, _ = token_service.create_refresh_token(
        user_id=str(usuario.usuario_id),
        expires_delta=refresh_token_expires
    )

    response.set_cookie(key="refresh_token", value=refresh_token,
                        httponly=True, samesite="Lax")

    return auth_schemas.TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        expires_in=int(access_token_expires.total_seconds())
    )


@router.post("/register", response_model=usuario_schemas.UsuarioRead,
             summary="Registrar un nuevo usuario",
             description="Crea un nuevo usuario en el sistema.")
def register_user(usuario_in: usuario_schemas.UsuarioCreate,
                  db: Session = Depends(get_db)):
    usuario_existente = crud_usuario.get_by_email(db, email=usuario_in.correo_institucional)
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado."
        )
    try:
        return crud_usuario.create_user(db=db, user_create=usuario_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/refresh", response_model=auth_schemas.TokenResponse,
             summary="Refrescar token de acceso",
             description="Utiliza el token de refresco para obtener un nuevo token de acceso.")
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco no proporcionado",
        )
    try:
        user_id = await token_service.decode_refresh_token(refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token de refresco inválido o expirado: {str(e)}"
        )

    usuario = crud_usuario.get_by_id(db, user_id=uuid.UUID(user_id))
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    access_token_expires = timedelta(minutes=60)
    new_access_token, _ = token_service.create_access_token(
        user_id=str(usuario.usuario_id),
        roles=[str(usuario.rol)],
        expires_delta=timedelta(minutes=60)
    )

    new_refresh_token, _ = token_service.create_refresh_token(
        user_id=str(usuario.usuario_id),
        expires_delta=timedelta(days=7)
    )
    response.set_cookie(key="refresh_token", value=new_refresh_token,
                        httponly=True, samesite="Lax")

    return auth_schemas.TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        refresh_token=new_refresh_token
    )


@router.get("/google/login",
            summary="Iniciar sesión con Google",
            description="Redirige al usuario a la página de autorización de Google.")
async def google_login():
    authorization_url = await oauth_service.get_google_authorization_url()
    return {"url": authorization_url}


@router.get("/google/callback", response_model=auth_schemas.TokenResponse,
            summary="Callback de Google OAuth",
            description="Maneja la respuesta de Google y autentica al usuario.")
async def google_callback(
    request: Request,
    response: Response,
    code: str,
    db: Session = Depends(get_db)
):
    try:
        tokens = await oauth_service.exchange_code_for_tokens(code)
        user_info = await oauth_service.get_user_info_from_google(tokens.get("access_token"))
        email = user_info.get("email")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correo electrónico no encontrado en la respuesta de Google."
            )

        usuario = crud_usuario.get_by_email(db, email=email)
        if not usuario:
            from src.schemas.auth.user_auth_schemas import UserRegisterRequest
            new_user_data = UserRegisterRequest(
                correo_institucional=email,
                nombres=user_info.get("name"),
                apellidos="",
                password="DUMMY_PASSWORD_OAUTH",
                username=None,
                tipo_documento=None,
                numero_documento=None,
                rol="estudiante",
                telefono=None,
                descripcion=None
            )
            usuario = crud_usuario.create_user(db, user_create=new_user_data)

        access_token = token_service.create_access_token(
            data={"sub": str(usuario.usuario_id), "scopes": ["read_users"]}
        )
        refresh_token = token_service.create_refresh_token(
            data={"sub": str(usuario.usuario_id)}
        )

        response.set_cookie(key="refresh_token", value=refresh_token,
                            httponly=True, samesite="Lax")

        return auth_schemas.TokenResponse(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la autenticación de Google: {str(e)}"
        )


@router.post("/forgot-password", status_code=status.HTTP_200_OK,
             summary="Solicitar restablecimiento de contraseña",
             description="Envía un enlace de restablecimiento de contraseña al correo del usuario.")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    usuario = crud_usuario.get_by_email(db, email=email)
    if not usuario:
        return {"detail": "Si el correo existe, se ha enviado un enlace para restablecer la contraseña."}

    reset_token = token_service.create_password_reset_token(data={"sub": str(usuario.usuario_id)})
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

    email_service.send_password_reset_email(
        email_to=usuario.email,
        username=usuario.nombre,
        reset_link=reset_link
    )

    return {"detail": "Si el correo existe, se ha enviado un enlace para restablecer la contraseña."}


@router.post("/reset-password", status_code=status.HTTP_200_OK,
             summary="Restablecer la contraseña",
             description="Valida el token y actualiza la contraseña del usuario.")
async def reset_password(reset_data: auth_schemas.PasswordResetRequest,
                         db: Session = Depends(get_db)):
    user_id = token_service.decode_password_reset_token(reset_data.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado."
        )

    usuario = crud_usuario.get_by_id(db, user_id=uuid.UUID(user_id))
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    try:
        crud_usuario.update_password(db, user_id=str(usuario.usuario_id), new_password=reset_data.new_password, verify_current=False)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"detail": "Contraseña actualizada con éxito."}