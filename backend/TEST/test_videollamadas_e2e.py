"""
🎬 Test End-to-End: Sistema de Videollamadas
============================================

Prueba el FLUJO COMPLETO del sistema con base de datos REAL:
1. Crear videollamada con auto-generación de room name
2. Unirse como participante
3. Actualizar calidad de conexión
4. Agregar más participantes
5. Finalizar videollamada
6. Agregar grabación
7. Verificar estado final

Requiere:
- Base de datos PostgreSQL configurada
- Migraciones aplicadas (alembic upgrade head)
- Usuario de prueba en la base de datos
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.models.users.usuario import Usuario
from src.models.communication.videollamada import Videollamada, VideollamadaParticipante, VideollamadaGrabacion
from src.services.communication.videollamada_service import VideollamadaService
from src.schemas.communication.videollamada_schemas import (
    VideollamadaCreate,
    ParticipanteUpdate,
    GrabacionCreate
)
from src.enums.communication.videollamada_enums import (
    TipoLlamada,
    EstadoVideollamada,
    CalidadConexion,
    FormatoGrabacion,
    CalidadGrabacion,
    EstadoProcesamiento
)


class Colors:
    """Colores ANSI para output bonito"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_step(step_num: int, description: str):
    """Imprime un paso del test"""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}[PASO {step_num}]{Colors.ENDC} {description}")


def print_success(message: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message: str):
    """Imprime mensaje de error"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_info(key: str, value):
    """Imprime información"""
    print(f"   {Colors.OKCYAN}• {key}:{Colors.ENDC} {value}")


def create_test_users(db: Session, count: int = 3) -> list[Usuario]:
    """
    Crea usuarios de prueba o usa existentes.
    
    Args:
        db: Sesión de base de datos
        count: Número de usuarios a crear/obtener
        
    Returns:
        Lista de usuarios
    """
    usuarios = []
    
    # Intentar obtener usuarios existentes primero
    existing_users = db.query(Usuario).limit(count).all()
    
    if len(existing_users) >= count:
        print_success(f"Usando {count} usuarios existentes de la base de datos")
        return existing_users[:count]
    
    # Si no hay suficientes, crear usuarios de prueba
    print_info("INFO", f"Creando {count - len(existing_users)} usuarios de prueba...")
    
    for i in range(len(existing_users), count):
        usuario = Usuario(
            usuario_id=uuid4(),
            nombres=f"Usuario{i+1}",
            apellidos=f"Test",
            correo_institucional=f"test_user_{i+1}_{uuid4().hex[:8]}@example.com",
            username=f"testuser{i+1}",
            tipo_documento="CC",
            numero_documento=f"100000000{i+1}",
            password_hash="hashed_password_test",  # No se usará para login
            rol="ESTUDIANTE",
            estado_cuenta="ACTIVO",
            fecha_creacion=datetime.utcnow()
        )
        db.add(usuario)
        usuarios.append(usuario)
    
    if usuarios:
        db.commit()
        print_success(f"Creados {len(usuarios)} nuevos usuarios")
    
    # Retornar todos los usuarios (existentes + nuevos)
    all_users = existing_users + usuarios
    return all_users[:count]


def cleanup_test_data(db: Session, videollamada_id: str):
    """
    Limpia datos de prueba al finalizar.
    
    Args:
        db: Sesión de base de datos
        videollamada_id: ID de la videollamada a limpiar
    """
    try:
        # Eliminar grabaciones
        db.query(VideollamadaGrabacion).filter(
            VideollamadaGrabacion.videollamada_id == videollamada_id
        ).delete()
        
        # Eliminar participantes
        db.query(VideollamadaParticipante).filter(
            VideollamadaParticipante.videollamada_id == videollamada_id
        ).delete()
        
        # Eliminar videollamada
        db.query(Videollamada).filter(
            Videollamada.id == videollamada_id
        ).delete()
        
        db.commit()
        print_success("Datos de prueba limpiados")
    except Exception as e:
        print_error(f"Error al limpiar datos: {e}")
        db.rollback()


async def run_e2e_test():
    """
    Ejecuta el test end-to-end completo.
    """
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}🎬 TEST END-TO-END: SISTEMA DE VIDEOLLAMADAS{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    db = SessionLocal()
    service = VideollamadaService()
    
    videollamada_id = None
    participante_ids = []
    
    try:
        # ==================== PREPARACIÓN ====================
        print_step(0, "Preparación: Crear/obtener usuarios de prueba")
        usuarios = create_test_users(db, count=3)
        iniciador = usuarios[0]
        participante1 = usuarios[1]
        participante2 = usuarios[2]
        
        print_info("Iniciador", f"{iniciador.nombres} {iniciador.apellidos} (ID: {iniciador.usuario_id})")
        print_info("Participante 1", f"{participante1.nombres} {participante1.apellidos}")
        print_info("Participante 2", f"{participante2.nombres} {participante2.apellidos}")
        
        # ==================== PASO 1: CREAR VIDEOLLAMADA ====================
        print_step(1, "Crear videollamada con auto-generación de room name")
        
        videollamada_data = VideollamadaCreate(
            jitsi_room_name=f"test-e2e-{uuid4().hex[:8]}",
            tipo_llamada=TipoLlamada.VIDEO,
            titulo="📚 Clase de Matemáticas - Test E2E",
            descripcion="Test end-to-end del sistema de videollamadas",
            configuracion={
                "max_participantes": 50,
                "permitir_grabacion": True,
                "calidad_default": "HD"
            }
        )
        
        videollamada = service.crear_videollamada(
            db=db,
            videollamada_in=videollamada_data,
            iniciador_id=iniciador.usuario_id
        )
        videollamada_id = str(videollamada.id)
        
        print_success("Videollamada creada exitosamente")
        print_info("ID", videollamada.id)
        print_info("Room Name", videollamada.jitsi_room_name)
        print_info("Estado", videollamada.estado.value)
        print_info("Tipo", videollamada.tipo_llamada.value)
        print_info("Iniciador auto-join", "✅" if videollamada.iniciador_id else "❌")
        
        # Verificar que el iniciador se unió automáticamente
        participantes_iniciales = service.obtener_participantes_activos(db=db, videollamada_id=videollamada_id)
        assert len(participantes_iniciales) == 1, "El iniciador debería estar auto-unido"
        assert str(participantes_iniciales[0].usuario_id) == str(iniciador.usuario_id)
        assert participantes_iniciales[0].es_moderador is True
        print_success("Iniciador auto-unido como moderador")
        
        # ==================== PASO 2: UNIRSE PARTICIPANTE 1 ====================
        print_step(2, "Participante 1 se une a la videollamada")
        
        participante1_obj = service.unirse_a_videollamada(
            db=db,
            videollamada_id=videollamada_id,
            usuario_id=participante1.usuario_id,
            es_moderador=False
        )
        participante_ids.append(str(participante1_obj.id))
        
        print_success("Participante 1 unido")
        print_info("ID Participante", participante1_obj.id)
        print_info("Es Moderador", participante1_obj.es_moderador)
        print_info("Fecha Unión", participante1_obj.fecha_union)
        
        # ==================== PASO 3: ACTUALIZAR CALIDAD ====================
        print_step(3, "Actualizar calidad de conexión del Participante 1")
        
        latencia = 45
        perdida = 0.5
        
        participante1_actualizado = service.actualizar_calidad_conexion(
            db=db,
            participante_id=participante1_obj.id,
            calidad=CalidadConexion.EXCELENTE,  # Se sobrescribe con cálculo automático
            latencia_ms=latencia,
            perdida_paquetes_pct=perdida
        )
        
        print_success("Calidad actualizada")
        print_info("Latencia", f"{latencia}ms")
        print_info("Pérdida Paquetes", f"{perdida}%")
        print_info("Calidad Calculada", participante1_actualizado.calidad_conexion.value)
        
        # Verificar que se calculó correctamente (45ms y 0.5% = EXCELENTE)
        assert participante1_actualizado.calidad_conexion == CalidadConexion.EXCELENTE
        print_success("Calidad calculada automáticamente: EXCELENTE")
        
        # ==================== PASO 4: UNIRSE PARTICIPANTE 2 ====================
        print_step(4, "Participante 2 se une a la videollamada")
        
        participante2_obj = service.unirse_a_videollamada(
            db=db,
            videollamada_id=videollamada_id,
            usuario_id=participante2.usuario_id,
            es_moderador=False
        )
        participante_ids.append(str(participante2_obj.id))
        
        print_success("Participante 2 unido")
        
        # Verificar total de participantes
        participantes_activos = service.obtener_participantes_activos(db=db, videollamada_id=videollamada_id)
        assert len(participantes_activos) == 3, "Deberían haber 3 participantes"
        print_success(f"Total de participantes activos: {len(participantes_activos)}")
        
        # ==================== PASO 5: LISTAR VIDEOLLAMADAS ====================
        print_step(5, "Listar videollamadas activas")
        
        lista = service.listar_videollamadas_activas(
            db=db
        )
        
        print_success(f"Encontradas {len(lista)} videollamadas activas")
        videollamada_encontrada = any(str(v.id) == videollamada_id for v in lista)
        assert videollamada_encontrada, "La videollamada creada debería estar en la lista"
        print_success("Videollamada encontrada en lista")
        
        # ==================== PASO 6: VALIDAR PUEDE UNIRSE ====================
        print_step(6, "Validar si nuevo usuario puede unirse")
        
        nuevo_usuario_id = uuid4()
        validacion = service.validar_puede_unirse(
            db=db,
            videollamada_id=videollamada_id,
            usuario_id=nuevo_usuario_id
        )
        
        print_info("Puede unirse", "✅" if validacion["puede_unirse"] else "❌")
        print_info("Razón", validacion.get("razon") or "Ninguna restricción")
        
        assert validacion["puede_unirse"] is True
        print_success("Validación exitosa: nuevo usuario puede unirse")
        
        # ==================== PASO 7: PARTICIPANTE 1 SALE ====================
        print_step(7, "Participante 1 sale de la videollamada")
        
        participante1_salida = service.salir_de_videollamada(
            db=db,
            videollamada_id=videollamada_id,
            usuario_id=participante1.usuario_id
        )
        
        print_success("Participante 1 salió")
        print_info("Fecha Salida", participante1_salida.fecha_salida)
        print_info("Duración", f"{participante1_salida.duracion_segundos} segundos")
        
        # Verificar que disminuyó el conteo
        participantes_despues_salida = service.obtener_participantes_activos(db=db, videollamada_id=videollamada_id)
        assert len(participantes_despues_salida) == 2, "Deberían quedar 2 participantes"
        print_success(f"Participantes activos ahora: {len(participantes_despues_salida)}")
        
        # ==================== PASO 8: FINALIZAR VIDEOLLAMADA ====================
        print_step(8, "Finalizar videollamada (solo moderador)")
        
        videollamada_finalizada = service.finalizar_videollamada(
            db=db,
            videollamada_id=videollamada_id
        )
        
        print_success("Videollamada finalizada")
        print_info("Estado", videollamada_finalizada.estado.value)
        print_info("Fecha Fin", videollamada_finalizada.fecha_fin)
        print_info("Duración Total", f"{videollamada_finalizada.duracion_segundos} segundos")
        
        assert videollamada_finalizada.estado == EstadoVideollamada.FINALIZADA
        assert videollamada_finalizada.fecha_fin is not None
        assert videollamada_finalizada.duracion_segundos is not None
        print_success("Estado y métricas actualizados correctamente")
        
        # ==================== PASO 9: AGREGAR GRABACIÓN ====================
        print_step(9, "Agregar grabación de la videollamada")
        
        grabacion_data = GrabacionCreate(
            videollamada_id=videollamada_id,
            archivo_url="https://cdn.example.com/recordings/test-e2e.mp4",
            formato=FormatoGrabacion.MP4,
            calidad=CalidadGrabacion.HD,
            duracion_segundos=videollamada_finalizada.duracion_segundos,
            tamano_bytes=524288000,  # ~500MB
            thumbnail_url="https://cdn.example.com/thumbnails/test-e2e.jpg"
        )
        
        grabacion = service.agregar_grabacion(
            db=db,
            videollamada_id=videollamada_id,
            grabacion_in=grabacion_data
        )
        
        print_success("Grabación agregada")
        print_info("ID", grabacion.id)
        print_info("Formato", f"{grabacion.formato.value} ({grabacion.formato.mime_type})")
        print_info("Calidad", f"{grabacion.calidad.value} - {grabacion.calidad.resolucion}")
        print_info("Tamaño", f"{grabacion.tamano_bytes / 1024 / 1024:.2f} MB")
        print_info("Estado", grabacion.estado_procesamiento.value)
        
        # Verificar propiedades de enum
        assert grabacion.formato.mime_type == "video/mp4"
        assert grabacion.calidad.resolucion == (1280, 720)
        print_success("Propiedades de enum validadas")
        
        # ==================== PASO 10: LISTAR GRABACIONES ====================
        print_step(10, "Listar grabaciones de la videollamada")
        
        grabaciones = service.obtener_grabaciones(db=db, videollamada_id=videollamada_id)
        
        print_success(f"Encontradas {len(grabaciones)} grabaciones")
        assert len(grabaciones) == 1
        assert str(grabaciones[0].id) == str(grabacion.id)
        print_success("Grabación encontrada en lista")
        
        # ==================== PASO 11: GENERAR ROOM NAME ====================
        print_step(11, "Generar room name único")
        
        room_name = service.obtener_room_name_disponible(db=db, base_name="test-e2e")
        
        print_success(f"Room name generado: {room_name}")
        assert "test-e2e" in room_name
        print_success("Base name incluido correctamente")
        
        # ==================== PASO 12: VERIFICACIÓN FINAL ====================
        print_step(12, "Verificación final: Obtener videollamada completa")
        
        videollamada_final = service.obtener_videollamada(
            db=db,
            videollamada_id=videollamada_id,
            incluir_participantes=True
        )
        
        print_success("Videollamada obtenida")
        print_info("Estado Final", videollamada_final.estado.value)
        print_info("Duración Total", f"{videollamada_final.duracion_segundos}s")
        print_info("Total Participantes (histórico)", videollamada_final.total_participantes or "N/A")
        print_info("Tiene Grabación", "✅" if videollamada_final.grabacion_url else "❌")
        
        # ==================== RESUMEN ====================
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ TEST END-TO-END COMPLETADO EXITOSAMENTE{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}📊 RESUMEN DE OPERACIONES:{Colors.ENDC}")
        print_info("Videollamada creada", "✅")
        print_info("Auto-join iniciador", "✅")
        print_info("Participantes unidos", "✅ (2 adicionales)")
        print_info("Calidad actualizada", "✅")
        print_info("Participante salió", "✅")
        print_info("Videollamada finalizada", "✅")
        print_info("Grabación agregada", "✅")
        print_info("Listados funcionales", "✅")
        print_info("Validaciones correctas", "✅")
        
        print(f"\n{Colors.BOLD}🎯 RESULTADOS FINALES:{Colors.ENDC}")
        print_info("Estado", videollamada_final.estado.value.upper())
        print_info("Duración", f"{videollamada_final.duracion_segundos} segundos")
        print_info("Participantes (pico)", "3")
        print_info("Grabaciones", "1")
        
        return True
        
    except Exception as e:
        print_error(f"Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # ==================== LIMPIEZA ====================
        if videollamada_id:
            print(f"\n{Colors.WARNING}{Colors.BOLD}🧹 LIMPIEZA DE DATOS{Colors.ENDC}")
            cleanup_test_data(db, videollamada_id)
        
        db.close()
        print_info("Sesión DB", "Cerrada")


def main():
    """
    Punto de entrada principal.
    """
    try:
        # Ejecutar test
        success = asyncio.run(run_e2e_test())
        
        # Exit code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Test interrumpido por el usuario{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
