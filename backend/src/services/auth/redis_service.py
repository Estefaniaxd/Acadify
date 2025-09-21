import redis
from typing import Optional
from src.core.config import settings


class RedisService:
    """Servicio para operaciones con Redis"""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    def connect(self):
        """Establecer conexión con Redis"""
        self.redis = redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )

    def disconnect(self):
        """Cerrar conexión con Redis"""
        if self.redis:
            self.redis.close()

    # === BLACKLIST DE TOKENS ===

    def _get_blacklist_key(self, jti: str) -> str:
        """Generar clave para blacklist de token"""
        return f"blacklist:token:{jti}"

    def blacklist_token(self, jti: str, ttl_seconds: int):
        """Agregar token JTI a blacklist con TTL"""
        key = self._get_blacklist_key(jti)
        self.redis.setex(key, ttl_seconds, "1")

    def is_token_blacklisted(self, jti: str) -> bool:
        """Verificar si token está en blacklist"""
        key = self._get_blacklist_key(jti)
        return bool(self.redis.exists(key))

    # === REFRESH TOKENS ACTIVOS ===

    def _get_refresh_token_key(self, user_id: str) -> str:
        """Generar clave para refresh tokens del usuario"""
        return f"refresh_tokens:user:{user_id}"

    def store_active_refresh_token(self, user_id: str, jti: str, ttl_seconds: int):
        """Almacenar refresh token activo"""
        key = self._get_refresh_token_key(user_id)
        # Usar set para almacenar múltiples refresh tokens por usuario
        self.redis.sadd(key, jti)
        self.redis.expire(key, ttl_seconds)

    def remove_refresh_token(self, user_id: str, jti: str):
        """Remover refresh token específico"""
        key = self._get_refresh_token_key(user_id)
        self.redis.srem(key, jti)

    def invalidate_all_user_tokens(self, user_id: str):
        """Invalidar todos los tokens de un usuario"""
        key = self._get_refresh_token_key(user_id)
        refresh_tokens = self.redis.smembers(key)
        
        # Blacklist todos los refresh tokens
        for jti in refresh_tokens:
            self.blacklist_token(jti, 86400)  # 24 horas
        
        # Limpiar set de tokens activos
        self.redis.delete(key)

    # === INTENTOS DE LOGIN FALLIDOS ===

    def _get_failed_attempts_key(self, identifier: str) -> str:
        """Generar clave para intentos fallidos"""
        return f"failed_attempts:{identifier}"

    def record_failed_attempt(self, identifier: str, ttl_seconds: int = 3600):
        """Registrar intento de login fallido"""
        key = self._get_failed_attempts_key(identifier)
        self.redis.incr(key)
        self.redis.expire(key, ttl_seconds)

    def get_failed_attempts(self, identifier: str) -> int:
        """Obtener número de intentos fallidos"""
        key = self._get_failed_attempts_key(identifier)
        attempts = self.redis.get(key)
        return int(attempts) if attempts else 0

    def clear_failed_attempts(self, identifier: str):
        """Limpiar intentos fallidos después de login exitoso"""
        key = self._get_failed_attempts_key(identifier)
        self.redis.delete(key)

    # === CÓDIGOS DE VERIFICACIÓN ===

    def _get_verification_key(self, user_id: str, code_type: str) -> str:
        """Generar clave para códigos de verificación"""
        return f"verification:{code_type}:{user_id}"

    def store_verification_code(
        self, user_id: str, code_type: str, code: str, ttl_seconds: int = 600
    ):
        """Almacenar código de verificación temporal"""
        key = self._get_verification_key(user_id, code_type)
        self.redis.setex(key, ttl_seconds, code)

    def verify_code(self, user_id: str, code_type: str, provided_code: str) -> bool:
        """Verificar código de verificación"""
        key = self._get_verification_key(user_id, code_type)
        stored_code = self.redis.get(key)
        
        if stored_code and stored_code == provided_code:
            self.redis.delete(key)  # Código de un solo uso
            return True
        return False

    # === SESIONES Y CACHE ===

    def cache_user_session(self, user_id: str, session_data: dict, ttl_seconds: int):
        """Cachear datos de sesión de usuario"""
        key = f"session:user:{user_id}"
        import json
        self.redis.setex(key, ttl_seconds, json.dumps(session_data))

    def get_cached_session(self, user_id: str) -> Optional[dict]:
        """Obtener datos de sesión cacheados"""
        key = f"session:user:{user_id}"
        data = self.redis.get(key)
        if data:
            import json
            return json.loads(data)
        return None

    def clear_user_session(self, user_id: str):
        """Limpiar sesión de usuario"""
        key = f"session:user:{user_id}"
        self.redis.delete(key)