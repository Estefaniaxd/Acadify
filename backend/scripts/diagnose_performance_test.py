#!/usr/bin/env python3
"""
Script de diagnóstico para troubleshooting de performance test.

Verifica:
1. Database connection
2. Auth endpoint
3. Endpoints existence
"""

import sys
import requests
from pathlib import Path

# Agregar backend al path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from src.core.config import settings

def check_database():
    """Verificar configuración de base de datos"""
    print("🔍 Verificando Database Configuration...")
    print(f"   DATABASE_URL from config: {settings.database_url[:50]}...")
    print(f"   POSTGRES_USER: {settings.POSTGRES_USER}")
    print(f"   POSTGRES_DB: {settings.POSTGRES_DB}")
    
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✅ Database connection: OK")
            return True
    except Exception as e:
        print(f"   ❌ Database connection FAILED: {e}")
        return False

def check_auth_endpoint():
    """Verificar endpoint de autenticación"""
    print("\n🔍 Verificando Auth Endpoint...")
    
    endpoints_to_try = [
        ("POST", "/api/auth/login"),
        ("POST", "/auth/login"),
        ("POST", "/api/token"),
        ("POST", "/token"),
    ]
    
    for method, path in endpoints_to_try:
        try:
            url = f"http://localhost:8000{path}"
            response = requests.request(
                method,
                url,
                json={"identifier": "test", "password": "test"},
                timeout=2
            )
            print(f"   {method} {path}: {response.status_code}")
            if response.status_code not in [404, 405]:
                print(f"      ✅ Endpoint encontrado!")
                print(f"      Response: {response.text[:100]}")
                return True
        except Exception as e:
            print(f"   {method} {path}: Error - {str(e)[:50]}")
    
    return False

def check_endpoints():
    """Verificar endpoints principales"""
    print("\n🔍 Verificando Endpoints Principales...")
    
    endpoints = [
        ("GET", "/api/cursos/"),
        ("GET", "/api/instituciones/"),
        ("GET", "/api/users/me/perfil"),
        ("GET", "/docs"),
    ]
    
    for method, path in endpoints:
        try:
            url = f"http://localhost:8000{path}"
            response = requests.request(method, url, timeout=2)
            status_icon = "✅" if response.status_code < 500 else "❌"
            print(f"   {status_icon} {method} {path}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {method} {path}: {str(e)[:50]}")

def check_openapi():
    """Obtener lista completa de endpoints"""
    print("\n🔍 Obteniendo lista de endpoints desde OpenAPI...")
    try:
        response = requests.get("http://localhost:8000/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            paths = data.get("paths", {})
            print(f"   ✅ Total endpoints en OpenAPI: {len(paths)}")
            
            # Mostrar endpoints de auth
            auth_endpoints = [p for p in paths.keys() if "auth" in p.lower() or "login" in p.lower()]
            if auth_endpoints:
                print(f"\n   📋 Auth endpoints encontrados:")
                for path in auth_endpoints:
                    methods = list(paths[path].keys())
                    print(f"      - {path}: {', '.join(methods).upper()}")
            
            return True
        else:
            print(f"   ❌ OpenAPI no disponible: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error obteniendo OpenAPI: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 Diagnóstico de Performance Test - Acadify API")
    print("=" * 60)
    
    results = {
        "database": check_database(),
        "auth": check_auth_endpoint(),
        "endpoints": True,  # Solo informativo
        "openapi": check_openapi()
    }
    
    print("\n" + "=" * 60)
    print("📊 Resumen")
    print("=" * 60)
    
    for check, result in results.items():
        icon = "✅" if result else "❌"
        print(f"   {icon} {check.capitalize()}: {'OK' if result else 'FAILED'}")
    
    check_endpoints()
    
    if not all(results.values()):
        print("\n⚠️  Hay problemas de configuración que deben corregirse.")
        print("   Ver PERFORMANCE_TEST_RESULTS.md para soluciones detalladas.")
        sys.exit(1)
    else:
        print("\n✅ Sistema listo para performance testing!")
        sys.exit(0)

if __name__ == "__main__":
    main()
