#!/usr/bin/env python3
"""
Script para probar el endpoint de login del backend directamente
"""
import asyncio
import sys
sys.path.append('/home/esteban/Acadify/backend')

from src.db.session import SessionLocal
from src.services.auth.auth_service import AuthService
from src.schemas.auth.auth_schemas import LoginRequest
from src.services.auth.redis_service import RedisService
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_login():
    """Probar login directamente con el AuthService"""
    # Conectar a Redis
    redis_service = RedisService()
    redis_service.connect()
    redis_client = redis_service.redis
    
    # Crear AuthService
    auth_service = AuthService(redis_client)
    
    # Crear sesión de DB
    db = SessionLocal()
    
    try:
        # Probar login con usuario administrador
        login_data = LoginRequest(
            identifier="admin@test.com",  # Email que agregamos
            password="admin123"           # Verificar si este es el password correcto
        )
        
        logger.info("Probando login con admin@test.com...")
        result = await auth_service.authenticate_user(db, login_data)
        
        logger.info(f"Login exitoso! Resultado: {result}")
        return True
        
    except Exception as e:
        logger.error(f"Error en login: {e}")
        
        # Probar con username directamente
        try:
            login_data = LoginRequest(
                identifier="esteban",  # Username original
                password="admin123"
            )
            
            logger.info("Probando login con username esteban...")
            result = await auth_service.authenticate_user(db, login_data)
            
            logger.info(f"Login exitoso con username! Resultado: {result}")
            return True
            
        except Exception as e2:
            logger.error(f"Error en login con username: {e2}")
            return False
        
    finally:
        db.close()
        redis_service.disconnect()

if __name__ == "__main__":
    success = asyncio.run(test_login())
    if success:
        print("✅ Login funciona correctamente")
    else:
        print("❌ Login no funciona")