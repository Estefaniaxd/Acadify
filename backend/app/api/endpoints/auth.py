from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.user import User
from app.api.deps import get_db
from app.core.security import token_manager, get_current_active_user
from app.core.config import settings
from app.core.logging import log_user_action, log_security_event
from app.crud.user import user_crud
from app.schemas.auth import LoginRequest, LoginResponse, Token, RefreshTokenRequest
from app.schemas.user import UserCreate, UserResponse, PasswordChangeRequest

router = APIRouter()

# -------------------
# Funciones auxiliares
# -------------------
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    return token_manager.create_access_token(data, expires_delta)

def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    expires = expires_delta if expires_delta else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return token_manager.create_access_token(data, expires)

# -------------------
# Endpoints
# -------------------
@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> Any:
    user = user_crud.authenticate(db, email=login_data.email, password=login_data.password)
    if not user:
        log_security_event("LOGIN_FAILED", {"email": login_data.email})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o contraseña incorrectos")
    if not user_crud.is_active(user):
        log_security_event("LOGIN_INACTIVE_USER", {"user_id": str(user.id)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cuenta de usuario inactiva")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": str(user.id)}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token({"sub": str(user.id)})

    user_crud.update_last_access(db, user=user)
    log_user_action(str(user.id), "LOGIN_SUCCESS")

    return LoginResponse(
        user=UserResponse.from_orm(user),
        token=Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
    )

@router.post("/login/oauth", response_model=LoginResponse)
async def oauth_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Any:
    user = user_crud.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        log_security_event("OAUTH_LOGIN_FAILED", {"username": form_data.username})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not user_crud.is_active(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cuenta de usuario inactiva")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": str(user.id)}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token({"sub": str(user.id)})

    user_crud.update_last_access(db, user=user)
    log_user_action(str(user.id), "OAUTH_LOGIN_SUCCESS")

    return LoginResponse(
        user=UserResponse.from_orm(user),
        token=Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
    )

@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)) -> Any:
    try:
        payload = token_manager.decode_token(refresh_data.refresh_token)
    except HTTPException:
        log_security_event("INVALID_REFRESH_TOKEN", {"token": refresh_data.refresh_token[:20]})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de refresco inválido")

    user_id = payload.get("sub")
    user = user_crud.get(db, id=user_id)
    if not user or not user_crud.is_active(user):
        log_security_event("REFRESH_TOKEN_INACTIVE_USER", {"user_id": user_id})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado o inactivo")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token({"sub": str(user.id)}, expires_delta=access_token_expires)
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    log_user_action(str(user.id), "TOKEN_REFRESHED")
    return Token(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
    if user_crud.get_by_email(db, email=user_data.institutional_email):
        log_security_event("REGISTRATION_DUPLICATE_EMAIL", {"email": user_data.institutional_email})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email institucional ya está registrado")
    if user_crud.get_by_document(db, document_number=user_data.document_number):
        log_security_event("REGISTRATION_DUPLICATE_DOCUMENT", {"document": user_data.document_number})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El número de documento ya está registrado")

    user = user_crud.create(db, obj_in=user_data)
    log_user_action(str(user.id), "USER_REGISTERED", {"email": user.institutional_email, "role": user.role.value})
    return UserResponse.from_orm(user)

@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    if not user_crud.authenticate(db, email=current_user.institutional_email, password=password_data.current_password):
        log_security_event("PASSWORD_CHANGE_FAILED", {"user_id": str(current_user.id)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña actual incorrecta")

    user_crud.update_password(db, user=current_user, new_password=password_data.new_password)
    log_user_action(str(current_user.id), "PASSWORD_CHANGED")
    return {"message": "Contraseña actualizada correctamente"}

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)) -> Any:
    log_user_action(str(current_user.id), "LOGOUT")
    return {"message": "Logout exitoso"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> Any:
    return UserResponse.from_orm(current_user)
