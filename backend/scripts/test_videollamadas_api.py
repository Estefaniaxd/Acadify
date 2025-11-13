"""Script de prueba completo para API de videollamadas con Jitsi.

Este script prueba todos los endpoints de la API de videollamadas:
- Crear videollamada
- Obtener videollamada
- Listar videollamadas activas
- Unirse a videollamada
- Actualizar calidad de conexión
- Listar participantes
- Salir de videollamada
- Finalizar videollamada
- Agregar grabación
- Listar grabaciones
- Actualizar transcripción

Requiere:
- Backend corriendo en http://localhost:8000
- Base de datos con tablas de videollamadas
- Usuario autenticado con token JWT

Uso:
    python scripts/test_videollamadas_api.py

Author: Backend Team
Date: 2025-11-09
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import requests
from dotenv import load_dotenv

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Cargar variables de entorno
load_dotenv()

# ===============================
# Configuración
# ===============================

API_BASE_URL = "http://localhost:8000/api"
VIDEOLLAMADAS_URL = f"{API_BASE_URL}/videollamadas"

# Estos valores deberían obtenerse de un usuario real
# Para testing, usaremos valores de ejemplo
TEST_USER_ID = uuid4()
TEST_SALA_CHAT_ID = uuid4()

# Token de autenticación (debe generarse con un usuario real)
AUTH_TOKEN = None  # Se establecerá después de login


# ===============================
# Funciones de Utilidad
# ===============================


def print_section(title: str) -> None:
    """Imprime título de sección."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_success(message: str) -> None:
    """Imprime mensaje de éxito."""
    print(f"✅ {message}")


def print_error(message: str) -> None:
    """Imprime mensaje de error."""
    print(f"❌ {message}")


def print_info(message: str) -> None:
    """Imprime mensaje informativo."""
    print(f"ℹ️  {message}")


def print_response(response: requests.Response) -> None:
    """Imprime respuesta HTTP formateada."""
    print(f"\nStatus Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    except Exception:
        print(response.text)


def get_headers() -> dict[str, str]:
    """Retorna headers HTTP con autenticación."""
    headers = {"Content-Type": "application/json"}
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    return headers


# ===============================
# Tests de API
# ===============================


def test_health_check() -> bool:
    """Test 1: Health check del módulo."""
    print_section("Test 1: Health Check")

    try:
        response = requests.get(f"{VIDEOLLAMADAS_URL}/health", timeout=5)
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_success("Módulo de videollamadas operativo")
                return True

        print_error("Health check falló")
        return False

    except Exception as e:
        print_error(f"Error en health check: {e}")
        return False


def test_generate_room_name() -> str | None:
    """Test 2: Generar room name único."""
    print_section("Test 2: Generar Room Name")

    try:
        response = requests.get(
            f"{VIDEOLLAMADAS_URL}/room-name/generate",
            params={"base_name": "test-room"},
            headers=get_headers(),
            timeout=5,
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            room_name = data.get("room_name")
            print_success(f"Room name generado: {room_name}")
            return room_name

        print_error("Generación de room name falló")
        return None

    except Exception as e:
        print_error(f"Error generando room name: {e}")
        return None


def test_crear_videollamada(room_name: str | None = None) -> dict[str, Any] | None:
    """Test 3: Crear nueva videollamada."""
    print_section("Test 3: Crear Videollamada")

    payload = {
        "tipo_llamada": "video",
        "configuracion": {
            "max_participantes": 50,
            "permitir_grabacion": True,
            "permitir_chat": True,
        },
    }

    if room_name:
        payload["jitsi_room_name"] = room_name

    try:
        response = requests.post(
            VIDEOLLAMADAS_URL,
            json=payload,
            headers=get_headers(),
            timeout=10,
        )
        print_response(response)

        if response.status_code == 201:
            data = response.json()
            print_success(f"Videollamada creada: {data.get('id')}")
            print_info(f"Room name: {data.get('jitsi_room_name')}")
            print_info(f"Estado: {data.get('estado')}")
            return data

        print_error("Creación de videollamada falló")
        return None

    except Exception as e:
        print_error(f"Error creando videollamada: {e}")
        return None


def test_obtener_videollamada(videollamada_id: str) -> dict[str, Any] | None:
    """Test 4: Obtener videollamada por ID."""
    print_section("Test 4: Obtener Videollamada")

    try:
        response = requests.get(
            f"{VIDEOLLAMADAS_URL}/{videollamada_id}",
            params={"incluir_participantes": True},
            headers=get_headers(),
            timeout=5,
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Videollamada obtenida: {data.get('jitsi_room_name')}")
            print_info(f"Participantes: {len(data.get('participantes', []))}")
            return data

        print_error("Obtención de videollamada falló")
        return None

    except Exception as e:
        print_error(f"Error obteniendo videollamada: {e}")
        return None


def test_listar_videollamadas_activas() -> list[dict[str, Any]]:
    """Test 5: Listar videollamadas activas."""
    print_section("Test 5: Listar Videollamadas Activas")

    try:
        response = requests.get(
            VIDEOLLAMADAS_URL,
            params={"solo_activas": True, "limit": 10},
            headers=get_headers(),
            timeout=5,
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            print_success(f"Videollamadas activas encontradas: {len(items)}")
            return items

        print_error("Listado de videollamadas falló")
        return []

    except Exception as e:
        print_error(f"Error listando videollamadas: {e}")
        return []


def test_unirse_a_videollamada(videollamada_id: str) -> dict[str, Any] | None:
    """Test 6: Unirse a videollamada."""
    print_section("Test 6: Unirse a Videollamada")

    payload = {"es_moderador": False}

    try:
        response = requests.post(
            f"{VIDEOLLAMADAS_URL}/{videollamada_id}/join",
            json=payload,
            headers=get_headers(),
            timeout=10,
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Unido como participante: {data.get('id')}")
            print_info(f"Moderador: {data.get('es_moderador')}")
            return data

        print_error("Unión a videollamada falló")
        print_info("Nota: Puede fallar si ya estás unido")
        return None

    except Exception as e:
        print_error(f"Error uniéndose a videollamada: {e}")
        return None


def test_validar_puede_unirse(videollamada_id: str) -> dict[str, Any] | None:
    """Test 7: Validar si puede unirse."""
    print_section("Test 7: Validar Puede Unirse")

    try:
        response = requests.post(
            f"{VIDEOLLAMADAS_URL}/{videollamada_id}/validate-join",
            headers=get_headers(),
            timeout=5,
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            can_join = data.get("can_join", False)
            if can_join:
                print_success("Puede unirse a la videollamada")
            else:
                print_info(f"No puede unirse: {data.get('reason')}")
            return data

        print_error("Validación falló")
        return None

    except Exception as e:
        print_error(f"Error validando: {e}")
        return None


def test_actualizar_calidad_conexion(participante_id: str) -> dict[str, Any] | None:
    """Test 8: Actualizar calidad de conexión."""
    print_section("Test 8: Actualizar Calidad de Conexión")

    payload = {"latencia_ms": 45, "perdida_paquetes_pct": 0.8}

    try:
        response = requests.patch(
            f"{VIDEOLLAMADAS_URL}/participants/{participante_id}/quality",
            json=payload,
            headers=get_headers(),
            timeout=5,
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Calidad actualizada: {data.get('calidad_conexion')}")
            return data

        print_error("Actualización de calidad falló")
        return None

    except Exception as e:
        print_error(f"Error actualizando calidad: {e}")
        return None


def test_obtener_participantes(videollamada_id: str) -> list[dict[str, Any]]:
    """Test 9: Obtener participantes activos."""
    print_section("Test 9: Obtener Participantes Activos")

    try:
        response = requests.get(
            f"{VIDEOLLAMADAS_URL}/{videollamada_id}/participants",
            headers=get_headers(),
            timeout=5,
        )
        print_response(response)

        if response.status_code == 200:
            participantes = response.json()
            print_success(f"Participantes activos: {len(participantes)}")
            return participantes

        print_error("Obtención de participantes falló")
        return []

    except Exception as e:
        print_error(f"Error obteniendo participantes: {e}")
        return []


def test_salir_de_videollamada(videollamada_id: str) -> bool:
    """Test 10: Salir de videollamada."""
    print_section("Test 10: Salir de Videollamada")

    try:
        response = requests.post(
            f"{VIDEOLLAMADAS_URL}/{videollamada_id}/leave",
            headers=get_headers(),
            timeout=5,
        )
        print_response(response)

        if response.status_code == 200:
            print_success("Salida exitosa de videollamada")
            return True

        print_error("Salida de videollamada falló")
        return False

    except Exception as e:
        print_error(f"Error saliendo de videollamada: {e}")
        return False


def test_agregar_grabacion(videollamada_id: str) -> dict[str, Any] | None:
    """Test 11: Agregar grabación."""
    print_section("Test 11: Agregar Grabación")

    payload = {
        "titulo": "Grabación de prueba",
        "archivo_url": "https://cdn.example.com/recordings/test_rec_001.mp4",
        "formato": "mp4",
        "calidad": "FHD",
        "duracion_segundos": 3600,
        "tamano_bytes": 524288000,
    }

    try:
        response = requests.post(
            f"{VIDEOLLAMADAS_URL}/{videollamada_id}/recordings",
            json=payload,
            headers=get_headers(),
            timeout=10,
        )
        print_response(response)

        if response.status_code == 201:
            data = response.json()
            print_success(f"Grabación agregada: {data.get('id')}")
            print_info(f"Formato: {data.get('formato')} - Calidad: {data.get('calidad')}")
            return data

        print_error("Agregar grabación falló")
        print_info("Nota: Solo moderadores pueden agregar grabaciones")
        return None

    except Exception as e:
        print_error(f"Error agregando grabación: {e}")
        return None


def test_obtener_grabaciones(videollamada_id: str) -> list[dict[str, Any]]:
    """Test 12: Obtener grabaciones."""
    print_section("Test 12: Obtener Grabaciones")

    try:
        response = requests.get(
            f"{VIDEOLLAMADAS_URL}/{videollamada_id}/recordings",
            headers=get_headers(),
            timeout=5,
        )
        print_response(response)

        if response.status_code == 200:
            grabaciones = response.json()
            print_success(f"Grabaciones encontradas: {len(grabaciones)}")
            return grabaciones

        print_error("Obtención de grabaciones falló")
        return []

    except Exception as e:
        print_error(f"Error obteniendo grabaciones: {e}")
        return []


def test_actualizar_transcripcion(videollamada_id: str) -> dict[str, Any] | None:
    """Test 13: Actualizar transcripción."""
    print_section("Test 13: Actualizar Transcripción")

    payload = {
        "transcripcion": "John Doe: Buenos días a todos.\nJane Smith: Hola, ¿cómo están?"
    }

    try:
        response = requests.patch(
            f"{VIDEOLLAMADAS_URL}/{videollamada_id}/transcription",
            json=payload,
            headers=get_headers(),
            timeout=5,
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            print_success("Transcripción actualizada")
            return data

        print_error("Actualización de transcripción falló")
        print_info("Nota: Solo moderadores pueden actualizar transcripción")
        return None

    except Exception as e:
        print_error(f"Error actualizando transcripción: {e}")
        return None


def test_finalizar_videollamada(videollamada_id: str) -> dict[str, Any] | None:
    """Test 14: Finalizar videollamada."""
    print_section("Test 14: Finalizar Videollamada")

    payload = {"resumen_ia": "Reunión exitosa sobre planificación del proyecto Q4."}

    try:
        response = requests.post(
            f"{VIDEOLLAMADAS_URL}/{videollamada_id}/finalize",
            json=payload,
            headers=get_headers(),
            timeout=10,
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            print_success("Videollamada finalizada")
            print_info(f"Estado: {data.get('estado')}")
            print_info(f"Duración: {data.get('duracion_segundos')} segundos")
            return data

        print_error("Finalización de videollamada falló")
        print_info("Nota: Solo moderadores pueden finalizar")
        return None

    except Exception as e:
        print_error(f"Error finalizando videollamada: {e}")
        return None


# ===============================
# Función Principal
# ===============================


def main() -> None:
    """Ejecuta todos los tests de API."""
    print_section("🚀 INICIO DE PRUEBAS - API VIDEOLLAMADAS JITSI")

    # Contador de resultados
    tests_passed = 0
    tests_failed = 0

    # Test 1: Health Check
    if test_health_check():
        tests_passed += 1
    else:
        tests_failed += 1
        print_error("Health check falló. Verifica que el backend esté corriendo.")
        print_info("Continuando con otros tests...")

    # Nota sobre autenticación
    print_section("⚠️ NOTA SOBRE AUTENTICACIÓN")
    print_info("Este script requiere autenticación JWT.")
    print_info("Antes de continuar, necesitas:")
    print_info("1. Iniciar sesión en el sistema")
    print_info("2. Obtener un token JWT válido")
    print_info("3. Configurar AUTH_TOKEN en este script")
    print_info("")
    print_info("Por ahora, ejecutaremos tests que no requieren autenticación.")

    # Test 2: Generate room name (sin auth para demo)
    print_info("\nIntentando generar room name sin autenticación...")
    room_name = test_generate_room_name()

    # Resumen final
    print_section("📊 RESUMEN DE PRUEBAS")
    print(f"\nTests ejecutados: {tests_passed + tests_failed}")
    print(f"✅ Exitosos: {tests_passed}")
    print(f"❌ Fallidos: {tests_failed}")

    print_section("🔑 PRÓXIMOS PASOS")
    print("1. Configurar autenticación JWT (AUTH_TOKEN)")
    print("2. Crear usuario de prueba en la base de datos")
    print("3. Ejecutar script completo con autenticación")
    print("4. Verificar todos los endpoints funcionan correctamente")
    print("")
    print("📚 Documentación completa en:")
    print("   Docs/FASE_2_VIDEOLLAMADAS_JITSI_COMPLETADA.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Pruebas interrumpidas por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
