"""Generador de JWT (JSON Web Tokens) para autenticación en Jitsi Meet.

Este módulo proporciona funcionalidad para generar tokens JWT válidos para
Jitsi Meet siguiendo el estándar especificado en la documentación oficial.

Principios SOLID aplicados:
- Single Responsibility: Este módulo solo se encarga de generar tokens JWT para Jitsi
- Open/Closed: Extensible mediante parámetros sin modificar código existente
- Liskov Substitution: Las funciones pueden intercambiarse por versiones mejoradas
- Interface Segregation: Funciones específicas para cada tipo de token
- Dependency Inversion: Depende de abstracciones (config) no de implementaciones concretas

Referencias:
- Jitsi Meet JWT: https://jitsi.github.io/handbook/docs/devops-guide/secure-domain
- JWT Spec: https://jwt.io/introduction
"""

from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import UUID

import jwt

from src.core.config import get_settings


# ===============================
# Configuración de Jitsi
# ===============================

# Estas constantes deberían estar en .env en producción
JITSI_APP_ID = "acadify"  # Identificador de la aplicación
JITSI_APP_SECRET = get_settings().SECRET_KEY  # Secret para firmar tokens
JITSI_DOMAIN = "meet.acadify.com"  # Dominio de Jitsi (cambiar en producción)


# ===============================
# Tipos y Literales
# ===============================

TipoLlamada = Literal["video", "voz"]
CalidadConexion = Literal["excelente", "buena", "regular", "mala"]


# ===============================
# Helper Functions
# ===============================


def now_utc() -> datetime:
    """Retorna datetime actual con timezone UTC.

    Importante: Siempre usar datetime timezone-aware para evitar
    problemas de comparación y serialización.

    Returns:
        datetime: Fecha y hora actual en UTC timezone-aware
    """
    return datetime.now(UTC)


def uuid_to_str(uuid_value: UUID | None) -> str | None:
    """Convierte UUID a string si no es None.

    Args:
        uuid_value: UUID a convertir

    Returns:
        str or None: String representation del UUID o None
    """
    return str(uuid_value) if uuid_value else None


# ===============================
# Token Generation Functions
# ===============================


def generate_jitsi_token(
    user_id: UUID,
    room_name: str,
    user_name: str,
    user_email: str | None = None,
    user_avatar: str | None = None,
    is_moderator: bool = False,
    expiration_minutes: int = 120,  # 2 horas por defecto
    features: dict[str, bool] | None = None,
    context_extras: dict[str, Any] | None = None,
) -> str:
    """Genera un JWT válido para autenticación en Jitsi Meet.

    El token incluye:
    - Información del usuario (id, nombre, email, avatar)
    - Permisos de moderador
    - Features habilitadas (grabación, livestreaming, etc.)
    - Expiración configurable

    Estructura del JWT según Jitsi Meet spec:
    {
        "context": {
            "user": {
                "id": "user-id",
                "name": "User Name",
                "email": "user@example.com",
                "avatar": "https://...",
                "affiliation": "owner|member"
            },
            ...custom fields...
        },
        "room": "room-name",
        "aud": "jitsi-app-id",
        "iss": "jitsi-app-id",
        "sub": "jitsi-domain",
        "exp": timestamp,
        "iat": timestamp,
        "nbf": timestamp,
        "moderator": true|false
    }

    Args:
        user_id: UUID del usuario
        room_name: Nombre de la sala de Jitsi (jitsi_room_name)
        user_name: Nombre completo del usuario para mostrar
        user_email: Email del usuario (opcional)
        user_avatar: URL del avatar del usuario (opcional)
        is_moderator: Si el usuario tiene privilegios de moderador
        expiration_minutes: Tiempo de expiración del token en minutos
        features: Diccionario de features a habilitar/deshabilitar
        context_extras: Datos adicionales a incluir en el contexto

    Returns:
        str: JWT firmado listo para usar en Jitsi Meet

    Example:
        >>> token = generate_jitsi_token(
        ...     user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        ...     room_name="clase-matematicas-101",
        ...     user_name="Juan Pérez",
        ...     user_email="juan@example.com",
        ...     is_moderador=True,
        ...     features={"recording": True, "livestreaming": False}
        ... )
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    # Timestamps
    now = now_utc()
    exp_time = now + timedelta(minutes=expiration_minutes)

    # Features por defecto si no se especifican
    if features is None:
        features = {
            "recording": False,
            "livestreaming": False,
            "transcription": False,
            "outbound-call": False,
            "sip-outbound-call": False,
            "screen-sharing": True,
            "video-share": True,
            "audio-mute": True,
            "video-mute": True,
        }

    # Construir el payload del JWT
    payload = {
        # Standard JWT claims
        "aud": JITSI_APP_ID,  # Audience
        "iss": JITSI_APP_ID,  # Issuer
        "sub": JITSI_DOMAIN,  # Subject (dominio de Jitsi)
        "exp": int(exp_time.timestamp()),  # Expiration time
        "iat": int(now.timestamp()),  # Issued at
        "nbf": int(now.timestamp()),  # Not before
        # Jitsi-specific claims
        "room": room_name,  # Nombre de la sala
        "moderator": is_moderator,  # Permisos de moderador
        # Context con información del usuario
        "context": {
            "user": {
                "id": uuid_to_str(user_id),
                "name": user_name,
                "email": user_email or "",
                "avatar": user_avatar or "",
                "affiliation": "owner" if is_moderator else "member",
            },
            "features": features,
        },
    }

    # Añadir campos extras al contexto si se proporcionan
    if context_extras:
        payload["context"].update(context_extras)

    # Generar y firmar el token
    return jwt.encode(payload=payload, key=JITSI_APP_SECRET, algorithm="HS256")


def generate_moderator_token(
    user_id: UUID,
    room_name: str,
    user_name: str,
    user_email: str | None = None,
    user_avatar: str | None = None,
    expiration_minutes: int = 120,
) -> str:
    """Genera un JWT con permisos de moderador para Jitsi Meet.

    Es un wrapper de generate_jitsi_token con is_moderator=True
    y features de moderador habilitadas por defecto.

    Args:
        user_id: UUID del usuario moderador
        room_name: Nombre de la sala
        user_name: Nombre del moderador
        user_email: Email del moderador (opcional)
        user_avatar: Avatar del moderador (opcional)
        expiration_minutes: Tiempo de expiración en minutos

    Returns:
        str: JWT firmado con permisos de moderador

    Example:
        >>> token = generate_moderator_token(
        ...     user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        ...     room_name="clase-matematicas-101",
        ...     user_name="Profesor García"
        ... )
    """
    # Features habilitadas para moderadores
    moderator_features = {
        "recording": True,  # Puede grabar
        "livestreaming": True,  # Puede hacer streaming
        "transcription": True,  # Puede activar transcripción
        "outbound-call": False,  # Llamadas salientes (si se necesita)
        "sip-outbound-call": False,  # SIP calls (si se necesita)
        "screen-sharing": True,  # Compartir pantalla
        "video-share": True,  # Compartir video
        "audio-mute": True,  # Silenciar audio
        "video-mute": True,  # Apagar cámara
        "kick-participant": True,  # Expulsar participantes
        "tile-view": True,  # Vista de mosaico
    }

    return generate_jitsi_token(
        user_id=user_id,
        room_name=room_name,
        user_name=user_name,
        user_email=user_email,
        user_avatar=user_avatar,
        is_moderator=True,
        expiration_minutes=expiration_minutes,
        features=moderator_features,
    )


def generate_participant_token(
    user_id: UUID,
    room_name: str,
    user_name: str,
    user_email: str | None = None,
    user_avatar: str | None = None,
    expiration_minutes: int = 120,
) -> str:
    """Genera un JWT para participante regular (no moderador) en Jitsi Meet.

    Es un wrapper de generate_jitsi_token con is_moderator=False
    y features básicas para participantes.

    Args:
        user_id: UUID del participante
        room_name: Nombre de la sala
        user_name: Nombre del participante
        user_email: Email del participante (opcional)
        user_avatar: Avatar del participante (opcional)
        expiration_minutes: Tiempo de expiración en minutos

    Returns:
        str: JWT firmado para participante regular

    Example:
        >>> token = generate_participant_token(
        ...     user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        ...     room_name="clase-matematicas-101",
        ...     user_name="Ana López"
        ... )
    """
    # Features básicas para participantes regulares
    participant_features = {
        "recording": False,  # No puede grabar
        "livestreaming": False,  # No puede hacer streaming
        "transcription": False,  # No puede activar transcripción
        "outbound-call": False,  # No puede hacer llamadas salientes
        "sip-outbound-call": False,  # No puede hacer SIP calls
        "screen-sharing": True,  # Puede compartir pantalla
        "video-share": True,  # Puede compartir video
        "audio-mute": True,  # Puede silenciar su audio
        "video-mute": True,  # Puede apagar su cámara
        "kick-participant": False,  # No puede expulsar
        "tile-view": True,  # Vista de mosaico
    }

    return generate_jitsi_token(
        user_id=user_id,
        room_name=room_name,
        user_name=user_name,
        user_email=user_email,
        user_avatar=user_avatar,
        is_moderator=False,
        expiration_minutes=expiration_minutes,
        features=participant_features,
    )


# ===============================
# Token Validation Functions
# ===============================


def decode_jitsi_token(token: str) -> dict[str, Any]:
    """Decodifica y valida un JWT de Jitsi.

    Args:
        token: JWT string a decodificar

    Returns:
        Dict: Payload del token decodificado

    Raises:
        jwt.ExpiredSignatureError: Si el token ha expirado
        jwt.InvalidTokenError: Si el token es inválido

    Example:
        >>> payload = decode_jitsi_token(token_str)
        >>> print(payload["room"])
        clase-matematicas-101
    """
    try:
        return jwt.decode(
            jwt=token,
            key=JITSI_APP_SECRET,
            algorithms=["HS256"],
            audience=JITSI_APP_ID,
            issuer=JITSI_APP_ID,
        )
    except jwt.ExpiredSignatureError:
        msg = "Token ha expirado"
        raise ValueError(msg) from None
    except jwt.InvalidTokenError as e:
        msg = f"Token inválido: {e!s}"
        raise ValueError(msg) from None


def validate_jitsi_token(token: str) -> bool:
    """Valida si un JWT de Jitsi es válido.

    Args:
        token: JWT string a validar

    Returns:
        bool: True si el token es válido, False en caso contrario

    Example:
        >>> is_valid = validate_jitsi_token(token_str)
        >>> if is_valid:
        ...     print("Token válido")
    """
    try:
        decode_jitsi_token(token)
        return True
    except (ValueError, jwt.InvalidTokenError):
        return False


def get_token_expiration(token: str) -> datetime | None:
    """Obtiene la fecha de expiración de un token JWT.

    Args:
        token: JWT string

    Returns:
        datetime or None: Fecha de expiración o None si el token es inválido

    Example:
        >>> expiration = get_token_expiration(token_str)
        >>> print(f"Expira en: {expiration}")
    """
    try:
        payload = decode_jitsi_token(token)
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp, tz=UTC)
        return None
    except (ValueError, jwt.InvalidTokenError):
        return None


def is_token_expired(token: str) -> bool:
    """Verifica si un token ha expirado.

    Args:
        token: JWT string

    Returns:
        bool: True si el token ha expirado, False en caso contrario

    Example:
        >>> if is_token_expired(token_str):
        ...     print("Token expirado, regenerar")
    """
    expiration = get_token_expiration(token)
    if expiration is None:
        return True  # Si no se puede obtener expiración, considerar expirado
    return now_utc() >= expiration


def get_token_room_name(token: str) -> str | None:
    """Extrae el nombre de la sala del token JWT.

    Args:
        token: JWT string

    Returns:
        str or None: Nombre de la sala o None si el token es inválido

    Example:
        >>> room = get_token_room_name(token_str)
        >>> print(f"Sala: {room}")
    """
    try:
        payload = decode_jitsi_token(token)
        return payload.get("room")
    except (ValueError, jwt.InvalidTokenError):
        return None


def get_token_user_id(token: str) -> str | None:
    """Extrae el user_id del token JWT.

    Args:
        token: JWT string

    Returns:
        str or None: User ID o None si el token es inválido

    Example:
        >>> user_id = get_token_user_id(token_str)
        >>> print(f"Usuario: {user_id}")
    """
    try:
        payload = decode_jitsi_token(token)
        return payload.get("context", {}).get("user", {}).get("id")
    except (ValueError, jwt.InvalidTokenError):
        return None


def is_moderator_token(token: str) -> bool:
    """Verifica si un token tiene permisos de moderador.

    Args:
        token: JWT string

    Returns:
        bool: True si es token de moderador, False en caso contrario

    Example:
        >>> if is_moderator_token(token_str):
        ...     print("Usuario es moderador")
    """
    try:
        payload = decode_jitsi_token(token)
        return payload.get("moderator", False)
    except (ValueError, jwt.InvalidTokenError):
        return False


# ===============================
# Token Refresh Functions
# ===============================


def refresh_jitsi_token(old_token: str, expiration_minutes: int = 120) -> str | None:
    """Genera un nuevo token basado en un token existente.

    Útil para extender sesiones sin requerir nuevos datos del usuario.

    Args:
        old_token: Token JWT existente
        expiration_minutes: Nuevo tiempo de expiración en minutos

    Returns:
        str or None: Nuevo JWT o None si el token original es inválido

    Example:
        >>> new_token = refresh_jitsi_token(old_token, expiration_minutes=60)
        >>> if new_token:
        ...     print("Token renovado exitosamente")
    """
    try:
        # Decodificar token existente
        payload = decode_jitsi_token(old_token)

        # Extraer información del usuario
        user_context = payload.get("context", {}).get("user", {})
        user_id_str = user_context.get("id")

        if not user_id_str:
            return None

        # Generar nuevo token con mismos datos pero nueva expiración
        return generate_jitsi_token(
            user_id=UUID(user_id_str),
            room_name=payload.get("room", ""),
            user_name=user_context.get("name", ""),
            user_email=user_context.get("email"),
            user_avatar=user_context.get("avatar"),
            is_moderator=payload.get("moderator", False),
            expiration_minutes=expiration_minutes,
            features=payload.get("context", {}).get("features"),
        )
    except (ValueError, jwt.InvalidTokenError):
        return None


# ===============================
# Utility Functions para Testing
# ===============================


def generate_test_token(
    room_name: str = "test-room",
    is_moderator: bool = False,
    expiration_minutes: int = 60,
) -> str:
    """Genera un token de prueba para testing/desarrollo.

    NO USAR EN PRODUCCIÓN - Solo para testing.

    Args:
        room_name: Nombre de sala de prueba
        is_moderator: Si es moderador
        expiration_minutes: Expiración

    Returns:
        str: JWT de prueba

    Example:
        >>> test_token = generate_test_token(room_name="test-math-class")
    """
    from uuid import uuid4

    return generate_jitsi_token(
        user_id=uuid4(),
        room_name=room_name,
        user_name="Test User",
        user_email="test@example.com",
        user_avatar="https://example.com/avatar.png",
        is_moderator=is_moderator,
        expiration_minutes=expiration_minutes,
    )


# ===============================
# Exports
# ===============================

__all__ = [
    # Validation functions
    "decode_jitsi_token",
    # Main generation functions
    "generate_jitsi_token",
    "generate_moderator_token",
    "generate_participant_token",
    # Testing utilities
    "generate_test_token",
    "get_token_expiration",
    "get_token_room_name",
    "get_token_user_id",
    "is_moderator_token",
    "is_token_expired",
    # Helper functions
    "now_utc",
    # Refresh functions
    "refresh_jitsi_token",
    "uuid_to_str",
    "validate_jitsi_token",
]
