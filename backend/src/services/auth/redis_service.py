import logging

import redis

from src.core.config import settings


class RedisService:
    """Servicio para operaciones con Redis."""

    def __init__(self) -> None:
        self.redis: redis.Redis | None = None
        self._logger = logging.getLogger(__name__)

    def connect(self) -> None:
        """Establecer conexión con Redis."""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        except redis.RedisError as exc:
            self._logger.warning("No se pudo conectar a Redis: %s", exc)
            self.redis = None

    def disconnect(self) -> None:
        """Cerrar conexión con Redis."""
        if self.redis:
            self.redis.close()

    def _ensure_client(self) -> redis.Redis | None:
        """Devuelve un cliente Redis válido o None si no hay conexión."""

        if self.redis is None:
            self.connect()
        if self.redis is None:
            self._logger.debug("Redis no disponible, la operación se omitirá")
        return self.redis

    # === BLACKLIST DE TOKENS ===

    def _get_blacklist_key(self, jti: str) -> str:
        """Generar clave para blacklist de token."""
        return f"blacklist:token:{jti}"

    def blacklist_token(self, jti: str, ttl_seconds: int) -> None:
        """Agregar token JTI a blacklist con TTL."""
        key = self._get_blacklist_key(jti)
        client = self._ensure_client()
        if not client:
            return
        client.setex(key, ttl_seconds, "1")

    def is_token_blacklisted(self, jti: str) -> bool:
        """Verificar si token está en blacklist."""
        key = self._get_blacklist_key(jti)
        client = self._ensure_client()
        if not client:
            return False
        return bool(client.exists(key))

    # === REFRESH TOKENS ACTIVOS ===

    def _get_refresh_token_key(self, user_id: str) -> str:
        """Generar clave para refresh tokens del usuario."""
        return f"refresh_tokens:user:{user_id}"

    def store_active_refresh_token(
        self, user_id: str, jti: str, ttl_seconds: int
    ) -> None:
        """Almacenar refresh token activo."""
        key = self._get_refresh_token_key(user_id)
        client = self._ensure_client()
        if not client:
            return
        # Usar set para almacenar múltiples refresh tokens por usuario
        client.sadd(key, jti)
        client.expire(key, ttl_seconds)

    def remove_refresh_token(self, user_id: str, jti: str) -> None:
        """Remover refresh token específico."""
        key = self._get_refresh_token_key(user_id)
        client = self._ensure_client()
        if not client:
            return
        client.srem(key, jti)

    def invalidate_all_user_tokens(self, user_id: str) -> None:
        """Invalidar todos los tokens de un usuario."""
        key = self._get_refresh_token_key(user_id)
        client = self._ensure_client()
        if not client:
            return
        refresh_tokens = client.smembers(key)

        # Blacklist todos los refresh tokens
        for jti in refresh_tokens:
            self.blacklist_token(jti, 86400)  # 24 horas

        # Limpiar set de tokens activos
        client.delete(key)

    def revoke_all_user_refresh_tokens(self, user_id: str) -> None:
        """Alias semántico para invalidar tokens de refresco."""

        self.invalidate_all_user_tokens(user_id)

    # === INTENTOS DE LOGIN FALLIDOS ===

    def _get_failed_attempts_key(self, identifier: str) -> str:
        """Generar clave para intentos fallidos."""
        return f"failed_attempts:{identifier}"

    def record_failed_attempt(self, identifier: str, ttl_seconds: int = 3600) -> None:
        """Registrar intento de login fallido."""
        key = self._get_failed_attempts_key(identifier)
        client = self._ensure_client()
        if not client:
            return
        client.incr(key)
        client.expire(key, ttl_seconds)

    def get_failed_attempts(self, identifier: str) -> int:
        """Obtener número de intentos fallidos."""
        key = self._get_failed_attempts_key(identifier)
        client = self._ensure_client()
        if not client:
            return 0
        attempts = client.get(key)
        return int(attempts) if attempts else 0

    def clear_failed_attempts(self, identifier: str) -> None:
        """Limpiar intentos fallidos después de login exitoso."""
        key = self._get_failed_attempts_key(identifier)
        client = self._ensure_client()
        if not client:
            return
        client.delete(key)

    # === CÓDIGOS DE VERIFICACIÓN ===

    def _get_verification_key(self, user_id: str, code_type: str) -> str:
        """Generar clave para códigos de verificación."""
        return f"verification:{code_type}:{user_id}"

    def store_verification_code(
        self, user_id: str, code_type: str, code: str, ttl_seconds: int = 600
    ) -> None:
        """Almacenar código de verificación temporal."""
        key = self._get_verification_key(user_id, code_type)
        client = self._ensure_client()
        if not client:
            return
        client.setex(key, ttl_seconds, code)

    def verify_code(self, user_id: str, code_type: str, provided_code: str) -> bool:
        """Verificar código de verificación."""
        key = self._get_verification_key(user_id, code_type)
        client = self._ensure_client()
        if not client:
            return False
        stored_code = client.get(key)

        if stored_code and stored_code == provided_code:
            client.delete(key)  # Código de un solo uso
            return True
        return False

    # === SESIONES Y CACHE ===

    def cache_user_session(
        self, user_id: str, session_data: dict, ttl_seconds: int
    ) -> None:
        """Cachear datos de sesión de usuario."""
        key = f"session:user:{user_id}"
        import json

        client = self._ensure_client()
        if not client:
            return
        client.setex(key, ttl_seconds, json.dumps(session_data))

    def get_cached_session(self, user_id: str) -> dict | None:
        """Obtener datos de sesión cacheados."""
        key = f"session:user:{user_id}"
        client = self._ensure_client()
        if not client:
            return None
        data = client.get(key)
        if data:
            import json

            return json.loads(data)
        return None

    def clear_user_session(self, user_id: str) -> None:
        """Limpiar sesión de usuario."""
        key = f"session:user:{user_id}"
        client = self._ensure_client()
        if not client:
            return
        client.delete(key)
