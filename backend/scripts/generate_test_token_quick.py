"""
Script rápido para generar un token JWT de prueba para testing.

Este script genera un token válido usando el generador de tokens
del sistema de autenticación existente.

Ejecutar:
    python scripts/generate_test_token_quick.py
"""

import sys
from pathlib import Path

# Añadir directorio raíz al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import datetime, timedelta, timezone
from uuid import uuid4
import jwt

from src.core.config import get_settings

settings = get_settings()


def generate_test_access_token(
    user_id: str = None,
    nombre: str = "Test",
    apellido: str = "User",
    email: str = "test@acadify.com",
    role: str = "docente",
    expires_hours: int = 24
) -> str:
    """
    Genera un token de acceso de prueba.
    
    Args:
        user_id: UUID del usuario (genera uno nuevo si no se especifica)
        nombre: Nombre del usuario
        apellido: Apellido del usuario
        email: Email del usuario
        role: Rol del usuario
        expires_hours: Horas de validez del token
        
    Returns:
        str: Token JWT
    """
    if user_id is None:
        user_id = str(uuid4())
    
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=expires_hours)
    
    payload = {
        "sub": user_id,
        "name": nombre,
        "last_name": apellido,
        "email": email,
        "test_user": True,
        "role": role,
        "type": "access",
        "exp": int(expires.timestamp()),
        "iat": int(now.timestamp()),
        "jti": f"{user_id}-{int(now.timestamp())}"
    }
    
    token = jwt.encode(
        payload=payload,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return token


def main():
    """Genera y muestra token de prueba"""
    print("=" * 70)
    print("🔑 GENERADOR DE TOKEN DE PRUEBA")
    print("=" * 70)
    
    print("\n📝 Generando token de prueba...")
    print(f"   - Rol: docente")
    print(f"   - Validez: 24 horas")
    print(f"   - Email: test@acadify.com")
    
    token = generate_test_access_token()
    
    print("\n✅ Token generado exitosamente!")
    print("\n" + "=" * 70)
    print("TOKEN JWT:")
    print("=" * 70)
    print(token)
    print("=" * 70)
    
    # Guardar en archivo
    token_file = backend_dir / "TEST" / "test_token.txt"
    token_file.parent.mkdir(exist_ok=True)
    token_file.write_text(token)
    
    print(f"\n💾 Token guardado en: {token_file}")
    print("\n💡 Uso:")
    print("   1. Copia el token de arriba")
    print("   2. Úsalo en headers HTTP:")
    print(f'      Authorization: Bearer {token[:30]}...')
    print("\n   O simplemente ejecuta test_videollamadas_endpoints.py")
    print("   que lo cargará automáticamente desde el archivo.")


if __name__ == "__main__":
    main()
