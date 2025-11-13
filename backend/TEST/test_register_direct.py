#!/usr/bin/env python3
"""
Test directo del servicio de registro
"""
import asyncio
from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.services.auth.auth_service import AuthService
from src.schemas.users.usuario import UsuarioCreate
from src.enums.users.usuario_enums import RolUsuario

async def test_register():
    db = SessionLocal()
    
    # Crear redis client
    from src.core.redis_manager import redis_manager
    redis_client = await redis_manager.get_redis()
    
    auth_service = AuthService(redis_client)
    
    user_data = UsuarioCreate(
        correo_institucional="test.direct@universidad.edu.co",
        nombres="TestDirect",
        apellidos="User",
        tipo_documento="CC",
        numero_documento="11223399",
        password="TestPassword123!",
        rol=RolUsuario.estudiante
    )
    
    try:
        print("🔄 Intentando registrar usuario...")
        new_user = await auth_service.register_user(db, user_data)
        print(f"✅ Usuario registrado: {new_user.usuario_id}")
        print(f"   Nombre: {new_user.nombres} {new_user.apellidos}")
        print(f"   Email: {new_user.correo_institucional}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_register())
