#!/usr/bin/env python3
"""
Script para generar token de prueba para testing de endpoints
"""

import jwt
from datetime import datetime, timedelta
import os
import sys
sys.path.append('/home/esteban/Acadify/backend')

# Configuración JWT (debe coincidir con la configuración del backend)
SECRET_KEY = "your-secret-key-here-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_test_token():
    """Crear token de prueba"""
    
    # Datos del usuario de prueba
    token_data = {
        "sub": "test@example.com",  # email del usuario
        "usuario_id": "123e4567-e89b-12d3-a456-426614174000",  # UUID de ejemplo
        "email": "test@example.com",
        "nombres": "Usuario",
        "apellidos": "De Prueba",
        "tipo_usuario": "estudiante",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
        "tipo": "access"
    }
    
    # Crear el token
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    print(f"🔑 Token de prueba generado:")
    print(f"Bearer {token}")
    print(f"")
    print(f"📋 Datos del token:")
    print(f"- Usuario ID: {token_data['usuario_id']}")
    print(f"- Email: {token_data['email']}")
    print(f"- Nombre: {token_data['nombres']} {token_data['apellidos']}")
    print(f"- Tipo: {token_data['tipo_usuario']}")
    print(f"- Expira: {token_data['exp']}")
    
    # Guardar en archivo para uso en scripts
    with open('/tmp/test_token.txt', 'w') as f:
        f.write(token)
    
    print(f"")
    print(f"💾 Token guardado en /tmp/test_token.txt")
    print(f"")
    print(f"🧪 Ejemplo de uso con curl:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/temp/comentarios/1')
    
    return token

if __name__ == "__main__":
    create_test_token()