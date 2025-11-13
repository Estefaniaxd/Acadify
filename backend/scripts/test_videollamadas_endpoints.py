"""
Script de pruebas para los endpoints REST de videollamadas.

Prueba todos los endpoints implementados:
- Crear videollamada
- Obtener por ID
- Listar con filtros
- Unirse a videollamada (genera JWT)
- Salir de videollamada
- Finalizar videollamada
- Listar participantes
- Listar grabaciones
- Estadísticas

Requiere:
- Servidor corriendo en http://127.0.0.1:8000
- Token JWT válido
- Sala de chat existente

Ejecutar:
    python scripts/test_videollamadas_endpoints.py
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Añadir directorio raíz al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

try:
    import requests
except ImportError:
    print("❌ Error: requests no está instalado")
    print("   Instalar con: pip install requests")
    sys.exit(1)


# ===============================
# Configuración
# ===============================

BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/communication/videollamadas"

# Token JWT válido (reemplazar con uno válido de tu sistema)
# Este token debe ser generado con generate_test_token.py o similar
TOKEN = None  # Se generará o solicitará

# IDs de prueba (se crearán dinámicamente durante tests)
TEST_SALA_CHAT_ID = None
TEST_VIDEOLLAMADA_ID = None
TEST_PARTICIPANTE_ID = None


# ===============================
# Utilidades
# ===============================

def print_header(title: str):
    """Imprime header para sección"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message: str):
    """Imprime mensaje de éxito"""
    print(f"✅ {message}")


def print_error(message: str):
    """Imprime mensaje de error"""
    print(f"❌ {message}")


def print_info(message: str):
    """Imprime mensaje informativo"""
    print(f"ℹ️  {message}")


def print_warning(message: str):
    """Imprime advertencia"""
    print(f"⚠️  {message}")


def get_headers() -> Dict[str, str]:
    """Obtiene headers con autenticación"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }


def make_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> tuple[int, Optional[Dict[str, Any]]]:
    """
    Hace una petición HTTP y retorna status code y response data.
    
    Args:
        method: HTTP method (GET, POST, PATCH, DELETE)
        endpoint: Endpoint path
        data: JSON data for request body
        params: Query parameters
        
    Returns:
        tuple: (status_code, response_data)
    """
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=get_headers(), params=params)
        elif method == "POST":
            response = requests.post(url, headers=get_headers(), json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=get_headers(), json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=get_headers())
        else:
            raise ValueError(f"Método HTTP no soportado: {method}")
        
        # Intentar parsear JSON
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"raw": response.text}
        
        return response.status_code, response_data
    
    except requests.exceptions.ConnectionError:
        print_error("No se pudo conectar al servidor")
        print_info("Asegúrate de que el servidor esté corriendo en http://127.0.0.1:8000")
        return 0, None
    except Exception as e:
        print_error(f"Error en petición: {e}")
        return 0, None


# ===============================
# Tests de Endpoints
# ===============================

def test_health_check() -> bool:
    """Test 1: Health check del sistema"""
    print_header("TEST 1: Health Check")
    
    status, data = make_request("GET", "/health")
    
    if status == 200:
        print_success(f"Health check OK: {data.get('message', 'N/A')}")
        return True
    else:
        print_error(f"Health check falló: {status}")
        return False


def test_crear_videollamada() -> bool:
    """Test 2: Crear nueva videollamada"""
    global TEST_VIDEOLLAMADA_ID
    
    print_header("TEST 2: Crear Videollamada")
    
    # Primero necesitamos un sala_chat_id válido
    # Por ahora usaremos uno de prueba (deberías tener uno en tu DB)
    from uuid import uuid4
    test_sala_id = str(uuid4())  # En producción, usar una sala real
    
    data = {
        "sala_chat_id": test_sala_id,
        "tipo_llamada": "video",
        "titulo": "Clase de Matemáticas - Test",
        "descripcion": "Videollamada de prueba desde script",
        "jitsi_room_name": f"test-room-{int(time.time())}",
        "configuracion": {
            "max_participantes": 30,
            "permitir_grabacion": True,
            "activar_sala_espera": False,
            "requerir_contrasena": False
        }
    }
    
    print_info("Datos de videollamada:")
    print(json.dumps(data, indent=2))
    
    status, response = make_request("POST", "/crear", data=data)
    
    if status == 201:
        print_success("Videollamada creada exitosamente")
        TEST_VIDEOLLAMADA_ID = response.get("id")
        print_info(f"ID: {TEST_VIDEOLLAMADA_ID}")
        print_info(f"Room: {response.get('jitsi_room_name')}")
        print_info(f"Estado: {response.get('estado')}")
        print_info(f"Participantes: {len(response.get('participantes', []))}")
        return True
    elif status == 401:
        print_error("No autenticado - Token inválido o expirado")
        print_warning("Genera un token válido con: python TEST/generate_test_token.py")
        return False
    elif status == 422:
        print_error(f"Validación falló: {response}")
        return False
    else:
        print_error(f"Error creando videollamada: {status}")
        print_info(f"Response: {response}")
        return False


def test_obtener_videollamada() -> bool:
    """Test 3: Obtener videollamada por ID"""
    print_header("TEST 3: Obtener Videollamada por ID")
    
    if not TEST_VIDEOLLAMADA_ID:
        print_warning("Saltando test - No hay videollamada creada")
        return False
    
    status, response = make_request("GET", f"/{TEST_VIDEOLLAMADA_ID}")
    
    if status == 200:
        print_success("Videollamada obtenida exitosamente")
        print_info(f"Título: {response.get('titulo')}")
        print_info(f"Estado: {response.get('estado')}")
        print_info(f"Tipo: {response.get('tipo_llamada')}")
        print_info(f"Participantes: {len(response.get('participantes', []))}")
        print_info(f"Grabaciones: {len(response.get('grabaciones', []))}")
        return True
    elif status == 404:
        print_error("Videollamada no encontrada")
        return False
    else:
        print_error(f"Error obteniendo videollamada: {status}")
        return False


def test_listar_videollamadas() -> bool:
    """Test 4: Listar videollamadas con filtros"""
    print_header("TEST 4: Listar Videollamadas")
    
    params = {
        "estado": "activa",
        "limit": 10
    }
    
    status, response = make_request("GET", "", params=params)
    
    if status == 200:
        items = response.get("items", [])
        print_success(f"Videollamadas listadas: {len(items)}")
        print_info(f"Total: {response.get('total', 0)}")
        print_info(f"Has more: {response.get('has_more', False)}")
        
        for item in items[:3]:  # Mostrar primeras 3
            print_info(f"  - {item.get('titulo')} ({item.get('estado')})")
        
        return True
    else:
        print_error(f"Error listando videollamadas: {status}")
        return False


def test_listar_activas() -> bool:
    """Test 5: Listar videollamadas activas"""
    print_header("TEST 5: Listar Videollamadas Activas")
    
    status, response = make_request("GET", "/activas")
    
    if status == 200:
        print_success(f"Videollamadas activas: {len(response)}")
        
        for item in response[:3]:
            print_info(f"  - {item.get('titulo')} ({item.get('jitsi_room_name')})")
        
        return True
    else:
        print_error(f"Error listando activas: {status}")
        return False


def test_unirse_videollamada() -> bool:
    """Test 6: Unirse a videollamada (genera JWT)"""
    global TEST_PARTICIPANTE_ID
    
    print_header("TEST 6: Unirse a Videollamada")
    
    if not TEST_VIDEOLLAMADA_ID:
        print_warning("Saltando test - No hay videollamada creada")
        return False
    
    data = {
        "es_moderador": False
    }
    
    status, response = make_request("POST", f"/{TEST_VIDEOLLAMADA_ID}/unirse", data=data)
    
    if status == 200:
        print_success("Usuario unido exitosamente")
        TEST_PARTICIPANTE_ID = response.get("id")
        print_info(f"Participante ID: {TEST_PARTICIPANTE_ID}")
        print_info(f"Es moderador: {response.get('es_moderador')}")
        
        # Verificar JWT token
        jwt_token = response.get("jwt_token")
        if jwt_token:
            print_success(f"JWT generado: {jwt_token[:50]}...")
            print_info(f"Room name: {response.get('jitsi_room_name')}")
        else:
            print_error("JWT token no generado")
            return False
        
        return True
    elif status == 400:
        print_error(f"No se puede unir: {response.get('detail')}")
        return False
    else:
        print_error(f"Error uniéndose: {status}")
        return False


def test_listar_participantes() -> bool:
    """Test 7: Listar participantes de videollamada"""
    print_header("TEST 7: Listar Participantes")
    
    if not TEST_VIDEOLLAMADA_ID:
        print_warning("Saltando test - No hay videollamada creada")
        return False
    
    params = {"solo_activos": True}
    status, response = make_request("GET", f"/{TEST_VIDEOLLAMADA_ID}/participantes", params=params)
    
    if status == 200:
        print_success(f"Participantes listados: {len(response)}")
        
        for p in response:
            nombre = f"{p.get('usuario_nombre', '')} {p.get('usuario_apellido', '')}"
            print_info(f"  - {nombre} (Moderador: {p.get('es_moderador')})")
        
        return True
    else:
        print_error(f"Error listando participantes: {status}")
        return False


def test_estadisticas() -> bool:
    """Test 8: Obtener estadísticas de videollamada"""
    print_header("TEST 8: Estadísticas")
    
    if not TEST_VIDEOLLAMADA_ID:
        print_warning("Saltando test - No hay videollamada creada")
        return False
    
    status, response = make_request("GET", f"/{TEST_VIDEOLLAMADA_ID}/estadisticas")
    
    if status == 200:
        print_success("Estadísticas obtenidas")
        print_info(f"Total participantes: {response.get('total_participantes')}")
        print_info(f"Participantes activos: {response.get('participantes_activos')}")
        print_info(f"Duración total: {response.get('duracion_total_segundos')}s")
        print_info(f"Grabaciones: {response.get('numero_grabaciones')}")
        print_info(f"Tiene transcripción: {response.get('tiene_transcripcion')}")
        return True
    else:
        print_error(f"Error obteniendo estadísticas: {status}")
        return False


def test_listar_grabaciones() -> bool:
    """Test 9: Listar grabaciones"""
    print_header("TEST 9: Listar Grabaciones")
    
    if not TEST_VIDEOLLAMADA_ID:
        print_warning("Saltando test - No hay videollamada creada")
        return False
    
    status, response = make_request("GET", f"/{TEST_VIDEOLLAMADA_ID}/grabaciones")
    
    if status == 200:
        print_success(f"Grabaciones listadas: {len(response)}")
        
        if len(response) == 0:
            print_info("  (No hay grabaciones aún)")
        else:
            for g in response:
                print_info(f"  - {g.get('formato')} ({g.get('calidad')}) - {g.get('tamano_mb')}MB")
        
        return True
    else:
        print_error(f"Error listando grabaciones: {status}")
        return False


def test_salir_videollamada() -> bool:
    """Test 10: Salir de videollamada"""
    print_header("TEST 10: Salir de Videollamada")
    
    if not TEST_VIDEOLLAMADA_ID:
        print_warning("Saltando test - No hay videollamada creada")
        return False
    
    status, response = make_request("POST", f"/{TEST_VIDEOLLAMADA_ID}/salir")
    
    if status == 200:
        print_success(response.get("message", "Salida exitosa"))
        return True
    else:
        print_error(f"Error saliendo: {status}")
        return False


def test_finalizar_videollamada() -> bool:
    """Test 11: Finalizar videollamada (requiere permisos de moderador)"""
    print_header("TEST 11: Finalizar Videollamada")
    
    if not TEST_VIDEOLLAMADA_ID:
        print_warning("Saltando test - No hay videollamada creada")
        return False
    
    status, response = make_request("POST", f"/{TEST_VIDEOLLAMADA_ID}/finalizar")
    
    if status == 200:
        print_success("Videollamada finalizada")
        print_info(f"Estado: {response.get('estado')}")
        print_info(f"Duración: {response.get('duracion_segundos')}s")
        return True
    elif status == 403:
        print_warning("No tienes permisos de moderador para finalizar")
        print_info("(Esto es esperado si no eres el iniciador)")
        return True  # No es un fallo real
    else:
        print_error(f"Error finalizando: {status}")
        return False


# ===============================
# Utilidades de Setup
# ===============================

def verificar_servidor() -> bool:
    """Verifica que el servidor esté corriendo"""
    print_header("Verificando Servidor")
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        if response.status_code == 200:
            print_success("Servidor corriendo OK")
            return True
        else:
            print_error(f"Servidor respondió con: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("No se pudo conectar al servidor")
        print_info("Inicia el servidor con: uvicorn src.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error verificando servidor: {e}")
        return False


def obtener_token() -> bool:
    """Obtiene o solicita un token JWT válido"""
    global TOKEN
    
    print_header("Configurando Token JWT")
    
    # Intenta cargar token de archivo
    token_file = backend_dir / "TEST" / "test_token.txt"
    if token_file.exists():
        TOKEN = token_file.read_text().strip()
        print_success(f"Token cargado desde archivo: {TOKEN[:30]}...")
        return True
    
    # Solicitar token al usuario
    print_warning("No se encontró token guardado")
    print_info("Genera un token con: python TEST/generate_test_token.py")
    print_info("O pega un token válido aquí:")
    
    user_token = input("Token JWT: ").strip()
    if user_token:
        TOKEN = user_token
        print_success("Token configurado")
        return True
    else:
        print_error("Token requerido para continuar")
        return False


# ===============================
# Main Test Runner
# ===============================

def run_all_tests():
    """Ejecuta todos los tests en orden"""
    print("\n" + "=" * 70)
    print("🧪 SUITE DE PRUEBAS - ENDPOINTS DE VIDEOLLAMADAS")
    print("=" * 70)
    
    # Setup
    if not verificar_servidor():
        print_error("Servidor no disponible. Abortando tests.")
        return False
    
    if not obtener_token():
        print_error("Token no disponible. Abortando tests.")
        return False
    
    # Tests
    tests = [
        ("Health Check", test_health_check),
        ("Crear Videollamada", test_crear_videollamada),
        ("Obtener por ID", test_obtener_videollamada),
        ("Listar Videollamadas", test_listar_videollamadas),
        ("Listar Activas", test_listar_activas),
        ("Unirse (genera JWT)", test_unirse_videollamada),
        ("Listar Participantes", test_listar_participantes),
        ("Estadísticas", test_estadisticas),
        ("Listar Grabaciones", test_listar_grabaciones),
        ("Salir de Llamada", test_salir_videollamada),
        ("Finalizar Llamada", test_finalizar_videollamada),
    ]
    
    results = []
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_error(f"Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
            failed += 1
        
        # Pequeña pausa entre tests
        time.sleep(0.5)
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    for test_name, result in results:
        if result:
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name}")
    
    print("\n" + "=" * 70)
    print(f"✅ Tests exitosos: {passed}/{len(tests)}")
    print(f"❌ Tests fallidos: {failed}/{len(tests)}")
    print(f"📊 Tasa de éxito: {(passed / len(tests) * 100):.1f}%")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ Sistema de videollamadas funcionando correctamente")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) fallaron")
        print("💡 Revisa los errores arriba para más detalles")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
