# src/services/security.py
from datetime import timedelta
from src.services.auth.datetime_utils import utcnow_aware
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.services.auth.redis_service import RedisService
import pyotp

# 🔑 Configuración básica
SECRET_KEY = "cambia_esto_por_un_secret_key_muy_seguro"  # ⚠️ Usa dotenv
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Servicio de Redis
redis_service = RedisService()


# -------------------------------
# 🔐 Funciones de contraseñas
# -------------------------------
def hash_password(password: str) -> str:
    """Genera un hash seguro de la contraseña"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña sea válida"""
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------------
# 🔑 JWT Tokens
# -------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un access token JWT"""
    to_encode = data.copy()
    expire = utcnow_aware() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Genera un refresh token JWT"""
    expire = utcnow_aware() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decodifica un token y devuelve el payload"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Token inválido o expirado")


# -------------------------------
# 🗑️ Manejo de blacklist con Redis
# -------------------------------
def blacklist_token(token: str, exp: int):
    """Guarda un token en blacklist hasta que expire"""
    redis_service.setex(f"blacklist:{token}", exp, "true")


def is_token_blacklisted(token: str) -> bool:
    """Verifica si un token está en blacklist"""
    return redis_service.get(f"blacklist:{token}") is not None


# -------------------------------
# 🔐 Autenticación de dos factores (2FA)
# -------------------------------
def generate_2fa_secret() -> str:
    """Genera un secreto para 2FA con TOTP"""
    return pyotp.random_base32()


def get_otp_uri(secret: str, username: str, issuer: str = "AcadifyApp") -> str:
    """Genera la URI que apps como Google Authenticator usan"""
    return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)


def verify_2fa_token(secret: str, token: str) -> bool:
    """Verifica un código 2FA"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token)


def authenticate_user(user: dict, password: str) -> bool:
    """
    Valida credenciales de un usuario (user debe traer 'hashed_password').
    """
    return verify_password(password, user["hashed_password"])
