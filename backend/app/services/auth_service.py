# backend/app/services/auth_service.py
"""
Servicio de autenticación avanzado y escalable
Gestiona login, logout, refresh de tokens, blacklist y sesiones activas
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import redis

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.logging import app_logger, log_security_event, log_user_action
from app.crud.user import user_crud
from app.utils.exceptions import AcadifyException


class AuthService:
    """Servicio avanzado de autenticación"""

    def __init__(self):
        self.redis_client = None
        self._memory_storage: Dict[str, Any] = {}
        try:
            if settings.REDIS_URL:
                self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            app_logger.warning(f"Redis no disponible, usando memoria: {e}")

        self.failed_attempt_ttl = 900  # 15 minutos
        self.refresh_token_ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600

    # --------------------------
    # LOGIN
    # --------------------------
    async def login_user(
        self, email: str, password: str, ip_address: str, user_agent: str, db: Session
    ) -> Dict[str, Any]:

        await self._check_login_attempts(email, ip_address)
        user = user_crud.authenticate(db, email=email, password=password)

        if not user:
            await self._record_failed_attempt(email, ip_address)
            log_security_event("LOGIN_FAILED", {"email": email, "ip": ip_address, "user_agent": user_agent})
            raise AcadifyException("Email o contraseña incorrectos", 401, "INVALID_CREDENTIALS")

        if not user_crud.is_active(user):
            log_security_event("LOGIN_INACTIVE_USER", {"user_id": str(user.id), "email": email, "ip": ip_address})
            raise AcadifyException("Cuenta inactiva", 400, "INACTIVE_ACCOUNT")

        await self._clear_failed_attempts(email, ip_address)

        access_token = create_access_token({"sub": str(user.id), "role": user.role.value},
                                           expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role.value})

        await self._store_refresh_token(user.id, refresh_token)
        user_crud.update_last_access(db, user=user)
        log_user_action(str(user.id), "LOGIN_SUCCESS", {"ip": ip_address, "user_agent": user_agent})

        return {"user": user, "access_token": access_token, "refresh_token": refresh_token}

    # --------------------------
    # LOGOUT
    # --------------------------
    async def logout_user(self, user_id: str, access_token: str, refresh_token: str):
        await self._blacklist_token(access_token)
        await self._blacklist_token(refresh_token)
        await self._remove_refresh_token(user_id, refresh_token)
        log_user_action(user_id, "LOGOUT_SUCCESS")

    # --------------------------
    # REFRESH TOKENS
    # --------------------------
    async def refresh_user_tokens(self, refresh_token: str, db: Session) -> Dict[str, str]:
        if await self._is_token_blacklisted(refresh_token):
            raise AcadifyException("Token inválido o revocado", 401, "INVALID_REFRESH_TOKEN")

        payload = verify_token(refresh_token, "refresh")
        if not payload:
            raise AcadifyException("Token inválido", 401, "INVALID_REFRESH_TOKEN")

        user_id = payload.get("sub")
        user = user_crud.get(db, id=user_id)
        if not user or not user_crud.is_active(user):
            raise AcadifyException("Usuario no encontrado o inactivo", 401, "USER_NOT_FOUND")

        if not await self._is_refresh_token_valid(user_id, refresh_token):
            raise AcadifyException("Token de refresco no válido", 401, "INVALID_REFRESH_TOKEN")

        await self._blacklist_token(refresh_token)
        await self._remove_refresh_token(user_id, refresh_token)

        access_token = create_access_token({"sub": str(user.id), "role": user.role.value},
                                           expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        new_refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role.value})
        await self._store_refresh_token(user.id, new_refresh_token)

        log_user_action(user.id, "TOKEN_REFRESHED")
        return {"access_token": access_token, "refresh_token": new_refresh_token}

    # --------------------------
    # LOGIN ATTEMPTS
    # --------------------------
    async def _check_login_attempts(self, email: str, ip_address: str):
        max_attempts = 5
        email_attempts = await self._get_failed_attempts(f"email:{email}")
        if email_attempts >= max_attempts:
            raise AcadifyException("Cuenta temporalmente bloqueada", 429, "ACCOUNT_LOCKED")
        ip_attempts = await self._get_failed_attempts(f"ip:{ip_address}")
        if ip_attempts >= max_attempts * 2:
            raise AcadifyException("Demasiados intentos desde esta IP", 429, "IP_BLOCKED")

    async def _record_failed_attempt(self, email: str, ip_address: str):
        await self._increment_failed_attempts(f"email:{email}")
        await self._increment_failed_attempts(f"ip:{ip_address}")

    async def _clear_failed_attempts(self, email: str, ip_address: str):
        await self._reset_failed_attempts(f"email:{email}")
        await self._reset_failed_attempts(f"ip:{ip_address}")

    # --------------------------
    # BLACKLIST & REFRESH TOKENS
    # --------------------------
    async def _blacklist_token(self, token: str):
        payload = verify_token(token, "access") or verify_token(token, "refresh")
        if payload:
            jti = payload.get("jti", token[-20:])
            ttl = max(0, payload.get("exp", 0) - int(datetime.utcnow().timestamp()))
            await self._store_value(f"blacklist:{jti}", "1", ttl)

    async def _is_token_blacklisted(self, token: str) -> bool:
        payload = verify_token(token, "access") or verify_token(token, "refresh")
        if payload:
            jti = payload.get("jti", token[-20:])
            return await self._get_value(f"blacklist:{jti}") is not None
        return False

    async def _store_refresh_token(self, user_id: str, refresh_token: str):
        await self._store_value(f"refresh_token:{user_id}:{refresh_token[-20:]}", refresh_token, self.refresh_token_ttl)

    async def _is_refresh_token_valid(self, user_id: str, refresh_token: str) -> bool:
        stored = await self._get_value(f"refresh_token:{user_id}:{refresh_token[-20:]}")
        return stored == refresh_token

    async def _remove_refresh_token(self, user_id: str, refresh_token: str):
        await self._delete_value(f"refresh_token:{user_id}:{refresh_token[-20:]}")

    # --------------------------
    # SESIONES
    # --------------------------
    async def revoke_all_user_tokens(self, user_id: str):
        pattern = f"refresh_token:{user_id}:*"
        keys = await self._get_keys(pattern)
        for key in keys:
            await self._delete_value(key)
        log_user_action(user_id, "REVOKE_ALL_TOKENS")

    async def get_active_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        pattern = f"refresh_token:{user_id}:*"
        keys = await self._get_keys(pattern)
        sessions = []
        for key in keys:
            ttl = await self._ttl(key)
            if ttl > 0:
                sessions.append({
                    "session_id": key.split(":")[-1],
                    "expires_in": ttl,
                    "created_at": datetime.utcnow() - timedelta(seconds=self.refresh_token_ttl - ttl)
                })
        return sessions

    # --------------------------
    # UTILIDADES GENÉRICAS (Redis o memoria)
    # --------------------------
    async def _store_value(self, key: str, value: str, ttl: int):
        if self.redis_client:
            self.redis_client.setex(key, ttl, value)
        else:
            self._memory_storage[key] = {"value": value, "expires": datetime.utcnow() + timedelta(seconds=ttl)}

    async def _get_value(self, key: str) -> Optional[str]:
        if self.redis_client:
            return self.redis_client.get(key)
        else:
            data = self._memory_storage.get(key)
            if data and data["expires"] > datetime.utcnow():
                return data["value"]
            self._memory_storage.pop(key, None)
            return None

    async def _delete_value(self, key: str):
        if self.redis_client:
            self.redis_client.delete(key)
        else:
            self._memory_storage.pop(key, None)

    async def _get_keys(self, pattern: str) -> List[str]:
        if self.redis_client:
            return self.redis_client.keys(pattern)
        else:
            return [k for k in self._memory_storage.keys() if k.startswith(pattern.replace("*", ""))]

    async def _ttl(self, key: str) -> int:
        if self.redis_client:
            return self.redis_client.ttl(key)
        else:
            data = self._memory_storage.get(key)
            if data:
                return max(0, int((data["expires"] - datetime.utcnow()).total_seconds()))
            return -1

    async def _get_failed_attempts(self, key: str) -> int:
        value = await self._get_value(f"failed_attempts:{key}")
        return int(value) if value else 0

    async def _increment_failed_attempts(self, key: str):
        value = await self._get_value(f"failed_attempts:{key}")
        value = int(value) + 1 if value else 1
        await self._store_value(f"failed_attempts:{key}", str(value), self.failed_attempt_ttl)

    async def _reset_failed_attempts(self, key: str):
        await self._delete_value(f"failed_attempts:{key}")


# Instancia global
auth_service = AuthService()
