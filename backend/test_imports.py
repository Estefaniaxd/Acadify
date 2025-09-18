#!/usr/bin/env python3
"""
Script para verificar que todas las importaciones funcionan correctamente
"""

def test_basic_imports():
    """Verificar importaciones básicas"""
    try:
        print("Verificando importaciones básicas...")
        
        print("✓ Importando config...")
        from src.core.config import get_settings
        settings = get_settings()
        print(f"  - Configuración cargada: {settings.PROJECT_NAME}")
        
        print("✓ Importando security...")
        from src.utils.security import security_manager
        print("  - SecurityManager disponible")
        
        print("✓ Importando auth_service...")
        from src.services.auth.auth_service import AuthService
        print("  - AuthService disponible")
        
        print("✓ Importando deps...")
        from src.api.deps import get_db
        print("  - Dependencias de DB disponibles")
        
        print("✓ Importando schemas...")
        from src.schemas.auth.auth_schemas import LoginRequest
        print("  - Schemas de autenticación disponibles")
        
        print("\n✅ Todas las importaciones funcionan correctamente!")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_redis_config():
    """Verificar configuración de Redis"""
    try:
        print("\nVerificando configuración de Redis...")
        from src.core.config import get_settings
        settings = get_settings()
        
        print(f"  - REDIS_HOST: {settings.REDIS_HOST}")
        print(f"  - REDIS_PORT: {settings.REDIS_PORT}")
        print(f"  - REDIS_DB: {settings.REDIS_DB}")
        print(f"  - REDIS_URL: {settings.REDIS_URL}")
        
        return True
    except Exception as e:
        print(f"❌ Error en configuración Redis: {e}")
        return False

def test_database_config():
    """Verificar configuración de base de datos"""
    try:
        print("\nVerificando configuración de base de datos...")
        from src.core.config import get_settings
        settings = get_settings()
        
        print(f"  - POSTGRES_HOST: {settings.POSTGRES_HOST}")
        print(f"  - POSTGRES_PORT: {settings.POSTGRES_PORT}")
        print(f"  - POSTGRES_DB: {settings.POSTGRES_DB}")
        print(f"  - DATABASE_URL: {settings.DATABASE_URL}")
        
        return True
    except Exception as e:
        print(f"❌ Error en configuración DB: {e}")
        return False

if __name__ == "__main__":
    print("=== VERIFICACIÓN DE CONFIGURACIÓN ACADIFY ===\n")
    
    success = True
    
    success &= test_basic_imports()
    success &= test_redis_config()
    success &= test_database_config()
    
    if success:
        print(f"\n🎉 ¡Todas las verificaciones pasaron! El sistema está listo.")
        print("\nPara iniciar el servidor:")
        print("  uvicorn src.main:app --reload")
        print("\nPara acceder a la documentación:")
        print("  http://127.0.0.1:8000/docs")
    else:
        print(f"\n💥 Hay problemas de configuración. Revisa los errores arriba.")
        exit(1)