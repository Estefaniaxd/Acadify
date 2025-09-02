# backend/app/utils/helpers.py
import uuid
import hashlib
import secrets
import re
from typing import Optional


# -------------------------------
# Generación de UUID
# -------------------------------

def generate_uuid() -> str:
    """
    Genera un UUID v4 como string.

    Returns:
        str: UUID único en formato estándar.
    """
    return str(uuid.uuid4())


# -------------------------------
# Sanitización de strings
# -------------------------------

def sanitize_input(value: Optional[str], max_length: int = 255) -> str:
    """
    Sanitiza cadenas de texto eliminando caracteres potencialmente peligrosos
    y recortando la longitud a max_length.

    Args:
        value (str | None): Texto a sanitizar.
        max_length (int): Longitud máxima permitida.

    Returns:
        str: Texto limpio y recortado.
    
    Justificación:
        Evita inyecciones básicas de HTML/JS y protege logs o base de datos.
    """
    if not value:
        return ""
    sanitized = re.sub(r'[<>;"\'%]', '', value)
    return sanitized[:max_length]


# -------------------------------
# Hashing seguro de contraseñas
# -------------------------------

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando SHA256 con salt aleatorio.

    Args:
        password (str): Contraseña en texto plano.

    Returns:
        str: Hash seguro en formato "salt$hash".

    Justificación:
        SHA256 + salt previene ataques de rainbow tables y garantiza unicidad.
        Para producción, se recomienda usar librerías como 'passlib' o 'bcrypt'.
    """
    salt = secrets.token_hex(16)  # 32 caracteres hexadecimales
    hash_obj = hashlib.sha256(f"{salt}{password}".encode('utf-8'))
    return f"{salt}${hash_obj.hexdigest()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña coincide con el hash almacenado.

    Args:
        password (str): Contraseña ingresada por el usuario.
        hashed_password (str): Hash almacenado (salt$hash).

    Returns:
        bool: True si coincide, False en caso contrario.
    """
    try:
        salt, hash_val = hashed_password.split("$")
        hash_obj = hashlib.sha256(f"{salt}{password}".encode('utf-8'))
        return hash_obj.hexdigest() == hash_val
    except Exception:
        return False


# -------------------------------
# Generación de tokens aleatorios seguros
# -------------------------------

def generate_random_token(length: int = 32) -> str:
    """
    Genera un token aleatorio seguro en formato hexadecimal.

    Args:
        length (int): Longitud del token en bytes (default=32, resultado=64 hex chars).

    Returns:
        str: Token seguro hexadecimal.
    
    Justificación:
        Útil para tokens de sesión, recuperación de contraseñas, OAuth, etc.
    """
    return secrets.token_hex(length)


# -------------------------------
# Funciones adicionales útiles
# -------------------------------

def generate_short_uuid() -> str:
    """
    Genera un UUID corto (8 caracteres) para uso interno o referencia rápida.

    Returns:
        str: UUID corto.
    
    Justificación:
        Para casos donde no necesitamos un UUID completo, como IDs temporales o referencias visibles.
    """
    return uuid.uuid4().hex[:8].upper()
