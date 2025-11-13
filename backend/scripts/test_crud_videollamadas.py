"""
Script de prueba para validar CRUD de videollamadas.

Este script prueba todas las operaciones CRUD implementadas para videollamadas,
participantes y grabaciones.
"""

import sys
from pathlib import Path

# Añadir el directorio backend al path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime

from src.db.session import engine
from src.crud.communication.videollamada import crud_videollamada
from src.models.communication.videollamada import Videollamada, VideollamadaParticipante, VideollamadaGrabacion


def test_crud_videollamadas():
    """
    Test completo de CRUD videollamadas.
    """
    print("🧪 Iniciando pruebas de CRUD videollamadas...\n")
    
    # Crear sesión
    db = Session(bind=engine)
    
    try:
        # ==================== TEST 1: Crear videollamada ====================
        print("=" * 70)
        print("TEST 1: Crear videollamada")
        print("=" * 70)
        
        # Necesitamos un usuario existente - obtenemos el primero disponible
        from src.models.users.usuario import Usuario
        usuario_test = db.query(Usuario).first()
        
        if not usuario_test:
            print("❌ No hay usuarios en la base de datos. Crea uno primero.")
            return
        
        print(f"📌 Usuario de prueba: {usuario_test.nombres} {usuario_test.apellidos}")
        print(f"   UUID: {usuario_test.usuario_id}")
        
        # Crear videollamada
        room_name = f"test-room-{uuid4().hex[:8]}"
        videollamada = crud_videollamada.create_videollamada(
            db=db,
            jitsi_room_name=room_name,
            tipo_llamada="video",
            iniciador_id=usuario_test.usuario_id,
            configuracion={"test": True, "max_participantes": 10}
        )
        
        print(f"✅ Videollamada creada: {videollamada.id}")
        print(f"   Room: {videollamada.jitsi_room_name}")
        print(f"   Tipo: {videollamada.tipo_llamada}")
        print(f"   Estado: {videollamada.estado}")
        print(f"   Iniciador: {videollamada.iniciador_id}")
        print(f"   Fecha inicio: {videollamada.fecha_inicio}")
        print(f"   Configuración: {videollamada.configuracion}")
        
        # Verificar que se creó el participante iniciador
        participantes = crud_videollamada.get_participantes_activos(db, videollamada.id)
        print(f"✅ Participantes iniciales: {len(participantes)}")
        assert len(participantes) == 1, "Debe haber 1 participante (el iniciador)"
        assert participantes[0].es_moderador == True, "El iniciador debe ser moderador"
        print(f"   - {participantes[0].usuario_id} (moderador: {participantes[0].es_moderador})")
        
        # ==================== TEST 2: Obtener videollamada ====================
        print("\n" + "=" * 70)
        print("TEST 2: Obtener videollamada")
        print("=" * 70)
        
        obtenida = crud_videollamada.get(db, videollamada.id)
        print(f"✅ Videollamada obtenida: {obtenida.id}")
        assert obtenida.jitsi_room_name == room_name
        
        obtenida_con_participantes = crud_videollamada.get_with_participants(db, videollamada.id)
        print(f"✅ Videollamada con participantes: {len(obtenida_con_participantes.participantes)} participantes")
        
        obtenida_por_room = crud_videollamada.get_by_room_name(db, room_name)
        print(f"✅ Videollamada por room_name: {obtenida_por_room.id}")
        assert obtenida_por_room.id == videollamada.id
        
        # ==================== TEST 3: Agregar participantes ====================
        print("\n" + "=" * 70)
        print("TEST 3: Agregar participantes")
        print("=" * 70)
        
        # Obtener más usuarios para pruebas
        usuarios_adicionales = db.query(Usuario).limit(3).all()
        
        for i, usuario in enumerate(usuarios_adicionales[1:], 1):  # Saltar el primero (ya es participante)
            participante = crud_videollamada.agregar_participante(
                db=db,
                videollamada_id=videollamada.id,
                usuario_id=usuario.usuario_id,
                es_moderador=(i == 1)  # El primero es moderador
            )
            print(f"✅ Participante {i} agregado: {usuario.nombres} (moderador: {participante.es_moderador})")
        
        participantes_activos = crud_videollamada.get_participantes_activos(db, videollamada.id)
        print(f"✅ Total participantes activos: {len(participantes_activos)}")
        
        # ==================== TEST 4: Obtener videollamadas activas ====================
        print("\n" + "=" * 70)
        print("TEST 4: Obtener videollamadas activas")
        print("=" * 70)
        
        activas = crud_videollamada.get_activas(db)
        print(f"✅ Videollamadas activas: {len(activas)}")
        for i, v in enumerate(activas[:5], 1):
            print(f"   {i}. {v.jitsi_room_name} (estado: {v.estado})")
        
        por_iniciador = crud_videollamada.get_by_iniciador(db, usuario_test.usuario_id)
        print(f"✅ Videollamadas del iniciador: {len(por_iniciador)}")
        
        # ==================== TEST 5: Actualizar transcripción ====================
        print("\n" + "=" * 70)
        print("TEST 5: Actualizar transcripción")
        print("=" * 70)
        
        transcripcion_test = "Esta es una transcripción de prueba de la videollamada."
        videollamada_con_transcripcion = crud_videollamada.actualizar_transcripcion(
            db=db,
            videollamada_id=videollamada.id,
            transcripcion=transcripcion_test
        )
        print(f"✅ Transcripción actualizada:")
        print(f"   {videollamada_con_transcripcion.transcripcion[:50]}...")
        assert videollamada_con_transcripcion.transcripcion == transcripcion_test
        
        # ==================== TEST 6: Agregar grabación ====================
        print("\n" + "=" * 70)
        print("TEST 6: Agregar grabación")
        print("=" * 70)
        
        grabacion = crud_videollamada.agregar_grabacion(
            db=db,
            videollamada_id=videollamada.id,
            archivo_url="https://storage.example.com/recordings/test.mp4",
            formato="mp4",
            duracion_segundos=1800,  # 30 minutos
            tamano_bytes=524288000,  # 500 MB
            calidad="HD",
            thumbnail_url="https://storage.example.com/thumbnails/test.jpg",
            metadatos={"codec": "h264", "resolution": "1920x1080"}
        )
        
        print(f"✅ Grabación agregada: {grabacion.id}")
        print(f"   URL: {grabacion.archivo_url}")
        print(f"   Formato: {grabacion.formato}")
        print(f"   Duración: {grabacion.duracion_segundos}s")
        print(f"   Tamaño: {grabacion.tamano_bytes / 1024 / 1024:.2f} MB")
        print(f"   Calidad: {grabacion.calidad}")
        
        grabaciones = crud_videollamada.get_grabaciones(db, videollamada.id)
        print(f"✅ Total grabaciones: {len(grabaciones)}")
        
        # ==================== TEST 7: Remover participante ====================
        print("\n" + "=" * 70)
        print("TEST 7: Remover participante")
        print("=" * 70)
        
        if len(participantes_activos) > 1:
            participante_a_remover = participantes_activos[-1]
            removido = crud_videollamada.remover_participante(
                db=db,
                videollamada_id=videollamada.id,
                usuario_id=participante_a_remover.usuario_id
            )
            print(f"✅ Participante removido: {participante_a_remover.usuario_id}")
            print(f"   Fecha salida: {removido.fecha_salida}")
            print(f"   Duración participación: {removido.duracion_segundos}s")
            
            participantes_despues = crud_videollamada.get_participantes_activos(db, videollamada.id)
            print(f"✅ Participantes activos restantes: {len(participantes_despues)}")
            assert len(participantes_despues) == len(participantes_activos) - 1
        
        # ==================== TEST 8: Finalizar videollamada ====================
        print("\n" + "=" * 70)
        print("TEST 8: Finalizar videollamada")
        print("=" * 70)
        
        resumen_test = "Esta videollamada fue muy productiva. Se discutieron los siguientes temas..."
        videollamada_finalizada = crud_videollamada.finalizar_llamada(
            db=db,
            videollamada_id=videollamada.id,
            resumen_ia=resumen_test
        )
        
        print(f"✅ Videollamada finalizada: {videollamada_finalizada.id}")
        print(f"   Estado: {videollamada_finalizada.estado}")
        print(f"   Fecha fin: {videollamada_finalizada.fecha_fin}")
        print(f"   Duración total: {videollamada_finalizada.duracion_segundos}s")
        print(f"   Resumen IA: {videollamada_finalizada.resumen_ia[:50]}...")
        
        assert videollamada_finalizada.estado == "finalizada"
        assert videollamada_finalizada.fecha_fin is not None
        assert videollamada_finalizada.duracion_segundos is not None
        
        # Verificar que todos los participantes se marcaron como salidos
        participantes_final = crud_videollamada.get_participantes_activos(db, videollamada.id)
        print(f"✅ Participantes activos después de finalizar: {len(participantes_final)}")
        assert len(participantes_final) == 0, "No debe haber participantes activos después de finalizar"
        
        # ==================== TEST 9: Soft delete ====================
        print("\n" + "=" * 70)
        print("TEST 9: Soft delete")
        print("=" * 70)
        
        eliminada = crud_videollamada.soft_delete(db, videollamada.id)
        print(f"✅ Videollamada eliminada (soft): {eliminada.id}")
        print(f"   deleted_at: {eliminada.deleted_at}")
        assert eliminada.deleted_at is not None
        
        # Verificar que no aparece en consultas normales
        obtenida_despues_delete = crud_videollamada.get(db, videollamada.id)
        print(f"❌ Videollamada no encontrada después de soft delete (esperado): {obtenida_despues_delete is None}")
        assert obtenida_despues_delete is None or obtenida_despues_delete.deleted_at is not None
        
        print("\n" + "=" * 70)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE! 🎉")
        print("=" * 70)
        print("\nResumen:")
        print(f"  ✅ Creación de videollamadas")
        print(f"  ✅ Obtención de videollamadas (múltiples métodos)")
        print(f"  ✅ Agregar participantes")
        print(f"  ✅ Remover participantes")
        print(f"  ✅ Actualizar transcripción")
        print(f"  ✅ Agregar grabaciones")
        print(f"  ✅ Finalizar videollamadas")
        print(f"  ✅ Soft delete")
        print(f"\n🎯 CRUD de videollamadas completamente funcional!")
        
    except Exception as e:
        print(f"\n❌ ERROR en las pruebas:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    test_crud_videollamadas()
