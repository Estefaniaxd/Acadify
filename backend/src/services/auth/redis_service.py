
import redis.asyncio as redis_async
from src.core.config import settings

class RedisService:
<<<<<<< HEAD
    """Servicio async para operaciones con Redis"""

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """Establecer conexión con Redis"""
        self.redis = await aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )

    async def disconnect(self):
        """Cerrar conexión con Redis"""
        if self.redis:
            await self.redis.close()

    # === BLACKLIST DE TOKENS ===

    def _get_blacklist_key(self, jti: str) -> str:
        """Generar clave para blacklist de token"""
        return f"blacklist:token:{jti}"

    async def blacklist_token(self, jti: str, ttl_seconds: int):
        """Agregar token JTI a blacklist con TTL"""
        key = self._get_blacklist_key(jti)
        await self.redis.setex(key, ttl_seconds, "revoked")

    async def is_token_blacklisted(self, jti: str) -> bool:
        """Verificar si token está en blacklist"""
        key = self._get_blacklist_key(jti)
        result = await self.redis.get(key)
        return result is not None

    # === INTENTOS DE LOGIN ===

    def _get_login_attempts_key(self, email: str) -> str:
        """Generar clave para contador de intentos fallidos"""
        return f"login_attempts:{email.lower()}"

    def _get_lockout_key(self, email: str) -> str:
        """Generar clave para bloqueo de cuenta"""
        return f"lockout:{email.lower()}"

    async def increment_login_attempts(self, email: str) -> int:
        """
        Incrementar contador de intentos fallidos

        Returns:
            int: número actual de intentos fallidos
        """
        key = self._get_login_attempts_key(email)

        # Incrementar contador con TTL de 1 hora
        attempts = await self.redis.incr(key)
        if attempts == 1:
            # Establecer TTL solo en el primer intento
            await self.redis.expire(key, 3600)  # 1 hora

        return attempts

    async def get_login_attempts(self, email: str) -> int:
        """Obtener número actual de intentos fallidos"""
        key = self._get_login_attempts_key(email)
        attempts = await self.redis.get(key)
        return int(attempts) if attempts else 0

    async def reset_login_attempts(self, email: str):
        """Resetear contador de intentos fallidos (login exitoso)"""
        key = self._get_login_attempts_key(email)
        await self.redis.delete(key)

    async def lock_account(self, email: str, duration_minutes: int = None):
        """Bloquear cuenta por intentos fallidos excesivos"""
        if duration_minutes is None:
            duration_minutes = settings.LOCKOUT_DURATION_MINUTES
        lockout_key = self._get_lockout_key(email)
        lockout_until = utcnow_aware() + timedelta(minutes=duration_minutes)
        # Almacenar hasta cuándo está bloqueada la cuenta
        await self.redis.setex(
            lockout_key,
            duration_minutes * 60,  # TTL en segundos
            lockout_until.isoformat(),
        )

    async def is_account_locked(self, email: str) -> tuple[bool, Optional[datetime]]:
        """
        Verificar si cuenta está bloqueada

        Returns:
            tuple: (is_locked, lockout_until_datetime)
        """
        lockout_key = self._get_lockout_key(email)
        lockout_until_str = await self.redis.get(lockout_key)

        if not lockout_until_str:
            return False, None

        try:
            lockout_until = datetime.fromisoformat(lockout_until_str)
            if utcnow_aware() >= lockout_until:
                # El bloqueo ya expiró, eliminarlo
                await self.redis.delete(lockout_key)
                return False, None
            return True, lockout_until
        except ValueError:
            # Formato inválido, eliminar clave
            await self.redis.delete(lockout_key)
            return False, None

    # === REFRESH TOKENS ACTIVOS ===

    def _get_user_refresh_tokens_key(self, user_id: str) -> str:
        """Generar clave para refresh tokens activos de usuario"""
        return f"user_refresh_tokens:{user_id}"

    async def store_active_refresh_token(
        self, user_id: str, jti: str, ttl_seconds: int
    ):
        """Almacenar refresh token activo para un usuario"""
        key = self._get_user_refresh_tokens_key(user_id)
        # Usar un set para almacenar múltiples refresh tokens (diferentes dispositivos)
        await self.redis.sadd(key, jti)
        await self.redis.expire(key, ttl_seconds)

    async def revoke_all_user_refresh_tokens(self, user_id: str):
        """Revocar todos los refresh tokens de un usuario"""
        key = self._get_user_refresh_tokens_key(user_id)

        # Obtener todos los JTIs de refresh tokens
        refresh_jtis = await self.redis.smembers(key)

        # Agregar cada JTI a la blacklist
        for jti in refresh_jtis:
            await self.blacklist_token(jti, 30 * 24 * 60 * 60)  # 30 días

        # Eliminar el set de refresh tokens activos
        await self.redis.delete(key)

    # === RATE LIMITING ===

    def _get_rate_limit_key(self, identifier: str, endpoint: str) -> str:
        """Generar clave para rate limiting"""
        return f"rate_limit:{endpoint}:{identifier}"

    async def check_rate_limit(
        self, identifier: str, endpoint: str, max_requests: int, window_seconds: int
    ) -> tuple[bool, int, int]:
        key = self._get_rate_limit_key(identifier, endpoint)
        current_time = int(utcnow_aware().timestamp())
        # Usar sliding window con Redis sorted sets
        pipe = self.redis.pipeline()
        # Remover entries antiguos
        pipe.zremrangebyscore(key, 0, current_time - window_seconds)
        # Contar requests actuales
        pipe.zcard(key)
        # Agregar request actual
        pipe.zadd(key, {str(current_time): current_time})
        # Establecer TTL
        pipe.expire(key, window_seconds)
        results = await pipe.execute()
        current_count = results[1]
        if current_count >= max_requests:
            return False, current_count, window_seconds
        return True, current_count + 1, window_seconds

    # === TOKENS DE RESET DE CONTRASEÑA ===

    def _get_password_reset_key(self, token: str) -> str:
        """Generar clave para token de reset de contraseña"""
        return f"password_reset:{token}"

    async def store_password_reset_token(
        self, token: str, user_id: str, ttl_minutes: int = 30
    ):
        """Almacenar token de reset de contraseña"""
        key = self._get_password_reset_key(token)
        data = {"user_id": user_id, "created_at": utcnow_aware().isoformat()}
        await self.redis.setex(key, ttl_minutes * 60, json.dumps(data))

    async def get_password_reset_data(self, token: str) -> Optional[Dict[str, Any]]:
        """Obtener datos del token de reset de contraseña"""
        key = self._get_password_reset_key(token)
        data_str = await self.redis.get(key)

        if not data_str:
            return None

        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            return None

    async def invalidate_password_reset_token(self, token: str):
        """Invalidar token de reset de contraseña (después de usar)"""
        key = self._get_password_reset_key(token)
        await self.redis.delete(key)

    # === ESTADOS DE OAUTH ===

    def _get_oauth_state_key(self, state: str) -> str:
        """Generar clave para estado de OAuth"""
        return f"oauth_state:{state}"

    async def store_oauth_state(
        self, state: str, provider: str, redirect_uri: str = None, ttl_minutes: int = 5
    ):
        """Almacenar estado de OAuth para validación CSRF"""
        key = self._get_oauth_state_key(state)
        data = {
            "provider": provider,
            "redirect_uri": redirect_uri,
            "created_at": utcnow_aware().isoformat(),
        }
        await self.redis.setex(key, ttl_minutes * 60, json.dumps(data))

    async def verify_and_consume_oauth_state(
        self, state: str
    ) -> Optional[Dict[str, Any]]:
        """Verificar y consumir estado de OAuth (una sola vez)"""
        key = self._get_oauth_state_key(state)
        data_str = await self.redis.get(key)

        if not data_str:
            return None

        # Eliminar inmediatamente para prevenir reutilización
        await self.redis.delete(key)

        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            return None
=======
	def __init__(self):
		self.redis_url = settings.REDIS_URL
		self.client = None

	async def connect(self):
		self.client = await redis_async.from_url(self.redis_url, decode_responses=True)

	async def disconnect(self):
		if self.client:
			await self.client.close()
			self.client = None
>>>>>>> origin/fix-auth
