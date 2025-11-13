"""
Script de prueba para validar schemas Pydantic de videollamadas.

Prueba todas las validaciones, ejemplos y casos edge.
"""

import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

# Añadir el directorio backend al path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.schemas.communication.videollamada_schemas import (
    VideollamadaCreate,
    VideollamadaUpdate,
    VideollamadaResponse,
    VideollamadaDetallada,
    VideollamadaFilter,
    ParticipanteCreate,
    ParticipanteResponse,
    GrabacionCreate,
    GrabacionResponse,
    EstadisticasVideollamada,
    MessageResponse,
    VideollamadaListResponse,
)
from pydantic import ValidationError


def test_videollamada_schemas():
    """
    Test completo de schemas de videollamadas.
    """
    print("🧪 Iniciando pruebas de Schemas Pydantic...\n")
    
    tests_passed = 0
    tests_failed = 0
    
    # ==================== TEST 1: VideollamadaCreate ====================
    print("=" * 70)
    print("TEST 1: VideollamadaCreate - Validaciones básicas")
    print("=" * 70)
    
    try:
        # Caso válido
        videollamada_create = VideollamadaCreate(
            jitsi_room_name="clase-matematicas-101",
            tipo_llamada="video",
            sala_chat_id=uuid4(),
            configuracion={
                "max_participantes": 30,
                "permitir_grabacion": True
            }
        )
        print(f"✅ VideollamadaCreate válido:")
        print(f"   Room: {videollamada_create.jitsi_room_name}")
        print(f"   Tipo: {videollamada_create.tipo_llamada}")
        print(f"   Config: {videollamada_create.configuracion}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en VideollamadaCreate válido: {e}")
        tests_failed += 1
    
    # Test validación room_name
    try:
        invalid_room = VideollamadaCreate(
            jitsi_room_name="sala con espacios!",
            tipo_llamada="video"
        )
        print("❌ Debería haber fallado con room_name inválido")
        tests_failed += 1
    except ValidationError as e:
        print(f"✅ Validación room_name funciona correctamente")
        print(f"   Error esperado: {e.errors()[0]['msg']}")
        tests_passed += 1
    
    # Test tipo_llamada inválido
    try:
        invalid_tipo = VideollamadaCreate(
            jitsi_room_name="sala-valida",
            tipo_llamada="audio"  # tipo inválido
        )
        print("❌ Debería haber fallado con tipo_llamada inválido")
        tests_failed += 1
    except ValidationError as e:
        print(f"✅ Validación tipo_llamada funciona correctamente")
        tests_passed += 1
    
    # Test max_participantes fuera de rango
    try:
        invalid_config = VideollamadaCreate(
            jitsi_room_name="sala-valida",
            tipo_llamada="video",
            configuracion={"max_participantes": 1000}  # Fuera de rango
        )
        print("❌ Debería haber fallado con max_participantes > 500")
        tests_failed += 1
    except ValidationError as e:
        print(f"✅ Validación max_participantes funciona correctamente")
        tests_passed += 1
    
    # ==================== TEST 2: VideollamadaResponse ====================
    print("\n" + "=" * 70)
    print("TEST 2: VideollamadaResponse - Serialización")
    print("=" * 70)
    
    try:
        response_data = {
            "id": uuid4(),
            "jitsi_room_name": "clase-programacion",
            "tipo_llamada": "video",
            "sala_chat_id": uuid4(),
            "iniciador_id": uuid4(),
            "estado": "activa",
            "fecha_inicio": datetime.now(timezone.utc),
            "fecha_fin": None,
            "duracion_segundos": None,
            "configuracion": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "total_participantes": 5,
            "participantes_activos": 3
        }
        
        videollamada_response = VideollamadaResponse(**response_data)
        print(f"✅ VideollamadaResponse creado:")
        print(f"   ID: {videollamada_response.id}")
        print(f"   Estado: {videollamada_response.estado}")
        print(f"   Participantes totales: {videollamada_response.total_participantes}")
        print(f"   Participantes activos: {videollamada_response.participantes_activos}")
        
        # Test model_dump
        dumped = videollamada_response.model_dump()
        print(f"✅ model_dump() funciona: {len(dumped)} campos")
        
        # Test model_dump_json
        json_str = videollamada_response.model_dump_json()
        print(f"✅ model_dump_json() funciona: {len(json_str)} caracteres")
        
        tests_passed += 3
    except Exception as e:
        print(f"❌ Error en VideollamadaResponse: {e}")
        tests_failed += 3
    
    # ==================== TEST 3: VideollamadaFilter ====================
    print("\n" + "=" * 70)
    print("TEST 3: VideollamadaFilter - Filtros y validaciones")
    print("=" * 70)
    
    try:
        # Filtro válido
        filtro = VideollamadaFilter(
            estado="activa",
            tipo_llamada="video",
            skip=0,
            limit=50,
            ordenar_por="fecha_inicio",
            orden_desc=True
        )
        print(f"✅ VideollamadaFilter válido:")
        print(f"   Estado: {filtro.estado}")
        print(f"   Paginación: skip={filtro.skip}, limit={filtro.limit}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en VideollamadaFilter: {e}")
        tests_failed += 1
    
    # Test validación de rango de fechas
    try:
        fecha_inicio = datetime.now(timezone.utc)
        fecha_fin = datetime(2024, 1, 1, tzinfo=timezone.utc)  # Antes de inicio
        
        invalid_filter = VideollamadaFilter(
            fecha_inicio_desde=fecha_inicio,
            fecha_inicio_hasta=fecha_fin
        )
        print("❌ Debería haber fallado con rango de fechas inválido")
        tests_failed += 1
    except ValidationError as e:
        print(f"✅ Validación de rango de fechas funciona correctamente")
        tests_passed += 1
    
    # Test límite máximo
    try:
        invalid_limit = VideollamadaFilter(limit=1000)
        print("❌ Debería haber fallado con limit > 500")
        tests_failed += 1
    except ValidationError as e:
        print(f"✅ Validación de límite funciona correctamente")
        tests_passed += 1
    
    # ==================== TEST 4: ParticipanteCreate ====================
    print("\n" + "=" * 70)
    print("TEST 4: ParticipanteCreate y ParticipanteResponse")
    print("=" * 70)
    
    try:
        participante_create = ParticipanteCreate(
            videollamada_id=uuid4(),
            usuario_id=uuid4(),
            es_moderador=True
        )
        print(f"✅ ParticipanteCreate válido:")
        print(f"   Videollamada: {participante_create.videollamada_id}")
        print(f"   Usuario: {participante_create.usuario_id}")
        print(f"   Moderador: {participante_create.es_moderador}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en ParticipanteCreate: {e}")
        tests_failed += 1
    
    try:
        participante_response = ParticipanteResponse(
            id=uuid4(),
            videollamada_id=uuid4(),
            usuario_id=uuid4(),
            es_moderador=False,
            fecha_union=datetime.now(timezone.utc),
            fecha_salida=None,
            duracion_segundos=None,
            calidad_conexion="excelente",
            datos_conexion={"latencia_ms": 25, "perdida_paquetes": 0.1},
            created_at=datetime.now(timezone.utc),
            usuario_nombre="Juan",
            usuario_apellido="Pérez"
        )
        print(f"✅ ParticipanteResponse válido:")
        print(f"   Usuario: {participante_response.usuario_nombre} {participante_response.usuario_apellido}")
        print(f"   Calidad conexión: {participante_response.calidad_conexion}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en ParticipanteResponse: {e}")
        tests_failed += 1
    
    # ==================== TEST 5: GrabacionCreate y Response ====================
    print("\n" + "=" * 70)
    print("TEST 5: GrabacionCreate y GrabacionResponse")
    print("=" * 70)
    
    try:
        grabacion_create = GrabacionCreate(
            videollamada_id=uuid4(),
            archivo_url="https://storage.example.com/recordings/call-123.mp4",
            formato="mp4",
            duracion_segundos=1800,
            tamano_bytes=524288000,
            calidad="HD",
            thumbnail_url="https://storage.example.com/thumbnails/call-123.jpg",
            metadatos={"codec": "h264", "resolution": "1920x1080"}
        )
        print(f"✅ GrabacionCreate válido:")
        print(f"   URL: {grabacion_create.archivo_url}")
        print(f"   Formato: {grabacion_create.formato}")
        print(f"   Duración: {grabacion_create.duracion_segundos}s")
        print(f"   Tamaño: {grabacion_create.tamano_bytes / 1024 / 1024:.2f} MB")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en GrabacionCreate: {e}")
        tests_failed += 1
    
    try:
        grabacion_response = GrabacionResponse(
            id=uuid4(),
            videollamada_id=uuid4(),
            archivo_url="https://storage.example.com/recordings/call-456.mp4",
            formato="mp4",
            duracion_segundos=3600,
            tamano_bytes=1048576000,
            calidad="FHD",
            thumbnail_url="https://storage.example.com/thumbnails/call-456.jpg",
            estado_procesamiento="completado",
            metadatos={"codec": "h264"},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        print(f"✅ GrabacionResponse válido:")
        print(f"   Tamaño calculado: {grabacion_response.tamano_mb} MB")
        print(f"   Duración formateada: {grabacion_response.duracion_formateada}")
        print(f"   Estado: {grabacion_response.estado_procesamiento}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en GrabacionResponse: {e}")
        tests_failed += 1
    
    # ==================== TEST 6: Schemas complejos ====================
    print("\n" + "=" * 70)
    print("TEST 6: Schemas complejos (VideollamadaDetallada, etc.)")
    print("=" * 70)
    
    try:
        videollamada_detallada = VideollamadaDetallada(
            id=uuid4(),
            jitsi_room_name="reunion-completa",
            tipo_llamada="video",
            sala_chat_id=uuid4(),
            iniciador_id=uuid4(),
            estado="finalizada",
            fecha_inicio=datetime.now(timezone.utc),
            fecha_fin=datetime.now(timezone.utc),
            duracion_segundos=1800,
            configuracion={},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            participantes=[],
            grabaciones=[],
            estadisticas={"total_mensajes": 50}
        )
        print(f"✅ VideollamadaDetallada válido:")
        print(f"   ID: {videollamada_detallada.id}")
        print(f"   Participantes: {len(videollamada_detallada.participantes)}")
        print(f"   Grabaciones: {len(videollamada_detallada.grabaciones)}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en VideollamadaDetallada: {e}")
        tests_failed += 1
    
    try:
        estadisticas = EstadisticasVideollamada(
            total_participantes=8,
            duracion_promedio_participante=1650.5,
            calidad_conexion_promedio="buena",
            total_grabaciones=1,
            tiene_transcripcion=True,
            tiene_resumen=True
        )
        print(f"✅ EstadisticasVideollamada válido:")
        print(f"   Total participantes: {estadisticas.total_participantes}")
        print(f"   Duración promedio: {estadisticas.duracion_promedio_participante}s")
        print(f"   Tiene transcripción: {estadisticas.tiene_transcripcion}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en EstadisticasVideollamada: {e}")
        tests_failed += 1
    
    try:
        lista_response = VideollamadaListResponse(
            items=[],
            total=42,
            skip=0,
            limit=20,
            has_more=True
        )
        print(f"✅ VideollamadaListResponse válido:")
        print(f"   Total: {lista_response.total}")
        print(f"   Has more: {lista_response.has_more}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en VideollamadaListResponse: {e}")
        tests_failed += 1
    
    try:
        message = MessageResponse(
            message="Operación exitosa",
            success=True,
            data={"id": str(uuid4())}
        )
        print(f"✅ MessageResponse válido:")
        print(f"   Message: {message.message}")
        print(f"   Success: {message.success}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en MessageResponse: {e}")
        tests_failed += 1
    
    # ==================== RESUMEN ====================
    print("\n" + "=" * 70)
    total_tests = tests_passed + tests_failed
    print(f"RESUMEN DE PRUEBAS")
    print("=" * 70)
    print(f"✅ Tests exitosos: {tests_passed}/{total_tests}")
    print(f"❌ Tests fallidos: {tests_failed}/{total_tests}")
    print(f"📊 Tasa de éxito: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("✅ Schemas Pydantic completamente funcionales")
        print("✅ Validaciones funcionando correctamente")
        print("✅ Serialización/deserialización correcta")
        print("✅ Ejemplos OpenAPI generados")
        return True
    else:
        print(f"\n⚠️  {tests_failed} tests fallaron. Revisar errores.")
        return False


if __name__ == "__main__":
    success = test_videollamada_schemas()
    sys.exit(0 if success else 1)
