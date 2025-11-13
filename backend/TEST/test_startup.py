#!/usr/bin/env python3
"""
Script de prueba para verificar que todos los servicios están funcionando correctamente.
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Prueba la conexión a la base de datos PostgreSQL"""
    print("🔍 Probando conexión a PostgreSQL...")
    try:
        from sqlalchemy import create_engine, text
        from src.core.config import settings
        
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"   ✅ PostgreSQL conectado: {version.split(',')[0]}")
            
            # Verificar que las tablas existen
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'"
            ))
            table_count = result.fetchone()[0]
            print(f"   ✅ Tablas en la base de datos: {table_count}")
        return True
    except Exception as e:
        print(f"   ❌ Error conectando a PostgreSQL: {e}")
        return False

def test_redis():
    """Prueba la conexión a Redis"""
    print("🔍 Probando conexión a Redis...")
    try:
        import redis
        from src.core.config import settings
        
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        if r.ping():
            print(f"   ✅ Redis conectado: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
            # Probar set/get
            test_key = "test:startup"
            r.set(test_key, "OK", ex=10)
            value = r.get(test_key)
            if value:
                print(f"   ✅ Redis set/get funcionando correctamente")
                r.delete(test_key)
            return True
    except Exception as e:
        print(f"   ❌ Error conectando a Redis: {e}")
        return False

def test_imports():
    """Prueba que todas las importaciones críticas funcionen"""
    print("🔍 Probando importaciones críticas...")
    try:
        from src.main import app
        print("   ✅ FastAPI app importada correctamente")
        
        from src.core.config import settings
        print("   ✅ Settings cargados correctamente")
        
        from src.models import Usuario
        print("   ✅ Modelos importados correctamente")
        
        return True
    except Exception as e:
        print(f"   ❌ Error en importaciones: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """Verifica las variables de entorno críticas"""
    print("🔍 Verificando variables de entorno...")
    try:
        from src.core.config import settings
        
        checks = {
            "DATABASE_URL": bool(settings.DATABASE_URL or settings.database_url),
            "SECRET_KEY": bool(settings.SECRET_KEY),
            "REDIS_HOST": bool(settings.REDIS_HOST),
            "REDIS_PORT": bool(settings.REDIS_PORT),
        }
        
        all_ok = True
        for key, value in checks.items():
            status = "✅" if value else "❌"
            print(f"   {status} {key}: {'OK' if value else 'NO CONFIGURADO'}")
            if not value:
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"   ❌ Error verificando entorno: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("🚀 ACADIFY - TEST DE INICIO DEL SISTEMA")
    print("="*60 + "\n")
    
    results = {
        "Entorno": test_environment(),
        "Importaciones": test_imports(),
        "PostgreSQL": test_database(),
        "Redis": test_redis(),
    }
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("="*60 + "\n")
    
    if all_passed:
        print("🎉 Todos los servicios están funcionando correctamente!")
        print("💡 Puedes iniciar el servidor con:")
        print("   uvicorn src.main:app --reload")
        return 0
    else:
        print("⚠️  Algunos servicios tienen problemas. Revisa los errores arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
