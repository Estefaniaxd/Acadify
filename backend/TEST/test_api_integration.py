#!/usr/bin/env python3
"""
Script de pruebas de integración para APIs de Acadify
Verifica funcionalidad end-to-end de los principales módulos
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuración
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}🧪 TEST: {name}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.ENDC}")

# Variables globales para tokens y IDs
auth_tokens = {}
created_ids = {}

# ==================== UTILIDADES ====================

def make_request(method, endpoint, data=None, token=None, files=None):
    """Realiza una petición HTTP"""
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if files:
        # No establecer Content-Type para multipart/form-data
        pass
    elif data and method in ["POST", "PUT", "PATCH"]:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data)
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            files=files,
            timeout=10
        )
        return response
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None

# ==================== TESTS DE AUTENTICACIÓN ====================

def test_health_check():
    """Verifica que el servidor esté corriendo"""
    print_test("Health Check - Servidor activo")
    
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    
    if response.status_code == 200:
        print_success("Servidor está activo")
        return True
    else:
        print_error(f"Servidor no responde correctamente: {response.status_code}")
        return False

def test_register_users():
    """Registra usuarios de prueba"""
    print_test("Registro de Usuarios")
    
    usuarios = [
        {
            "email": "docente.test@acadify.com",
            "password": "Test123456",
            "nombre": "Juan",
            "apellido": "Docente",
            "tipo_usuario": "docente"
        },
        {
            "email": "estudiante.test@acadify.com",
            "password": "Test123456",
            "nombre": "María",
            "apellido": "Estudiante",
            "tipo_usuario": "estudiante"
        },
        {
            "email": "coordinador.test@acadify.com",
            "password": "Test123456",
            "nombre": "Carlos",
            "apellido": "Coordinador",
            "tipo_usuario": "coordinador"
        }
    ]
    
    success_count = 0
    for user in usuarios:
        response = make_request("POST", "/auth/register", data=user)
        
        if response and response.status_code in [200, 201]:
            print_success(f"Usuario registrado: {user['email']}")
            success_count += 1
        elif response and response.status_code == 400:
            print_warning(f"Usuario ya existe: {user['email']}")
            success_count += 1
        else:
            print_error(f"Error registrando {user['email']}: {response.status_code if response else 'No response'}")
    
    return success_count == len(usuarios)

def test_login_users():
    """Login de usuarios de prueba"""
    print_test("Login de Usuarios")
    
    usuarios = [
        {"email": "docente.test@acadify.com", "password": "Test123456", "tipo": "docente"},
        {"email": "estudiante.test@acadify.com", "password": "Test123456", "tipo": "estudiante"},
        {"email": "coordinador.test@acadify.com", "password": "Test123456", "tipo": "coordinador"}
    ]
    
    success_count = 0
    for user in usuarios:
        response = make_request("POST", "/auth/login", data={
            "email": user["email"],
            "password": user["password"]
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                auth_tokens[user["tipo"]] = data["access_token"]
                print_success(f"Login exitoso: {user['email']}")
                success_count += 1
            else:
                print_error(f"Login sin token: {user['email']}")
        else:
            print_error(f"Error login {user['email']}: {response.status_code if response else 'No response'}")
    
    return success_count == len(usuarios)

def test_get_current_user():
    """Obtiene información del usuario actual"""
    print_test("Obtener usuario actual (/auth/me)")
    
    if not auth_tokens.get("docente"):
        print_error("No hay token de docente disponible")
        return False
    
    response = make_request("GET", "/auth/me", token=auth_tokens["docente"])
    
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Usuario obtenido: {data.get('email', 'N/A')}")
        created_ids["docente_id"] = data.get("usuario_id")
        return True
    else:
        print_error(f"Error obteniendo usuario: {response.status_code if response else 'No response'}")
        return False

# ==================== TESTS DE CURSOS ====================

def test_create_curso():
    """Crea un curso de prueba"""
    print_test("Crear Curso")
    
    if not auth_tokens.get("docente"):
        print_error("No hay token de docente disponible")
        return False
    
    curso_data = {
        "nombre": "Matemáticas Avanzadas",
        "codigo": f"MAT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "descripcion": "Curso de prueba para matemáticas",
        "creditos": 4,
        "estado": "activo"
    }
    
    response = make_request("POST", "/cursos", data=curso_data, token=auth_tokens["docente"])
    
    if response and response.status_code in [200, 201]:
        data = response.json()
        created_ids["curso_id"] = data.get("id") or data.get("curso_id")
        print_success(f"Curso creado: {curso_data['nombre']} (ID: {created_ids['curso_id']})")
        return True
    else:
        print_error(f"Error creando curso: {response.status_code if response else 'No response'}")
        if response:
            print_info(f"Response: {response.text[:200]}")
        return False

def test_list_cursos():
    """Lista todos los cursos"""
    print_test("Listar Cursos")
    
    if not auth_tokens.get("docente"):
        print_error("No hay token disponible")
        return False
    
    response = make_request("GET", "/cursos", token=auth_tokens["docente"])
    
    if response and response.status_code == 200:
        data = response.json()
        count = len(data) if isinstance(data, list) else data.get("total", 0)
        print_success(f"Cursos listados: {count}")
        return True
    else:
        print_error(f"Error listando cursos: {response.status_code if response else 'No response'}")
        return False

# ==================== TESTS DE TAREAS ====================

def test_create_tarea():
    """Crea una tarea de prueba"""
    print_test("Crear Tarea")
    
    if not auth_tokens.get("docente") or not created_ids.get("curso_id"):
        print_error("Falta token de docente o ID de curso")
        return False
    
    fecha_inicio = datetime.now()
    fecha_entrega = fecha_inicio + timedelta(days=7)
    
    tarea_data = {
        "titulo": "Tarea de Prueba - Integrales",
        "descripcion": "Resolver ejercicios de integrales indefinidas",
        "curso_id": created_ids["curso_id"],
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_entrega": fecha_entrega.isoformat(),
        "puntuacion_maxima": 100,
        "tipo": "individual",
        "estado": "publicada"
    }
    
    response = make_request("POST", "/tareas", data=tarea_data, token=auth_tokens["docente"])
    
    if response and response.status_code in [200, 201]:
        data = response.json()
        created_ids["tarea_id"] = data.get("id") or data.get("tarea_id")
        print_success(f"Tarea creada: {tarea_data['titulo']} (ID: {created_ids['tarea_id']})")
        return True
    else:
        print_error(f"Error creando tarea: {response.status_code if response else 'No response'}")
        if response:
            print_info(f"Response: {response.text[:200]}")
        return False

def test_list_tareas():
    """Lista todas las tareas"""
    print_test("Listar Tareas")
    
    if not auth_tokens.get("estudiante"):
        print_error("No hay token de estudiante disponible")
        return False
    
    response = make_request("GET", "/tareas", token=auth_tokens["estudiante"])
    
    if response and response.status_code == 200:
        data = response.json()
        count = len(data) if isinstance(data, list) else data.get("total", 0)
        print_success(f"Tareas listadas: {count}")
        return True
    else:
        print_error(f"Error listando tareas: {response.status_code if response else 'No response'}")
        return False

# ==================== TESTS DE EVALUACIONES ====================

def test_create_evaluacion():
    """Crea una evaluación de prueba"""
    print_test("Crear Evaluación")
    
    if not auth_tokens.get("docente") or not created_ids.get("curso_id"):
        print_error("Falta token o ID de curso")
        return False
    
    fecha_inicio = datetime.now()
    fecha_fin = fecha_inicio + timedelta(days=1)
    
    evaluacion_data = {
        "titulo": "Examen Parcial - Cálculo",
        "descripcion": "Evaluación de los temas 1-5",
        "curso_id": created_ids["curso_id"],
        "tipo_evaluacion": "examen",
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat(),
        "duracion_minutos": 90,
        "puntuacion_maxima": 100,
        "estado": "activa"
    }
    
    response = make_request("POST", "/evaluaciones", data=evaluacion_data, token=auth_tokens["docente"])
    
    if response and response.status_code in [200, 201]:
        data = response.json()
        created_ids["evaluacion_id"] = data.get("id") or data.get("evaluacion_id")
        print_success(f"Evaluación creada: {evaluacion_data['titulo']} (ID: {created_ids['evaluacion_id']})")
        return True
    else:
        print_error(f"Error creando evaluación: {response.status_code if response else 'No response'}")
        if response:
            print_info(f"Response: {response.text[:200]}")
        return False

# ==================== MAIN ====================

def run_all_tests():
    """Ejecuta todos los tests en orden"""
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"🚀 INICIANDO TESTS DE INTEGRACIÓN DE APIs - ACADIFY")
    print(f"{'='*70}{Colors.ENDC}\n")
    
    results = {}
    
    # Tests de infraestructura
    results["health"] = test_health_check()
    if not results["health"]:
        print_error("\n❌ Servidor no está activo. Abortando tests.")
        return
    
    # Tests de autenticación
    results["register"] = test_register_users()
    results["login"] = test_login_users()
    results["me"] = test_get_current_user()
    
    # Tests de módulos académicos
    if results["login"]:
        results["create_curso"] = test_create_curso()
        results["list_cursos"] = test_list_cursos()
        results["create_tarea"] = test_create_tarea()
        results["list_tareas"] = test_list_tareas()
        results["create_evaluacion"] = test_create_evaluacion()
    
    # Resumen
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"📊 RESUMEN DE RESULTADOS")
    print(f"{'='*70}{Colors.ENDC}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests pasados{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}\n🎉 ¡TODOS LOS TESTS PASARON!{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}\n⚠️  Algunos tests fallaron. Revisar logs arriba.{Colors.ENDC}")
    
    print(f"\n{Colors.BLUE}IDs creados:{Colors.ENDC}")
    for key, value in created_ids.items():
        print(f"  • {key}: {value}")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrumpidos por el usuario{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
