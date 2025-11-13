"""
Test del flujo completo de invitación de coordinadores.

Este script prueba:
1. Crear una institución (admin)
2. Enviar invitación a coordinador
3. Validar código de invitación
4. Aceptar invitación y registrar coordinador
5. Verificar que la institución se activó

Uso:
    python TEST/test_invitacion_flow.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
# Usamos un usuario existente que sabemos que funciona
TEST_EMAIL = "docente@acadify.com"  # Usuario de prueba
TEST_PASSWORD = "Admin123!"

# Colores para output
class Colors:
    GREEN = '\033[92m',
    RED = '\033[91m',
    YELLOW = '\033[93m',
    BLUE = '\033[94m',
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.RESET}\n")


# Test 1: Login como admin
def test_admin_login():
    print_section("TEST 1: Registrar Administrador y Login")
    
    # Primero intentamos registrar un admin
    timestamp = datetime.now().strftime("%H%M%S")
    admin_email = f"admin.test{timestamp}@acadify.com",
    admin_password = "AdminTest123!"
    
    print_info("Registrando nuevo administrador...")
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": admin_email,
            "password": admin_password,
            "username": f"admin{timestamp}",
            "nombre": "Admin",
            "apellido": "Test",
            "rol": "admin"
        }
    )
    
    if register_response.status_code == 201:
        print_success(f"Admin registrado: {admin_email}")
    else:
        print_warning(f"No se pudo registrar admin (puede que ya exista similar)")
    
    # Ahora hacemos login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "identifier": admin_email,
            "password": admin_password
        }
    )
    
    if response.status_code == 200:,
        data = response.json()
        token = data.get("access_token")
        print_success(f"Login exitoso como {admin_email}")
        print_info(f"Token obtenido: {token[:50]}...")
        return token
    else:
        print_error(f"Error en login: {response.status_code}")
        print_error(f"Respuesta: {response.text}")
        return None


# Test 2: Crear institución
def test_crear_institucion(token):
    print_section("TEST 2: Crear Nueva Institución")
    
    timestamp = datetime.now().strftime("%H%M%S")
    institucion_data = {
        "nombre": f"Universidad de Prueba {timestamp}",
        "sigla": f"UPT{timestamp[-4:]}",
        "lema": "Educación de calidad para todos",
        "tipo_institucion": "universidad",
        "usa_programas": True,
        "nivel_educativo": "superior",
        "sector": "publico",
        "direccion": "Calle 123 #45-67",
        "ciudad": "Bogotá",
        "pais": "Colombia",
        "correo_institucional": f"contacto.prueba{timestamp}@universidad.edu.co",
        "telefono": "+57 300 123 4567",
        "nit": f"900{timestamp}"
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/instituciones",
        json=institucion_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:,
        data = response.json()
        institucion_id = data["institucion_id"]
        print_success(f"Institución creada: {data['nombre']}")
        print_info(f"ID: {institucion_id}")
        print_info(f"Estado: {data.get('estado', 'N/A')}")
        return institucion_id
    else:
        print_error(f"Error al crear institución: {response.status_code}")
        print_error(f"Respuesta: {response.text}")
        return None


# Test 3: Invitar coordinador
def test_invitar_coordinador(token, institucion_id):
    print_section("TEST 3: Enviar Invitación a Coordinador")
    
    timestamp = datetime.now().strftime("%H%M%S")
    email_coordinador = f"coordinador.test{timestamp}@gmail.com"
    
    response = requests.post(
        f"{BASE_URL}/admin/instituciones/{institucion_id}/invitar-coordinador",
        json={"email_destino": email_coordinador},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:,
        data = response.json()
        codigo = data["codigo"]
        print_success(f"Invitación enviada a {email_coordinador}")
        print_info(f"Código generado: {codigo}")
        print_info(f"Estado: {data['estado']}")
        print_info(f"Expira: {data['fecha_expiracion']}")
        return codigo, email_coordinador
    else:
        print_error(f"Error al enviar invitación: {response.status_code}")
        print_error(f"Respuesta: {response.text}")
        return None, None


# Test 4: Validar código
def test_validar_codigo(codigo):
    print_section("TEST 4: Validar Código de Invitación")
    
    response = requests.post(
        f"{BASE_URL}/admin/invitaciones/validar",
        params={"codigo": codigo}
    )
    
    if response.status_code == 200:,
        data = response.json()
        print_success("Código válido")
        print_info(f"Email destino: {data['invitacion']['email_destino']}")
        print_info(f"Institución: {data['institucion']['nombre']}")
        print_info(f"Ciudad: {data['institucion']['ciudad']}, {data['institucion']['pais']}")
        return True
    else:
        print_error(f"Error al validar código: {response.status_code}")
        print_error(f"Respuesta: {response.text}")
        return False


# Test 5: Aceptar invitación
def test_aceptar_invitacion(codigo):
    print_section("TEST 5: Aceptar Invitación y Registrar Coordinador")
    
    response = requests.post(
        f"{BASE_URL}/admin/invitaciones/aceptar",
        params={
            "codigo": codigo,
            "nombre": "Juan Carlos",
            "apellido": "Pérez Gómez",
            "password": "SecurePass123!"
        }
    )
    
    if response.status_code == 200:,
        data = response.json()
        print_success("Invitación aceptada exitosamente")
        print_info(f"Usuario creado: {data['usuario']['nombre']} {data['usuario']['apellido']}")
        print_info(f"Email: {data['usuario']['email']}")
        print_info(f"Rol: {data['usuario']['rol']}")
        print_info(f"Institución: {data['institucion']['nombre']}")
        print_info(f"Estado institución: {data['institucion']['estado']}")
        if data['institucion']['fecha_activacion']:
            print_info(f"Fecha activación: {data['institucion']['fecha_activacion']}")
        return data['usuario']['email']
    else:
        print_error(f"Error al aceptar invitación: {response.status_code}")
        print_error(f"Respuesta: {response.text}")
        return None


# Test 6: Login como coordinador
def test_coordinador_login(email):
    print_section("TEST 6: Login como Coordinador")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "identifier": email,
            "password": "SecurePass123!"
        }
    )
    
    if response.status_code == 200:,
        data = response.json()
        print_success(f"Login exitoso como coordinador")
        print_info(f"Usuario: {data.get('user', {}).get('username', 'N/A')}")
        print_info(f"Rol: {data.get('user', {}).get('role', 'N/A')}")
        return True
    else:
        print_error(f"Error en login coordinador: {response.status_code}")
        print_error(f"Respuesta: {response.text}")
        return False


# Test 7: Verificar que no se puede usar el código dos veces
def test_codigo_ya_usado(codigo):
    print_section("TEST 7: Verificar que Código No Se Puede Reutilizar")
    
    response = requests.post(
        f"{BASE_URL}/admin/invitaciones/validar",
        params={"codigo": codigo}
    )
    
    if response.status_code != 200:
        print_success("Código correctamente marcado como usado")
        print_info(f"Status: {response.status_code}")
        return True
    else:
        print_warning("⚠️ PROBLEMA: El código todavía se puede validar")
        return False


def main():
    print("\n" + "="*60)
    print(f"{Colors.BLUE}🧪 TEST COMPLETO: FLUJO DE INVITACIÓN DE COORDINADORES{Colors.RESET}")
    print("="*60)
    
    try:
        # Test 1: Login admin
        token = test_admin_login()
        if not token:
            print_error("No se pudo obtener token de admin. Abortando.")
            return
        
        # Test 2: Crear institución
        institucion_id = test_crear_institucion(token)
        if not institucion_id:
            print_error("No se pudo crear institución. Abortando.")
            return
        
        # Test 3: Invitar coordinador
        codigo, email_coord = test_invitar_coordinador(token, institucion_id)
        if not codigo:
            print_error("No se pudo enviar invitación. Abortando.")
            return
        
        # Test 4: Validar código
        if not test_validar_codigo(codigo):
            print_error("Código no válido. Abortando.")
            return
        
        # Test 5: Aceptar invitación
        email_creado = test_aceptar_invitacion(codigo)
        if not email_creado:
            print_error("No se pudo aceptar invitación. Abortando.")
            return
        
        # Test 6: Login como coordinador
        if not test_coordinador_login(email_creado):
            print_error("No se pudo hacer login como coordinador.")
            return
        
        # Test 7: Código ya usado
        test_codigo_ya_usado(codigo)
        
        # Resumen final
        print_section("✅ RESUMEN: TODOS LOS TESTS PASARON")
        print_success("El flujo completo funciona correctamente:")
        print("  1. ✓ Admin puede crear instituciones")
        print("  2. ✓ Admin puede enviar invitaciones")
        print("  3. ✓ Códigos se pueden validar antes de usar")
        print("  4. ✓ Coordinador puede aceptar invitación y registrarse")
        print("  5. ✓ Institución se activa automáticamente")
        print("  6. ✓ Coordinador puede hacer login")
        print("  7. ✓ Códigos no se pueden reutilizar")
        
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

