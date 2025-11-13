#!/usr/bin/env python3
"""
Script para probar los endpoints del sistema de proctoring.
Verifica la integración completa: API → Base de Datos → Respuestas

Endpoints a probar:
1. POST /api/evaluaciones/proctoring/intentos/{id}/eventos
2. POST /api/evaluaciones/proctoring/intentos/{id}/snapshots
3. POST /api/evaluaciones/proctoring/intentos/{id}/eventos-audio
4. GET /api/evaluaciones/proctoring/intentos/{id}/resumen
5. PATCH /api/evaluaciones/proctoring/eventos/{id}/resolver

Uso:
    python test_proctoring_endpoints.py
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime
import base64

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuración
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/evaluaciones/proctoring"


class Colors:
    """Códigos de color ANSI para output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Imprime un encabezado destacado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    """Imprime mensaje de error"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """Imprime mensaje informativo"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text: str):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def generate_test_token() -> str:
    """
    Genera un token de prueba.
    En producción, este vendría del login.
    """
    # TODO: Implementar login real
    print_warning("Usando mock token. Implementar login real para producción.")
    return "test_token_123"


def create_test_intento() -> str:
    """
    Crea un intento de evaluación de prueba.
    Retorna el ID del intento creado.
    """
    from sqlalchemy import create_engine, text
    from src.core.config import settings
    import uuid
    
    print_info("Creando intento de evaluación de prueba...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.begin() as conn:
            # Verificar si ya existe un intento de prueba
            result = conn.execute(text("""
                SELECT id FROM intentos_evaluacion 
                WHERE estudiante_id = 'test_student_proctoring'
                ORDER BY fecha_inicio DESC
                LIMIT 1
            """))
            
            existing = result.fetchone()
            if existing:
                intento_id = existing[0]
                print_success(f"Usando intento existente: {intento_id}")
                return intento_id
            
            # Crear evaluación de prueba si no existe
            evaluacion_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO evaluaciones (
                    id, curso_id, titulo, descripcion, tipo_evaluacion,
                    puntuacion_maxima, tiempo_limite_minutos, intentos_permitidos,
                    creado_por, fecha_creacion, estado
                ) VALUES (
                    :id, 'test_curso', 'Evaluación Proctoring Test', 
                    'Evaluación para pruebas de proctoring', 'examen',
                    100, 60, 3, 'test_profesor', NOW(), 'activo'
                )
                ON CONFLICT (id) DO NOTHING
            """), {"id": evaluacion_id})
            
            # Crear intento de prueba
            intento_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO intentos_evaluacion (
                    id, evaluacion_id, estudiante_id, numero_intento,
                    estado_intento, fecha_inicio, total_preguntas,
                    puntuacion_maxima, progreso_actual
                ) VALUES (
                    :id, :evaluacion_id, 'test_student_proctoring', 1,
                    'en_progreso', NOW(), 10, 100, 0.0
                )
            """), {"id": intento_id, "evaluacion_id": evaluacion_id})
            
            print_success(f"Intento creado: {intento_id}")
            return intento_id
            
    except Exception as e:
        print_error(f"Error al crear intento de prueba: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


def test_registrar_evento(intento_id: str, token: str) -> dict:
    """
    Prueba POST /proctoring/intentos/{id}/eventos
    """
    print_header("TEST 1: Registrar Evento de Proctoring")
    
    url = f"{BASE_URL}{API_PREFIX}/intentos/{intento_id}/eventos"
    
    payload = {
        "tipo": "sin_rostro",
        "severidad": "alta",
        "mensaje": "No se detectó rostro en la cámara",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "test": True,
            "confidence": 0.95
        }
    }
    
    print_info(f"POST {url}")
    print_info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success("Evento registrado exitosamente")
            print_info(f"Evento ID: {data.get('evento_id', 'N/A')}")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return data
        else:
            print_error(f"Error: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Excepción: {e}")
        return None


def test_subir_snapshot(intento_id: str, token: str) -> dict:
    """
    Prueba POST /proctoring/intentos/{id}/snapshots
    """
    print_header("TEST 2: Subir Snapshot de Cámara")
    
    url = f"{BASE_URL}{API_PREFIX}/intentos/{intento_id}/snapshots"
    
    # Crear una imagen de prueba en base64 (1x1 pixel PNG transparente)
    fake_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    payload = {
        "imagen_base64": fake_image_base64,
        "formato": "image/png",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "resolution": "1x1",
            "test": True
        }
    }
    
    print_info(f"POST {url}")
    print_info("Payload: [imagen_base64 truncada para visualización]")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success("Snapshot subido exitosamente")
            print_info(f"Snapshot ID: {data.get('snapshot_id', 'N/A')}")
            return data
        else:
            print_error(f"Error: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Excepción: {e}")
        return None


def test_registrar_evento_audio(intento_id: str, token: str) -> dict:
    """
    Prueba POST /proctoring/intentos/{id}/eventos-audio
    """
    print_header("TEST 3: Registrar Evento de Audio")
    
    url = f"{BASE_URL}{API_PREFIX}/intentos/{intento_id}/eventos-audio"
    
    payload = {
        "nivel_audio": 85.5,
        "frecuencias_detectadas": [200.5, 450.3, 1200.8],
        "duracion_ms": 5000,
        "es_sospechoso": True,
        "descripcion": "Nivel de audio elevado detectado",
        "metadata": {
            "test": True,
            "source": "test_script"
        }
    }
    
    print_info(f"POST {url}")
    print_info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success("Evento de audio registrado exitosamente")
            print_info(f"Evento Audio ID: {data.get('evento_audio_id', 'N/A')}")
            return data
        else:
            print_error(f"Error: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Excepción: {e}")
        return None


def test_obtener_resumen(intento_id: str, token: str) -> dict:
    """
    Prueba GET /proctoring/intentos/{id}/resumen
    """
    print_header("TEST 4: Obtener Resumen de Proctoring")
    
    url = f"{BASE_URL}{API_PREFIX}/intentos/{intento_id}/resumen"
    
    print_info(f"GET {url}")
    
    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Resumen obtenido exitosamente")
            print_info(f"Total Eventos: {data.get('total_eventos', 0)}")
            print_info(f"Nivel de Riesgo: {data.get('nivel_riesgo', 'N/A')}")
            print_info(f"Response completo:")
            print(json.dumps(data, indent=2))
            return data
        else:
            print_error(f"Error: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Excepción: {e}")
        return None


def test_resolver_evento(evento_id: int, token: str) -> dict:
    """
    Prueba PATCH /proctoring/eventos/{id}/resolver
    """
    print_header("TEST 5: Resolver Evento de Proctoring")
    
    if not evento_id:
        print_warning("No hay evento_id para resolver. Saltando test.")
        return None
    
    url = f"{BASE_URL}{API_PREFIX}/eventos/{evento_id}/resolver"
    
    payload = {
        "resuelto": True,
        "comentario_resolucion": "Evento revisado y considerado falso positivo"
    }
    
    print_info(f"PATCH {url}")
    print_info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.patch(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Evento resuelto exitosamente")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return data
        else:
            print_error(f"Error: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Excepción: {e}")
        return None


def verify_database(intento_id: str):
    """
    Verifica que los datos se hayan guardado correctamente en la base de datos.
    """
    print_header("VERIFICACIÓN: Base de Datos")
    
    from sqlalchemy import create_engine, text
    from src.core.config import settings
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.begin() as conn:
            # Verificar eventos_audio
            result = conn.execute(text("""
                SELECT COUNT(*), AVG(nivel_audio), SUM(CASE WHEN es_sospechoso THEN 1 ELSE 0 END)
                FROM eventos_audio
                WHERE intento_id = :intento_id
            """), {"intento_id": intento_id})
            
            row = result.fetchone()
            if row:
                count, avg_nivel, sospechosos = row
                print_info(f"Eventos de Audio: {count or 0}")
                print_info(f"Nivel Audio Promedio: {avg_nivel or 0:.2f}")
                print_info(f"Eventos Sospechosos: {sospechosos or 0}")
            
            print_success("Verificación de base de datos completada")
            
    except Exception as e:
        print_error(f"Error en verificación de BD: {e}")
    finally:
        engine.dispose()


def main():
    """
    Función principal que ejecuta todos los tests.
    """
    print_header("🚀 TEST SUITE: Sistema de Proctoring")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Generar token
    token = generate_test_token()
    
    # Crear intento de prueba
    intento_id = create_test_intento()
    
    # Ejecutar tests
    results = {
        "test_1_evento": None,
        "test_2_snapshot": None,
        "test_3_audio": None,
        "test_4_resumen": None,
        "test_5_resolver": None
    }
    
    # Test 1: Registrar Evento
    evento_data = test_registrar_evento(intento_id, token)
    results["test_1_evento"] = evento_data is not None
    
    # Test 2: Subir Snapshot
    snapshot_data = test_subir_snapshot(intento_id, token)
    results["test_2_snapshot"] = snapshot_data is not None
    
    # Test 3: Registrar Evento Audio
    audio_data = test_registrar_evento_audio(intento_id, token)
    results["test_3_audio"] = audio_data is not None
    
    # Test 4: Obtener Resumen
    resumen_data = test_obtener_resumen(intento_id, token)
    results["test_4_resumen"] = resumen_data is not None
    
    # Test 5: Resolver Evento (necesita evento_id del test 1)
    if evento_data and "evento_id" in evento_data:
        resolver_data = test_resolver_evento(evento_data["evento_id"], token)
        results["test_5_resolver"] = resolver_data is not None
    
    # Verificar base de datos
    verify_database(intento_id)
    
    # Resumen de resultados
    print_header("📊 RESUMEN DE RESULTADOS")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        elif result is False:
            print_error(f"{test_name}: FAILED")
        else:
            print_warning(f"{test_name}: SKIPPED")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests pasados{Colors.ENDC}")
    
    if passed == total:
        print_success("\n🎉 ¡Todos los tests pasaron exitosamente!")
        sys.exit(0)
    else:
        print_error(f"\n⚠️  {total - passed} tests fallaron")
        sys.exit(1)


if __name__ == "__main__":
    main()
