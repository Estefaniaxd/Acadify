"""
Seguridad central para Acadify
Incluye autenticación, autorización, protección, bloqueo de cuentas y gestión de JWT
"""

from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import redis

from app.models.user import User, AccountStatus
from app.core.config import settings
from app.core.logging import app_logger
from app.crud.user import user_crud
from app.core.token_manager import TokenManager  # Nuevo módulo

# -------------------------------
# OAuth2
# -------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login/oauth")

# -------------------------------
# Redis fallback
# -------------------------------
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True) if settings.REDIS_URL else None
except Exception as e:
    redis_client = None
    app_logger.warning(f"Redis no disponible, usando memoria en fallback. Error: {e}")

memory_storage = {}

# -------------------------------
# Password Policy
# -------------------------------
class PasswordPolicy:
    def __init__(self):
        self.min_length = 8
        self.max_length = 128
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_numbers = True
        self.require_symbols = True
        self.min_unique_chars = 6
        self.forbidden_passwords = {"password", "123456", "admin", "letmein", "welcome", "acadify"}

    def validate_password(self, password: str, user_email: str = "") -> tuple[bool, list[str]]:
        errors = []
        if len(password) < self.min_length:
            errors.append(f"Debe tener al menos {self.min_length} caracteres")
        if len(password) > self.max_length:
            errors.append(f"No puede tener más de {self.max_length} caracteres")
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Debe contener al menos una letra mayúscula")
        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append("Debe contener al menos una letra minúscula")
        if self.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Debe contener al menos un número")
        if self.require_symbols:
            symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in symbols for c in password):
                errors.append("Debe contener al menos un símbolo especial")
        if len(set(password.lower())) < self.min_unique_chars:
            errors.append(f"Debe contener al menos {self.min_unique_chars} caracteres únicos")
        if password.lower() in self.forbidden_passwords:
            errors.append("Esta contraseña es demasiado común")
        if user_email:
            email_parts = user_email.lower().split('@')[0].split('.')
            for part in email_parts:
                if len(part) > 3 and part in password.lower():
                    errors.append("No debe contener partes de tu email")
        return len(errors) == 0, errors

password_policy = PasswordPolicy()

# -------------------------------
# Logging
# -------------------------------
def log_security_event(event_type: str, details: dict, severity: str = "INFO"):
    app_logger.log(getattr(__import__('logging'), severity.upper(), 20), f"{event_type}: {details}")

# -------------------------------
# Account Lockout
# -------------------------------
class AccountLockout:
    def __init__(self):
        self.max_attempts = 5
        self.lockout_duration = 900  # 15 min
        self.ip_max_attempts = 10
        self.ip_lockout_duration = 3600  # 1 hora

    def _get_key(self, identifier: str, key_type: str):
        return f"{key_type}:{identifier}"

    async def check_lockout(self, identifier: str, key_type: str = "email") -> bool:
        key = self._get_key(identifier, "lockout")
        try:
            lockout_until = None
            if redis_client:
                lockout_until = redis_client.get(key)
            else:
                lockout_until = memory_storage.get(key)
            if lockout_until:
                if datetime.utcnow() < datetime.fromisoformat(lockout_until):
                    return True
                # expiró
                if redis_client:
                    redis_client.delete(key)
                else:
                    memory_storage.pop(key, None)
            return False
        except Exception as e:
            app_logger.warning(f"Error check_lockout: {e}")
            return False

    async def record_failed_attempt(self, identifier: str, key_type: str = "email") -> bool:
        attempts_key = self._get_key(identifier, "attempts")
        lockout_key = self._get_key(identifier, "lockout")
        max_attempts = self.max_attempts if key_type == "email" else self.ip_max_attempts
        lockout_duration = self.lockout_duration if key_type == "email" else self.ip_lockout_duration
        try:
            if redis_client:
                attempts = redis_client.incr(attempts_key)
                redis_client.expire(attempts_key, lockout_duration)
            else:
                attempts = memory_storage.get(attempts_key, 0) + 1
                memory_storage[attempts_key] = attempts
            if attempts >= max_attempts:
                lockout_until = datetime.utcnow() + timedelta(seconds=lockout_duration)
                if redis_client:
                    redis_client.setex(lockout_key, lockout_duration, lockout_until.isoformat())
                else:
                    memory_storage[lockout_key] = lockout_until
                log_security_event("ACCOUNT_LOCKED", {"identifier": identifier, "attempts": attempts}, "WARNING")
                return True
            return False
        except Exception as e:
            app_logger.warning(f"Error record_failed_attempt: {e}")
            return False

    async def reset_failed_attempts(self, identifier: str):
        keys = [self._get_key(identifier, "attempts"), self._get_key(identifier, "lockout")]
        try:
            if redis_client:
                redis_client.delete(*keys)
            else:
                for k in keys:
                    memory_storage.pop(k, None)
        except Exception as e:
            app_logger.warning(f"Error reset_failed_attempts: {e}")

account_lockout = AccountLockout()

# -------------------------------
# User Dependencies
# -------------------------------
async def get_user_from_token(token: str, db=Depends()):
    payload = TokenManager.decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends()):
    return await get_user_from_token(token, db)

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.account_status != AccountStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")
    return current_user

# Al final de security.py
token_manager = TokenManager()
