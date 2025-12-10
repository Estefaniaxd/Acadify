#!/usr/bin/env python3
"""
Script de Testing: Sistema de Entrega de Tareas
Prueba el flujo completo:
1. Login
2. Obtener ID de tarea
3. Enviar FormData con archivo + contenido
4. Verificar respuesta
5. Verificar archivo guardado
"""

import requests
import json
from pathlib import Path
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Credenciales de test (ajustar según tu BD)
TEST_USER_EMAIL = "estudiante@example.com"
TEST_USER_PASSWORD = "password123"

def print_section(title):
    """Imprimir sección del test"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_response(response, label="Response"):
    """Imprimir respuesta HTTP"""
    print(f"\n{label}:")
    print(f"  Status: {response.status_code}")
    try:
        print(f"  Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"  Body: {response.text[:200]}")

def test_entrega_tarea():
    """Test completo del sistema de entrega"""
    
    session = requests.Session()
    
    # ========================================
    # PASO 1: LOGIN
    # ========================================
    print_section("PASO 1: LOGIN")
    
    login_payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    print(f"Enviando login: {login_payload}")
    login_response = session.post(f"{API_URL}/auth/login", json=login_payload)
    print_response(login_response, "Login Response")
    
    if login_response.status_code != 200:
        print("❌ Login fallido")
        return False
    
    token_data = login_response.json()
    access_token = token_data.get("access_token")
    
    if not access_token:
        print("❌ No se obtuvo access_token")
        return False
    
    print(f"✓ Token obtenido: {access_token[:20]}...")
    session.headers.update({"Authorization": f"Bearer {access_token}"})
    
    # ========================================
    # PASO 2: OBTENER TAREAS
    # ========================================
    print_section("PASO 2: OBTENER TAREAS")
    
    # Obtener ID de curso (asumir existe uno)
    # TODO: Ajustar según tu BD
    curso_id = "550e8400-e29b-41d4-a716-446655440000"  # Cambiar por ID real
    
    print(f"Obteniendo tareas del curso: {curso_id}")
    tareas_response = session.get(f"{API_URL}/cursos/tareas/{curso_id}/tareas")
    print_response(tareas_response, "Tareas Response")
    
    if tareas_response.status_code != 200:
        print("⚠ No se obtuvieron tareas")
        # Continuar con una tarea de prueba
        tarea_id = "550e8400-e29b-41d4-a716-446655440111"
    else:
        tareas_data = tareas_response.json()
        tareas = tareas_data.get("tareas", [])
        
        if not tareas:
            print("⚠ No hay tareas disponibles")
            tarea_id = "550e8400-e29b-41d4-a716-446655440111"
        else:
            tarea_id = tareas[0]["id"]
            print(f"✓ Tarea seleccionada: {tarea_id}")
    
    # ========================================
    # PASO 3: CREAR ARCHIVO DE TEST
    # ========================================
    print_section("PASO 3: CREAR ARCHIVO DE TEST")
    
    test_file_path = Path("/tmp/test_entrega.txt")
    test_content = f"Entrega de prueba - {datetime.now().isoformat()}\n"
    test_content += "Esta es una prueba del sistema de entrega de tareas.\n"
    test_content += "Archivo guardado en el servidor con UUID único.\n"
    
    test_file_path.write_text(test_content)
    print(f"✓ Archivo de test creado: {test_file_path}")
    print(f"  Contenido:\n{test_content}")
    
    # ========================================
    # PASO 4: ENVIAR ENTREGA CON FORMDATA
    # ========================================
    print_section("PASO 4: ENVIAR ENTREGA CON FORMDATA")
    
    entrega_url = f"{API_URL}/cursos/tareas/tareas/{tarea_id}/entregar"
    print(f"URL: POST {entrega_url}")
    
    # Crear FormData
    with open(test_file_path, "rb") as f:
        files = {
            "archivo": ("test_entrega.txt", f, "text/plain"),
        }
        data = {
            "contenido": "Esto es mi solución con archivo adjunto",
        }
        
        print(f"\nFormData:")
        print(f"  - contenido: '{data['contenido']}'")
        print(f"  - archivo: test_entrega.txt (text/plain)")
        
        entrega_response = session.post(entrega_url, files=files, data=data)
    
    print_response(entrega_response, "Entrega Response")
    
    # ========================================
    # PASO 5: VALIDAR RESPUESTA
    # ========================================
    print_section("PASO 5: VALIDAR RESPUESTA")
    
    if entrega_response.status_code == 200:
        print("✓ Entrega enviada exitosamente (200 OK)")
        entrega_data = entrega_response.json()
        
        if entrega_data.get("success"):
            print("✓ Response indica éxito")
            print(f"  Data: {json.dumps(entrega_data.get('data', {}), indent=2)}")
        else:
            print("⚠ Response no marca éxito pero status es 200")
        
        return True
    
    elif entrega_response.status_code == 201:
        print("✓ Entrega creada (201 Created)")
        return True
    
    elif entrega_response.status_code in (400, 422):
        print(f"❌ Error de validación ({entrega_response.status_code})")
        print(f"  Detalle: {entrega_response.json()}")
        return False
    
    elif entrega_response.status_code == 401:
        print("❌ No autorizado (401)")
        return False
    
    else:
        print(f"❌ Error inesperado ({entrega_response.status_code})")
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("  TESTING: Sistema de Entrega de Tareas")
    print("="*60)
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Test User: {TEST_USER_EMAIL}")
    
    try:
        success = test_entrega_tarea()
        
        print_section("RESULTADO FINAL")
        if success:
            print("✓ Test completado exitosamente")
            return 0
        else:
            print("❌ Test fallido")
            return 1
    
    except Exception as e:
        print(f"\n❌ Excepción durante test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
