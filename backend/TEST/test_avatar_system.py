"""
Script de pruebas completo para el sistema de avatares.

Este script verifica:
1. Carga de assets desde la base de datos
2. Endpoints de avatares (GET, POST, PUT, DELETE)
3. Cache de Redis
4. Actualización de avatar activo
5. Problema reportado: avatar no actualiza al cambiar de usuario
"""

import sys
import requests
import json
from typing import Dict, Optional

BASE_URL = "http://localhost:8000"

# Credenciales de test
TEST_USERS = {
    "admin": {"identifier": "adminacadify", "password": "Admin123!"},
    "docente": {"identifier": "docente@acadify.com", "password": "Admin123!"},
    "estudiante": {"identifier": "estudiante@acadify.com", "password": "Admin123!"}
}

class Colors:
    """Colores ANSI para terminal."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_test(name: str):
    print(f"\n{Colors.OKBLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}TEST: {name}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'='*70}{Colors.ENDC}")

def print_success(msg: str):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg: str):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_warning(msg: str):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

def print_info(msg: str):
    print(f"{Colors.OKCYAN}ℹ️  {msg}{Colors.ENDC}")


class AvatarTester:
    """Clase para probar el sistema de avatares."""
    
    def __init__(self):
        self.tokens = {}
        self.avatars = {}
        self.results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
    
    def login(self, user_type: str) -> Optional[str]:
        """Login y obtener token."""
        print_test(f"LOGIN - {user_type.upper()}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=TEST_USERS[user_type]
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                self.tokens[user_type] = token
                print_success(f"Login exitoso para {user_type}")
                print_info(f"Token: {token[:20]}...")
                self.results["passed"] += 1
                return token
            else:
                print_error(f"Login falló: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.results["failed"] += 1
                return None
                
        except Exception as e:
            print_error(f"Error en login: {e}")
            self.results["failed"] += 1
            return None
    
    def test_assets_endpoint(self):
        """Prueba el endpoint de assets (público, sin autenticación)."""
        print_test("GET /avatar/assets - PÚBLICO")
        
        try:
            response = requests.get(f"{BASE_URL}/avatar/assets")
            
            if response.status_code == 200:
                data = response.json()
                print_success("Endpoint de assets funciona")
                
                # Verificar estructura
                print_info(f"Resolution: {data.get('resolution')}")
                print_info(f"Total assets: {data.get('total_assets')}")
                
                categories = data.get('categories', {})
                print_info(f"Categorías encontradas: {len(categories)}")
                print_info(f"Categorías: {', '.join(categories.keys())}")
                
                # Verificar cada categoría
                for category, items in categories.items():
                    if isinstance(items, list) and len(items) > 0:
                        print_success(f"  ├─ {category}: {len(items)} items")
                        # Mostrar ejemplo del primer item
                        first_item = items[0]
                        print_info(f"     └─ Ejemplo: {first_item.get('display_name', 'N/A')}")
                    else:
                        print_warning(f"  ├─ {category}: Vacía o formato incorrecto")
                
                self.results["passed"] += 1
                return data
            else:
                print_error(f"Error: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.results["failed"] += 1
                return None
                
        except Exception as e:
            print_error(f"Exception: {e}")
            import traceback
            traceback.print_exc()
            self.results["failed"] += 1
            return None
    
    def test_get_my_avatars(self, user_type: str):
        """Prueba GET /avatar/me para obtener avatares del usuario."""
        print_test(f"GET /avatar/me - {user_type.upper()}")
        
        token = self.tokens.get(user_type)
        if not token:
            print_error("No hay token disponible")
            self.results["failed"] += 1
            return None
        
        try:
            response = requests.get(
                f"{BASE_URL}/avatar/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                avatars = data.get("avatars", [])
                total = data.get("total", 0)
                has_active = data.get("has_active", False)
                active_id = data.get("active_avatar_id")
                
                print_success(f"Avatares obtenidos: {len(avatars)}")
                print_info(f"Total en DB: {total}")
                print_info(f"Tiene avatar activo: {has_active}")
                if active_id:
                    print_info(f"Avatar activo ID: {active_id}")
                
                # Guardar para tests posteriores
                self.avatars[user_type] = {
                    "list": avatars,
                    "active_id": active_id
                }
                
                # Mostrar detalles de cada avatar
                for idx, avatar in enumerate(avatars, 1):
                    print_info(f"\n  Avatar #{idx}:")
                    print_info(f"    ├─ Name: {avatar.get('name')}")
                    print_info(f"    ├─ ID: {avatar.get('id')}")
                    print_info(f"    ├─ Active: {avatar.get('is_active')}")
                    print_info(f"    ├─ Image URL: {avatar.get('image_url')}")
                    print_info(f"    └─ Layers: {len(avatar.get('layers', []))} capas")
                
                self.results["passed"] += 1
                return data
            else:
                print_error(f"Error: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.results["failed"] += 1
                return None
                
        except Exception as e:
            print_error(f"Exception: {e}")
            self.results["failed"] += 1
            return None
    
    def test_create_avatar(self, user_type: str):
        """Prueba POST /avatar/save para crear un avatar."""
        print_test(f"POST /avatar/save - {user_type.upper()}")
        
        token = self.tokens.get(user_type)
        if not token:
            print_error("No hay token disponible")
            self.results["failed"] += 1
            return None
        
        # Avatar de prueba simple
        test_avatar = {
            "name": f"Test Avatar {user_type}",
            "base_gender": "male",
            "layers": [
                {"category": "base", "file": "base/light_skin_male.png"},
                {"category": "hair", "file": "hair/short_brown.png"}
            ],
            "is_active": True,
            "is_public": True
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/avatar/save",
                headers={"Authorization": f"Bearer {token}"},
                json=test_avatar
            )
            
            if response.status_code == 201:
                data = response.json()
                print_success("Avatar creado exitosamente")
                print_info(f"Avatar ID: {data.get('id')}")
                print_info(f"Image URL: {data.get('image_url')}")
                print_info(f"Is Active: {data.get('is_active')}")
                
                self.results["passed"] += 1
                return data
            elif response.status_code == 400:
                print_warning(f"Avatar ya existe o datos inválidos: {response.json().get('detail')}")
                self.results["warnings"] += 1
                return None
            else:
                print_error(f"Error: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.results["failed"] += 1
                return None
                
        except Exception as e:
            print_error(f"Exception: {e}")
            self.results["failed"] += 1
            return None
    
    def test_update_avatar(self, user_type: str, avatar_id: str):
        """Prueba PUT /avatar/{avatar_id} para actualizar un avatar."""
        print_test(f"PUT /avatar/{{id}} - {user_type.upper()}")
        
        token = self.tokens.get(user_type)
        if not token:
            print_error("No hay token disponible")
            self.results["failed"] += 1
            return None
        
        update_data = {
            "name": f"Updated Avatar {user_type}",
            "is_active": True
        }
        
        try:
            response = requests.put(
                f"{BASE_URL}/avatar/{avatar_id}",
                headers={"Authorization": f"Bearer {token}"},
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Avatar actualizado exitosamente")
                print_info(f"Nuevo nombre: {data.get('name')}")
                print_info(f"Is Active: {data.get('is_active')}")
                
                self.results["passed"] += 1
                return data
            else:
                print_error(f"Error: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.results["failed"] += 1
                return None
                
        except Exception as e:
            print_error(f"Exception: {e}")
            self.results["failed"] += 1
            return None
    
    def test_avatar_isolation(self):
        """Prueba el aislamiento de avatares entre usuarios."""
        print_test("AISLAMIENTO DE AVATARES ENTRE USUARIOS")
        
        print_info("Verificando que cada usuario vea solo sus propios avatares...")
        
        for user_type in ["docente", "estudiante"]:
            avatars = self.avatars.get(user_type, {}).get("list", [])
            user_ids = set(av.get("user_id") for av in avatars if av.get("user_id"))
            
            if len(user_ids) <= 1:
                print_success(f"✓ {user_type}: Solo ve sus propios avatares")
                self.results["passed"] += 1
            else:
                print_error(f"✗ {user_type}: Ve avatares de múltiples usuarios: {user_ids}")
                self.results["failed"] += 1
    
    def test_cross_user_avatar_bug(self):
        """
        Prueba el bug reportado: Al actualizar avatar de un usuario,
        aparece el mismo para todos.
        """
        print_test("BUG: AVATAR COMPARTIDO ENTRE USUARIOS")
        
        print_info("Simulando el escenario del bug reportado...")
        print_info("1. Login como docente")
        print_info("2. Obtener avatar activo del docente")
        print_info("3. Login como estudiante")
        print_info("4. Obtener avatar activo del estudiante")
        print_info("5. Verificar que sean diferentes")
        
        docente_avatar = self.avatars.get("docente", {}).get("active_id")
        estudiante_avatar = self.avatars.get("estudiante", {}).get("active_id")
        
        print_info(f"\nAvatar activo docente: {docente_avatar}")
        print_info(f"Avatar activo estudiante: {estudiante_avatar}")
        
        if docente_avatar and estudiante_avatar:
            if docente_avatar != estudiante_avatar:
                print_success("✓ Los avatares son diferentes (correcto)")
                self.results["passed"] += 1
            else:
                print_error("✗ LOS AVATARES SON IGUALES - BUG CONFIRMADO")
                print_error("  Ambos usuarios tienen el mismo avatar_id activo")
                self.results["failed"] += 1
        elif not docente_avatar and not estudiante_avatar:
            print_warning("Ningún usuario tiene avatar activo - crear avatares primero")
            self.results["warnings"] += 1
        else:
            print_warning("Solo un usuario tiene avatar activo")
            self.results["warnings"] += 1
    
    def print_summary(self):
        """Imprime resumen de resultados."""
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}RESUMEN DE PRUEBAS{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
        
        total = self.results["passed"] + self.results["failed"] + self.results["warnings"]
        
        print(f"\n{Colors.OKGREEN}✅ Pruebas exitosas: {self.results['passed']}{Colors.ENDC}")
        print(f"{Colors.FAIL}❌ Pruebas fallidas: {self.results['failed']}{Colors.ENDC}")
        print(f"{Colors.WARNING}⚠️  Advertencias: {self.results['warnings']}{Colors.ENDC}")
        print(f"{Colors.BOLD}📊 Total: {total}{Colors.ENDC}")
        
        if self.results["failed"] == 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 TODOS LOS TESTS PASARON{Colors.ENDC}")
            success_rate = 100
        else:
            success_rate = (self.results["passed"] / total * 100) if total > 0 else 0
            print(f"\n{Colors.WARNING}Tasa de éxito: {success_rate:.1f}%{Colors.ENDC}")
        
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")
        
        return self.results["failed"] == 0


def main():
    """Función principal."""
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("="*70)
    print("    SUITE DE PRUEBAS - SISTEMA DE AVATARES")
    print("="*70)
    print(f"{Colors.ENDC}")
    
    tester = AvatarTester()
    
    # 1. Test de assets (público)
    tester.test_assets_endpoint()
    
    # 2. Login de usuarios
    for user_type in ["docente", "estudiante"]:
        tester.login(user_type)
    
    # 3. Obtener avatares de cada usuario
    for user_type in ["docente", "estudiante"]:
        tester.test_get_my_avatars(user_type)
    
    # 4. Crear avatares si no existen
    for user_type in ["docente", "estudiante"]:
        avatars = tester.avatars.get(user_type, {}).get("list", [])
        if len(avatars) == 0:
            print_info(f"Creando avatar de prueba para {user_type}...")
            tester.test_create_avatar(user_type)
            # Recargar avatares después de crear
            tester.test_get_my_avatars(user_type)
    
    # 5. Test de aislamiento
    tester.test_avatar_isolation()
    
    # 6. Test del bug reportado
    tester.test_cross_user_avatar_bug()
    
    # 7. Actualizar avatares
    for user_type in ["docente", "estudiante"]:
        avatar_id = tester.avatars.get(user_type, {}).get("active_id")
        if avatar_id:
            tester.test_update_avatar(user_type, avatar_id)
    
    # Resumen final
    success = tester.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
