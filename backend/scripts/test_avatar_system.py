#!/usr/bin/env python3
"""
Script de pruebas rápidas para el sistema de avatares.
Verifica endpoints, cache Redis y base de datos.
"""

import os
import sys
import asyncio
import json
import requests
from pathlib import Path

# Añadir el directorio src al path para importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.config import settings
from src.db.session import SessionLocal
from src.services.avatar_service import avatar_service


class AvatarSystemTester:
    """Tester para el sistema de avatares."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Inicializa el tester.
        
        Args:
            base_url: URL base del API
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1/avatar"
        self.auth_token = None
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Registra resultado de prueba."""
        result = {
            'test': test_name,
            'success': success,
            'details': details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
    
    def test_redis_connection(self):
        """Prueba conexión a Redis."""
        try:
            avatar_service.connect_redis()
            if avatar_service.redis:
                avatar_service.redis.ping()
                self.log_test("Redis Connection", True, "Connected successfully")
            else:
                self.log_test("Redis Connection", False, "No Redis instance")
        except Exception as e:
            self.log_test("Redis Connection", False, f"Error: {e}")
    
    def test_database_connection(self):
        """Prueba conexión a base de datos."""
        try:
            db = SessionLocal()
            # Hacer una query simple
            result = db.execute("SELECT 1").fetchone()
            db.close()
            
            if result:
                self.log_test("Database Connection", True, "Connected successfully")
            else:
                self.log_test("Database Connection", False, "No result from query")
        except Exception as e:
            self.log_test("Database Connection", False, f"Error: {e}")
    
    def test_assets_directory(self):
        """Prueba directorio de assets."""
        try:
            assets_dir = Path(settings.AVATAR_ASSETS_PATH)
            
            if not assets_dir.exists():
                self.log_test("Assets Directory", False, f"Directory not found: {assets_dir}")
                return
            
            # Contar archivos por categoría
            categories = {}
            for category_path in assets_dir.iterdir():
                if category_path.is_dir() and not category_path.name.startswith('.'):
                    png_files = list(category_path.glob('*.png'))
                    categories[category_path.name] = len(png_files)
            
            total_files = sum(categories.values())
            details = f"Found {len(categories)} categories, {total_files} total files"
            
            if total_files > 0:
                self.log_test("Assets Directory", True, details)
            else:
                self.log_test("Assets Directory", False, "No PNG files found")
                
        except Exception as e:
            self.log_test("Assets Directory", False, f"Error: {e}")
    
    def test_manifest_endpoint(self):
        """Prueba endpoint de manifest."""
        try:
            url = f"{self.api_url}/assets"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                categories = data.get('categories', {})
                total_assets = data.get('total_assets', 0)
                
                details = f"Status: {response.status_code}, Categories: {len(categories)}, Assets: {total_assets}"
                self.log_test("Manifest Endpoint", True, details)
            else:
                self.log_test("Manifest Endpoint", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Manifest Endpoint", False, f"Error: {e}")
    
    def test_preview_endpoint(self):
        """Prueba endpoint de preview (sin auth)."""
        try:
            url = f"{self.api_url}/preview"
            
            # Payload de prueba simple
            payload = {
                "layers": [
                    {"category": "base", "file": "base/base_001.png"}
                ]
            }
            
            response = requests.post(
                url, 
                json=payload, 
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                preview_url = data.get('preview_url', '')
                from_cache = data.get('from_cache', False)
                
                details = f"Status: {response.status_code}, URL: {preview_url[:50]}..., Cache: {from_cache}"
                self.log_test("Preview Endpoint", True, details)
            elif response.status_code == 400:
                # Error esperado si no hay assets
                details = f"Status: {response.status_code} (expected if no assets)"
                self.log_test("Preview Endpoint", True, details)
            else:
                details = f"Status: {response.status_code}, Error: {response.text}"
                self.log_test("Preview Endpoint", False, details)
                
        except Exception as e:
            self.log_test("Preview Endpoint", False, f"Error: {e}")
    
    def test_authenticated_endpoints(self):
        """Prueba endpoints que requieren autenticación."""
        try:
            # Intentar acceder sin autenticación
            url = f"{self.api_url}/me"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 401:
                self.log_test("Auth Protection", True, "401 Unauthorized as expected")
            else:
                self.log_test("Auth Protection", False, f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Auth Protection", False, f"Error: {e}")
    
    def test_cache_functionality(self):
        """Prueba funcionalidad de cache."""
        try:
            if not avatar_service.redis:
                self.log_test("Cache Functionality", False, "Redis not available")
                return
            
            # Probar operaciones básicas de cache
            test_key = "avatar_test:test_key"
            test_value = "test_value"
            
            # Set
            avatar_service.redis.setex(test_key, 60, test_value)
            
            # Get
            cached_value = avatar_service.redis.get(test_key)
            
            # Clean up
            avatar_service.redis.delete(test_key)
            
            if cached_value and cached_value.decode('utf-8') == test_value:
                self.log_test("Cache Functionality", True, "Redis set/get working")
            else:
                self.log_test("Cache Functionality", False, "Cache value mismatch")
                
        except Exception as e:
            self.log_test("Cache Functionality", False, f"Error: {e}")
    
    def test_configuration(self):
        """Prueba configuración del sistema."""
        config_tests = [
            ("AVATAR_ASSETS_PATH", settings.AVATAR_ASSETS_PATH),
            ("AVATAR_STORAGE_PATH", settings.AVATAR_STORAGE_PATH),
            ("AVATAR_ASSETS_BASE_URL", settings.AVATAR_ASSETS_BASE_URL),
            ("REDIS_URL", settings.REDIS_URL),
            ("DATABASE_URL", settings.DATABASE_URL[:20] + "..."),
        ]
        
        missing_configs = []
        for name, value in config_tests:
            if not value:
                missing_configs.append(name)
        
        if missing_configs:
            details = f"Missing: {', '.join(missing_configs)}"
            self.log_test("Configuration", False, details)
        else:
            self.log_test("Configuration", True, "All config values present")
    
    def generate_report(self):
        """Genera reporte final."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("AVATAR SYSTEM TEST REPORT")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("="*60)
        
        return failed_tests == 0


async def main():
    """Función principal."""
    print("=== Avatar System Quick Test ===")
    print(f"API Base URL: http://localhost:8000")
    print(f"Assets Path: {settings.AVATAR_ASSETS_PATH}")
    print(f"Redis URL: {settings.REDIS_URL}")
    print()
    
    tester = AvatarSystemTester()
    
    # Ejecutar pruebas
    print("Running tests...")
    print("-" * 40)
    
    tester.test_configuration()
    tester.test_redis_connection()
    tester.test_database_connection()
    tester.test_assets_directory()
    tester.test_manifest_endpoint()
    tester.test_preview_endpoint()
    tester.test_authenticated_endpoints()
    tester.test_cache_functionality()
    
    # Generar reporte
    success = tester.generate_report()
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())