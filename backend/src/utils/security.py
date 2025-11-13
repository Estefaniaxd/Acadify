# src/utils/security.py
import asyncio
from datetime import UTC, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import secrets
import string
from typing import Any

import aiosmtplib
from fastapi import HTTPException, status
from jinja2 import Environment, FileSystemLoader
from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp
import redis.asyncio as redis

from src.core.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


# ===============================
# Security Manager
# ===============================
class SecurityManager:
    """Maneja operaciones de seguridad: hashing, tokens, OTP."""

    def __init__(self) -> None:
        # Solo BCrypt para máxima compatibilidad
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña con bcrypt."""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.exception(f"Error verificando contraseña: {e}")
            return False

    def get_password_hash(self, password: str) -> str:
        """Hash de contraseña con bcrypt."""
        return self.pwd_context.hash(password)

    def needs_update(self, hashed_password: str) -> bool:
        """Verificar si el hash necesita actualización."""
        return self.pwd_context.needs_update(hashed_password)

    def create_access_token(
        self,
        subject: str,
        expires_delta: timedelta | None = None,
        additional_claims: dict[str, Any] | None = None,
    ) -> str:
        """Crear access token JWT."""
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {
            "exp": expire,
            "sub": subject,
            "type": "access",
            "iat": datetime.now(UTC),
        }

        if additional_claims:
            to_encode.update(additional_claims)

        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_refresh_token(self, subject: str) -> tuple[str, str]:
        """Crear refresh token JWT con JTI único."""
        jti = secrets.token_urlsafe(32)
        expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {
            "exp": expire,
            "sub": subject,
            "type": "refresh",
            "jti": jti,
            "iat": datetime.now(UTC),
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt, jti

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decodificar y validar token JWT."""
        try:
            # Log para depuración
            logger.debug(
                f"Intentando decodificar token: {token[:10] if token else 'None'}..."
            )

            if not token or len(token.strip()) == 0:
                logger.warning("Token vacío o nulo")
                msg = "Token vacío o nulo"
                raise JWTError(msg)

            # Verificar formato básico (3 partes separadas por puntos)
            parts = token.split(".")
            if len(parts) != 3:
                logger.warning(f"Token con formato incorrecto: {len(parts)} partes")
                msg = "Not enough segments"
                raise JWTError(msg)

            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

            logger.debug(f"Token decodificado correctamente: {payload.get('sub')}")
            return payload
        except JWTError as e:
            # Para operaciones críticas (login, refresh token, etc.) no mostrar detalles específicos
            # Esto previene la filtración de información sensible
            logger.warning(f"Token inválido: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e
        """Decodificar y validar token JWT"""
        try:
            # Log para depuración
            logger.debug(f"Intentando decodificar token: {token[:10]}...")

            if not token or len(token.strip()) == 0:
                logger.warning("Token vacío o nulo")
                msg = "Token vacío o nulo"
                raise JWTError(msg)

            # Verificar formato básico (3 partes separadas por puntos)
            parts = token.split(".")
            if len(parts) != 3:
                logger.warning(f"Token con formato incorrecto: {len(parts)} partes")
                msg = "Not enough segments"
                raise JWTError(msg)

            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

            # Verificar campos requeridos en el token
            if "sub" not in payload:
                logger.warning("Token sin campo 'sub' (subject)")
                msg = "Token sin subject"
                raise JWTError(msg)

            if "exp" not in payload:
                logger.warning("Token sin campo 'exp' (expiration)")
                msg = "Token sin expiración"
                raise JWTError(msg)

            # Más información sobre el token para depuración
            logger.debug("Token decodificado correctamente:")
            logger.debug(f"- Subject: {payload.get('sub')}")
            logger.debug(f"- Type: {payload.get('type')}")
            logger.debug(f"- Roles: {payload.get('roles', 'No hay roles')}")
            logger.debug(f"- Expires: {payload.get('exp')}")

            return payload

        except JWTError as e:
            logger.warning(f"Token inválido: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido o expirado: {e!s}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    def generate_otp_code(self, length: int = 6) -> str:
        """Generar código OTP numérico seguro."""
        return "".join(secrets.choice(string.digits) for _ in range(length))

    def generate_totp_secret(self) -> str:
        """Generar secret para TOTP."""
        return pyotp.random_base32()

    def get_totp_provisioning_uri(
        self, user_email: str, secret: str, issuer: str = "Acadify"
    ) -> str:
        """Generar URI de provisioning para QR TOTP."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=user_email, issuer_name=issuer)

    def verify_totp_code(self, secret: str, code: str, window: int = 1) -> bool:
        """Verificar código TOTP."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, window=window)


# ===============================
# Token Blacklist Manager
# ===============================
class TokenBlacklist:
    """Maneja la blacklist de tokens en Redis."""

    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client
        self.prefix = "blacklist"

    async def add_token(self, token: str, expires_at: datetime) -> None:
        """Añadir token a blacklist con TTL."""
        key = f"{self.prefix}:{token}"
        ttl = int((expires_at - datetime.now(UTC)).total_seconds())
        if ttl > 0:
            await self.redis.setex(key, ttl, "1")

    async def is_blacklisted(self, token: str) -> bool:
        """Verificar si token está en blacklist."""
        key = f"{self.prefix}:{token}"
        result = await self.redis.get(key)
        return result is not None


# ===============================
# Login Attempt Manager
# ===============================
class LoginAttemptManager:
    """Maneja intentos de login y lockout de cuentas."""

    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client
        self.attempt_prefix = "login_attempts"
        self.lockout_prefix = "account_locked"
        self.max_attempts = settings.MAX_LOGIN_ATTEMPTS
        self.lockout_duration = settings.LOCKOUT_DURATION_MINUTES
        self.attempt_window = settings.LOGIN_ATTEMPT_WINDOW_MINUTES

    async def record_failed_attempt(self, identifier: str) -> dict[str, Any]:
        """Registrar intento fallido y determinar si bloquear cuenta."""
        attempt_key = f"{self.attempt_prefix}:{identifier}"
        lockout_key = f"{self.lockout_prefix}:{identifier}"

        # Incrementar contador de intentos
        attempts = await self.redis.incr(attempt_key)

        # Establecer TTL en primer intento
        if attempts == 1:
            await self.redis.expire(attempt_key, self.attempt_window * 60)

        attempts_remaining = max(0, self.max_attempts - attempts)

        # Verificar si se debe bloquear cuenta
        if attempts >= self.max_attempts:
            lockout_until = datetime.now(UTC) + timedelta(minutes=self.lockout_duration)
            await self.redis.setex(
                lockout_key, self.lockout_duration * 60, lockout_until.isoformat()
            )
            # Limpiar contador de intentos
            await self.redis.delete(attempt_key)
            return {
                "locked": True,
                "attempts_remaining": 0,
                "lockout_until": lockout_until,
                "message": f"Cuenta bloqueada por múltiples intentos fallidos. Inténtelo nuevamente en {self.lockout_duration} minutos.",
            }

        return {
            "locked": False,
            "attempts_remaining": attempts_remaining,
            "lockout_until": None,
            "message": f"Credenciales incorrectas. {attempts_remaining} intentos restantes.",
        }

    async def is_account_locked(self, identifier: str) -> dict[str, Any] | None:
        """Verificar si cuenta está bloqueada."""
        lockout_key = f"{self.lockout_prefix}:{identifier}"
        lockout_until_str = await self.redis.get(lockout_key)

        if lockout_until_str:
            lockout_until = datetime.fromisoformat(lockout_until_str.decode())
            if lockout_until > datetime.now(UTC):
                return {
                    "locked": True,
                    "lockout_until": lockout_until,
                    "message": f"Cuenta bloqueada hasta {lockout_until.strftime('%Y-%m-%d %H:%M:%S')}",
                }
            # Lockout expirado, limpiar
            await self.redis.delete(lockout_key)

        return None

    async def clear_attempts(self, identifier: str) -> None:
        """Limpiar intentos fallidos tras login exitoso."""
        attempt_key = f"{self.attempt_prefix}:{identifier}"
        lockout_key = f"{self.lockout_prefix}:{identifier}"

        await self.redis.delete(attempt_key)
        await self.redis.delete(lockout_key)


# ===============================
# Email Service
# ===============================
class EmailService:
    """Servicio de envío de correos con templates."""

    def __init__(self) -> None:
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASS
        self.from_email = settings.EMAIL_FROM
        self.use_tls = settings.SMTP_TLS

        # Configurar Jinja2 para templates
        self.template_env = Environment(
            loader=FileSystemLoader("src/templates/emails"), autoescape=True
        )

    async def send_template_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: dict[str, Any],
        max_retries: int = 3,
        background: bool = False,  # Nuevo parámetro para envío en background
    ) -> None:
        """Enviar email usando template Jinja2 con reintentos.

        Args:
            background: Si es True, envía el email en background sin bloquear la respuesta
        """
        template = self.template_env.get_template(template_name)
        html_body = template.render(**context)

        if background:
            # Enviar en background sin esperar
            task = asyncio.create_task(
                self._send_email_with_retries(to_email, subject, html_body, max_retries)
            )
            # No esperamos el resultado pero guardamos la tarea para evitar GC
            task.add_done_callback(lambda t: None)
            logger.info(f"📧 Email programado para envío en background a {to_email}")
            return

        # Envío síncrono (espera respuesta)
        await self._send_email_with_retries(to_email, subject, html_body, max_retries)

    async def _send_email_with_retries(
        self, to_email: str, subject: str, html_body: str, max_retries: int
    ) -> None:
        """Enviar email con reintentos (método interno)."""
        for attempt in range(max_retries + 1):
            try:
                await self._send_email(to_email, subject, html_body)
                logger.info(f"Email enviado exitosamente a {to_email}")
                return

            except Exception as e:
                logger.exception(f"Error enviando email (intento {attempt + 1}): {e}")
                if attempt == max_retries:
                    logger.exception(
                        f"❌ Falló el envío de email a {to_email} después de {max_retries + 1} intentos"
                    )
                    return  # No lanza excepción en background
                await asyncio.sleep(2**attempt)  # Backoff exponencial

    async def _send_email(self, to_email: str, subject: str, html_body: str) -> None:
        """Enviar email usando aiosmtplib."""
        message = MIMEMultipart("alternative")
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject

        html_part = MIMEText(html_body, "html", "utf-8")
        message.attach(html_part)

        await aiosmtplib.send(
            message,
            hostname=self.smtp_host,
            port=self.smtp_port,
            start_tls=self.use_tls,
            username=self.smtp_user,
            password=self.smtp_password,
        )


# ===============================
# Singletons globales
# ===============================
security_manager = SecurityManager()


def get_token_blacklist(redis_client: redis.Redis) -> TokenBlacklist:
    """Factory para TokenBlacklist."""
    if redis_client is None:
        msg = "Redis no inicializado"
        raise RuntimeError(msg)
    return TokenBlacklist(redis_client)


def get_login_attempt_manager(redis_client: redis.Redis) -> LoginAttemptManager:
    """Factory para LoginAttemptManager."""
    if redis_client is None:
        msg = "Redis no inicializado"
        raise RuntimeError(msg)
    return LoginAttemptManager(redis_client)


def get_email_service() -> EmailService:
    """Factory para EmailService."""
    return EmailService()


# ===============================
# Utilities adicionales
# ===============================
def generate_reset_token() -> str:
    """Generar token seguro para reset de contraseña."""
    return secrets.token_urlsafe(32)


def is_strong_password(password: str) -> tuple[bool, str]:
    """Validar fortaleza de contraseña."""
    if len(password) < 10:
        return False, "La contraseña debe tener al menos 10 caracteres"

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*(),.?":{}|<>' for c in password)

    if not all([has_upper, has_lower, has_digit, has_special]):
        return (
            False,
            "La contraseña debe contener al menos: 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial",
        )

    return True, "Contraseña válida"
