#!/usr/bin/env python3
"""
Test Suite Comprehensivo para VideollamadaService.

Tests de integración que validan:
- Creación completa de videollamadas
- Unirse y salir de llamadas
- Gestión de grabaciones
- Finalización de llamadas
- Estadísticas
- Validaciones y permisos
- Integración con WebSocket
"""

import sys
import asyncio
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from typing import Optional

# Setup path
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.services.videollamada_service import VideollamadaService
from src.schemas.communication.videollamada_schemas import (
    VideollamadaCreate,
    TipoLlamada
)
from src.models.users import usuario as Usuario
from src.crud.user.usuario import crud_usuario


# ===============================
# Test Configuration
# ===============================

class TestContext:
    """Contexto compartido entre tests."""
    def __init__(self):
        self.db: Optional[Session] = None
        self.service: Optional[VideollamadaService] = None
        self.test_usuario: Optional[Usuario] = None
        self.test_usuario_2: Optional[Usuario] = None
        self.videollamada_id: Optional[UUID] = None
        self.participante_id: Optional[UUID] = None
        self.grabacion_id: Optional[UUID] = None
        
        # Contadores
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_total = 0


ctx = TestContext()


# ===============================
# Helper Functions
# ===============================

def print_test_header(test_name: str):
    """Imprimir header del test."""
    print(f"\n{'=' * 70}")
    print(f"  {test_name}")
    print(f"{'=' * 70}")


def print_success(message: str):
    """Imprimir mensaje de éxito."""
    print(f"✅ {message}")


def print_error(message: str):
    """Imprimir mensaje de error."""
    print(f"❌ {message}")


def print_info(message: str):
    """Imprimir mensaje informativo."""
    print(f"ℹ️  {message}")


async def run_test(test_name: str, test_func):
    """
    Ejecutar un test y manejar errores.
    
    Args:
        test_name: Nombre del test
        test_func: Función async del test
    """
    ctx.tests_total += 1
    print_test_header(f"TEST {ctx.tests_total}: {test_name}")
    
    try:
        await test_func()
        ctx.tests_passed += 1
        print_success(f"Test '{test_name}' PASSED")
        return True
    except AssertionError as e:
        ctx.tests_failed += 1
        print_error(f"Test '{test_name}' FAILED: {e}")
        return False
    except Exception as e:
        ctx.tests_failed += 1
        print_error(f"Test '{test_name}' ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


# ===============================
# Setup & Teardown
# ===============================

async def setup():
    """Setup inicial de tests."""
    print("\n" + "=" * 70)
    print("🚀 INICIANDO TEST SUITE - VIDEOLLAMADA SERVICE")
    print("=" * 70)
    
    # Crear sesión de BD
    ctx.db = SessionLocal()
    print_success("Sesión de base de datos creada")
    
    # Crear servicio
    ctx.service = VideollamadaService(ctx.db)
    print_success("VideollamadaService inicializado")
    
    # Obtener o crear usuario de test
    try:
        # Buscar usuario test existente
        usuarios = crud_usuario.get_multi(ctx.db, limit=2)
        if usuarios:
            ctx.test_usuario = usuarios[0]
            print_success(f"Usuario de test obtenido: {ctx.test_usuario.id}")
            
            if len(usuarios) > 1:
                ctx.test_usuario_2 = usuarios[1]
                print_success(f"Usuario de test 2 obtenido: {ctx.test_usuario_2.id}")
        else:
            print_error("No hay usuarios en la base de datos")
            print_info("Por favor crea al menos un usuario para ejecutar los tests")
            return False
    except Exception as e:
        print_error(f"Error obteniendo usuarios: {e}")
        return False
    
    print_success("Setup completado\n")
    return True


async def teardown():
    """Cleanup después de tests."""
    print("\n" + "=" * 70)
    print("🧹 LIMPIEZA")
    print("=" * 70)
    
    if ctx.db:
        ctx.db.close()
        print_success("Sesión de base de datos cerrada")
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE TESTS")
    print("=" * 70)
    print(f"✅ Tests exitosos: {ctx.tests_passed}/{ctx.tests_total}")
    print(f"❌ Tests fallidos: {ctx.tests_failed}/{ctx.tests_total}")
    
    success_rate = (ctx.tests_passed / ctx.tests_total * 100) if ctx.tests_total > 0 else 0
    print(f"📊 Tasa de éxito: {success_rate:.1f}%")
    print("=" * 70 + "\n")
    
    return ctx.tests_failed == 0


# ===============================
# Test Cases
# ===============================

async def test_crear_videollamada_completa():
    """Test: Crear videollamada completa con auto-join."""
    
    # Preparar datos
    videollamada_data = VideollamadaCreate(
        sala_chat_id=uuid4(),
        tipo_llamada=TipoLlamada.VIDEO,
        titulo="Test Videollamada Service",
        descripcion="Videollamada de prueba del service layer",
        jitsi_room_name=f"test-service-{int(datetime.now().timestamp())}",
        fecha_programada=datetime.now() + timedelta(hours=1),
        configuracion={
            "max_participantes": 30,
            "permitir_grabacion": True,
            "activar_sala_espera": False,
            "requerir_contrasena": False
        }
    )
    
    print_info(f"Creando videollamada: {videollamada_data.titulo}")
    
    # Ejecutar
    videollamada, jwt_token = await ctx.service.crear_videollamada_completa(
        videollamada_in=videollamada_data,
        usuario_creador=ctx.test_usuario,
        auto_unir_creador=True
    )
    
    # Guardar ID para otros tests
    ctx.videollamada_id = videollamada.id
    
    # Validaciones
    assert videollamada is not None, "Videollamada no creada"
    assert videollamada.id is not None, "Videollamada sin ID"
    assert videollamada.titulo == videollamada_data.titulo, "Título no coincide"
    assert jwt_token is not None, "JWT token no generado"
    assert len(videollamada.participantes) == 1, "Creador no agregado como participante"
    assert videollamada.participantes[0].es_moderador, "Creador no es moderador"
    
    print_success(f"Videollamada creada: ID={videollamada.id}")
    print_success(f"JWT token generado: {jwt_token[:50]}...")
    print_success(f"Participantes: {len(videollamada.participantes)}")


async def test_unirse_a_videollamada():
    """Test: Segundo usuario se une a la videollamada."""
    
    if not ctx.test_usuario_2:
        print_info("Saltando test - no hay segundo usuario")
        ctx.tests_passed += 1  # No contar como fallido
        return
    
    if not ctx.videollamada_id:
        raise AssertionError("No hay videollamada creada para unirse")
    
    print_info(f"Usuario {ctx.test_usuario_2.id} uniéndose a videollamada {ctx.videollamada_id}")
    
    # Ejecutar
    response = await ctx.service.unirse_a_videollamada(
        videollamada_id=ctx.videollamada_id,
        usuario=ctx.test_usuario_2,
        es_moderador=False
    )
    
    # Guardar ID
    ctx.participante_id = response.id
    
    # Validaciones
    assert response is not None, "Response no generado"
    assert response.id is not None, "Participante sin ID"
    assert str(response.usuario_id) == str(ctx.test_usuario_2.id), "Usuario_id no coincide"
    assert response.es_moderador == False, "No debería ser moderador"
    assert response.jwt_token is not None, "JWT token no generado"
    assert response.jitsi_room_name is not None, "Room name no presente"
    
    print_success(f"Usuario unido: Participante ID={response.id}")
    print_success(f"JWT token generado")
    print_success(f"Room name: {response.jitsi_room_name}")


async def test_unirse_duplicado_falla():
    """Test: Intentar unirse dos veces debe fallar."""
    
    if not ctx.test_usuario_2:
        print_info("Saltando test - no hay segundo usuario")
        ctx.tests_passed += 1
        return
    
    if not ctx.videollamada_id:
        raise AssertionError("No hay videollamada para el test")
    
    print_info("Intentando unirse nuevamente (debería fallar)")
    
    # Ejecutar
    try:
        await ctx.service.unirse_a_videollamada(
            videollamada_id=ctx.videollamada_id,
            usuario=ctx.test_usuario_2,
            es_moderador=False
        )
        raise AssertionError("Debería haber lanzado HTTPException")
    except Exception as e:
        # Esperamos un error 409 Conflict
        assert "409" in str(e) or "participando" in str(e).lower(), f"Error inesperado: {e}"
        print_success("Error esperado capturado: Ya está participando")


async def test_iniciar_grabacion():
    """Test: Iniciar grabación (solo moderador)."""
    
    if not ctx.videollamada_id:
        raise AssertionError("No hay videollamada para el test")
    
    print_info(f"Iniciando grabación en videollamada {ctx.videollamada_id}")
    
    # Ejecutar
    grabacion = await ctx.service.iniciar_grabacion(
        videollamada_id=ctx.videollamada_id,
        usuario_iniciador=ctx.test_usuario,  # Es moderador (creador)
        url_grabacion="https://test.com/recording.mp4"
    )
    
    # Guardar ID
    ctx.grabacion_id = grabacion.id
    
    # Validaciones
    assert grabacion is not None, "Grabación no creada"
    assert grabacion.id is not None, "Grabación sin ID"
    assert str(grabacion.videollamada_id) == str(ctx.videollamada_id), "Videollamada_id no coincide"
    assert str(grabacion.iniciado_por_usuario_id) == str(ctx.test_usuario.id), "Usuario iniciador no coincide"
    assert grabacion.fecha_inicio is not None, "Fecha inicio no establecida"
    assert grabacion.fecha_fin is None, "Fecha fin debería ser None"
    
    print_success(f"Grabación iniciada: ID={grabacion.id}")
    print_success(f"Fecha inicio: {grabacion.fecha_inicio}")


async def test_detener_grabacion():
    """Test: Detener grabación."""
    
    if not ctx.videollamada_id or not ctx.grabacion_id:
        raise AssertionError("No hay grabación para detener")
    
    print_info(f"Deteniendo grabación {ctx.grabacion_id}")
    
    # Esperar un poco para simular grabación
    await asyncio.sleep(2)
    
    # Ejecutar
    grabacion = await ctx.service.detener_grabacion(
        videollamada_id=ctx.videollamada_id,
        grabacion_id=ctx.grabacion_id,
        usuario_detenedor=ctx.test_usuario,
        url_grabacion="https://test.com/recording_final.mp4",
        tamano_bytes=1024 * 1024 * 50  # 50 MB
    )
    
    # Validaciones
    assert grabacion.fecha_fin is not None, "Fecha fin no establecida"
    assert grabacion.duracion_segundos > 0, "Duración no calculada"
    assert grabacion.tamano_bytes == 1024 * 1024 * 50, "Tamaño no actualizado"
    
    print_success(f"Grabación detenida")
    print_success(f"Duración: {grabacion.duracion_segundos} segundos")
    print_success(f"Tamaño: {grabacion.tamano_bytes / (1024*1024):.1f} MB")


async def test_obtener_estadisticas():
    """Test: Obtener estadísticas de videollamada."""
    
    if not ctx.videollamada_id:
        raise AssertionError("No hay videollamada para estadísticas")
    
    print_info(f"Obteniendo estadísticas de videollamada {ctx.videollamada_id}")
    
    # Ejecutar
    estadisticas = ctx.service.obtener_estadisticas(
        videollamada_id=ctx.videollamada_id
    )
    
    # Validaciones
    assert estadisticas is not None, "Estadísticas no generadas"
    assert str(estadisticas.videollamada_id) == str(ctx.videollamada_id), "Videollamada_id no coincide"
    assert estadisticas.total_participantes > 0, "Debería haber participantes"
    assert estadisticas.total_grabaciones > 0, "Debería haber grabaciones"
    
    print_success(f"Total participantes: {estadisticas.total_participantes}")
    print_success(f"Participantes activos: {estadisticas.participantes_activos}")
    print_success(f"Total grabaciones: {estadisticas.total_grabaciones}")
    print_success(f"Duración: {estadisticas.duracion_total_segundos} segundos")


async def test_salir_de_videollamada():
    """Test: Usuario sale de videollamada."""
    
    if not ctx.test_usuario_2:
        print_info("Saltando test - no hay segundo usuario")
        ctx.tests_passed += 1
        return
    
    if not ctx.videollamada_id:
        raise AssertionError("No hay videollamada para salir")
    
    print_info(f"Usuario {ctx.test_usuario_2.id} saliendo de videollamada")
    
    # Ejecutar
    participante = await ctx.service.salir_de_videollamada(
        videollamada_id=ctx.videollamada_id,
        usuario=ctx.test_usuario_2,
        razon="test_completed"
    )
    
    # Validaciones
    assert participante.fecha_salida is not None, "Fecha salida no establecida"
    assert str(participante.usuario_id) == str(ctx.test_usuario_2.id), "Usuario_id no coincide"
    
    print_success(f"Usuario salió exitosamente")
    print_success(f"Fecha salida: {participante.fecha_salida}")


async def test_finalizar_videollamada():
    """Test: Finalizar videollamada (solo moderador)."""
    
    if not ctx.videollamada_id:
        raise AssertionError("No hay videollamada para finalizar")
    
    print_info(f"Finalizando videollamada {ctx.videollamada_id}")
    
    # Ejecutar
    videollamada = await ctx.service.finalizar_videollamada(
        videollamada_id=ctx.videollamada_id,
        usuario_finalizador=ctx.test_usuario,  # Es moderador
        razon="test_completed"
    )
    
    # Validaciones
    assert videollamada.estado == "finalizada", f"Estado debería ser 'finalizada', es '{videollamada.estado}'"
    assert videollamada.fecha_fin is not None, "Fecha fin no establecida"
    
    print_success(f"Videollamada finalizada")
    print_success(f"Estado: {videollamada.estado}")
    print_success(f"Fecha fin: {videollamada.fecha_fin}")


async def test_permisos_no_moderador_falla():
    """Test: Usuario no moderador no puede finalizar."""
    
    if not ctx.test_usuario_2:
        print_info("Saltando test - no hay segundo usuario")
        ctx.tests_passed += 1
        return
    
    # Crear nueva videollamada para este test
    videollamada_data = VideollamadaCreate(
        sala_chat_id=uuid4(),
        tipo_llamada=TipoLlamada.VIDEO,
        titulo="Test Permisos",
        jitsi_room_name=f"test-permisos-{int(datetime.now().timestamp())}",
        configuracion={"max_participantes": 10}
    )
    
    videollamada, _ = await ctx.service.crear_videollamada_completa(
        videollamada_in=videollamada_data,
        usuario_creador=ctx.test_usuario,
        auto_unir_creador=True
    )
    
    # Usuario 2 se une como participante normal
    await ctx.service.unirse_a_videollamada(
        videollamada_id=videollamada.id,
        usuario=ctx.test_usuario_2,
        es_moderador=False
    )
    
    print_info("Usuario no moderador intentando finalizar (debería fallar)")
    
    # Intentar finalizar con usuario no moderador
    try:
        await ctx.service.finalizar_videollamada(
            videollamada_id=videollamada.id,
            usuario_finalizador=ctx.test_usuario_2,  # No es moderador
            razon="unauthorized_test"
        )
        raise AssertionError("Debería haber lanzado HTTPException")
    except Exception as e:
        # Esperamos un error 403 Forbidden
        assert "403" in str(e) or "permisos" in str(e).lower(), f"Error inesperado: {e}"
        print_success("Error esperado capturado: No tiene permisos")
    
    # Limpiar - finalizar con usuario correcto
    await ctx.service.finalizar_videollamada(
        videollamada_id=videollamada.id,
        usuario_finalizador=ctx.test_usuario,
        razon="cleanup"
    )


async def test_validacion_capacidad_maxima():
    """Test: No se puede exceder capacidad máxima."""
    
    # Crear videollamada con capacidad de solo 1 participante
    videollamada_data = VideollamadaCreate(
        sala_chat_id=uuid4(),
        tipo_llamada=TipoLlamada.VIDEO,
        titulo="Test Capacidad Máxima",
        jitsi_room_name=f"test-capacity-{int(datetime.now().timestamp())}",
        configuracion={"max_participantes": 1}  # Solo 1 participante
    )
    
    videollamada, _ = await ctx.service.crear_videollamada_completa(
        videollamada_in=videollamada_data,
        usuario_creador=ctx.test_usuario,
        auto_unir_creador=True  # Ya hay 1 participante
    )
    
    print_info(f"Videollamada con max 1 participante. Intentando agregar segundo (debería fallar)")
    
    if not ctx.test_usuario_2:
        print_info("Saltando validación - no hay segundo usuario")
        ctx.tests_passed += 1
        
        # Limpiar
        await ctx.service.finalizar_videollamada(
            videollamada_id=videollamada.id,
            usuario_finalizador=ctx.test_usuario,
            razon="cleanup"
        )
        return
    
    # Intentar agregar segundo participante (debería fallar)
    try:
        await ctx.service.unirse_a_videollamada(
            videollamada_id=videollamada.id,
            usuario=ctx.test_usuario_2,
            es_moderador=False
        )
        raise AssertionError("Debería haber lanzado HTTPException por capacidad")
    except Exception as e:
        # Esperamos un error 409 con mensaje de capacidad
        assert "409" in str(e) or "capacidad" in str(e).lower(), f"Error inesperado: {e}"
        print_success("Error esperado capturado: Capacidad máxima alcanzada")
    
    # Limpiar
    await ctx.service.finalizar_videollamada(
        videollamada_id=videollamada.id,
        usuario_finalizador=ctx.test_usuario,
        razon="cleanup"
    )


# ===============================
# Main Test Runner
# ===============================

async def main():
    """Ejecutar todos los tests."""
    
    # Setup
    success = await setup()
    if not success:
        print_error("Setup falló. Abortando tests.")
        return False
    
    # Ejecutar tests
    await run_test("Crear Videollamada Completa", test_crear_videollamada_completa)
    await run_test("Unirse a Videollamada", test_unirse_a_videollamada)
    await run_test("Unirse Duplicado Falla", test_unirse_duplicado_falla)
    await run_test("Iniciar Grabación", test_iniciar_grabacion)
    await run_test("Detener Grabación", test_detener_grabacion)
    await run_test("Obtener Estadísticas", test_obtener_estadisticas)
    await run_test("Salir de Videollamada", test_salir_de_videollamada)
    await run_test("Finalizar Videollamada", test_finalizar_videollamada)
    await run_test("Permisos No Moderador Falla", test_permisos_no_moderador_falla)
    await run_test("Validación Capacidad Máxima", test_validacion_capacidad_maxima)
    
    # Teardown
    success = await teardown()
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrumpidos por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
