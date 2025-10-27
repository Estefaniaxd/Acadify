#!/usr/bin/env python3
"""
Script para generar tokens de acceso para pruebas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import jwt
from datetime import datetime, timedelta
from uuid import UUID
from src.core.config import settings

# Usar la SECRET_KEY real del settings
JWT_SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = "HS256"

def get_user_info(email: str) -> dict:
    """Obtener información del usuario por email (simulado)"""
    # Usar usuarios reales de la base de datos
    users = {
        "estudiante@example.com": {
            "usuario_id": "69938ad1-1b07-4fa2-b2ce-741ba9706f23",  # estefania londono
            "email": "estefania@arp.edu.co",
            "nombres": "Estefania",
            "apellidos": "Londono",
            "rol": "estudiante"
        },
        "docente@example.com": {
            "usuario_id": "9d72cebb-4ae2-4d80-ad22-286b027a76bc",  # juan martinez
            "email": "juanitomm2408@gmail.com", 
            "nombres": "Juan",
            "apellidos": "Martinez",
            "rol": "docente"
        }
    }
    
    return users.get(email, users["estudiante@example.com"])

def generate_access_token(user_info: dict) -> str:
    """Generar token de acceso JWT"""
    payload = {
        "sub": str(user_info["usuario_id"]),
        "email": user_info["email"],
        "nombres": user_info["nombres"],
        "apellidos": user_info["apellidos"],
        "type": "access",  # Campo requerido
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

if __name__ == "__main__":
    # Generar token para estudiante por defecto
    user_info = get_user_info("estudiante@example.com")
    token = generate_access_token(user_info)
    print(f"Token generado para {user_info['email']}:")
    print(token)