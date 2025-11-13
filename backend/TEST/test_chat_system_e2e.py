"""
🎬 Test End-to-End: Sistema de Chat y Comunicación
====================================================

Prueba el FLUJO COMPLETO del sistema de chats con base de datos REAL:
1. Crear sala de chat
2. Agregar participantes
3. Enviar mensaje de TEXTO
4. Enviar mensaje con IMAGEN
5. Enviar mensaje con ARCHIVO
6. Enviar mensaje con AUDIO
7. Enviar mensaje con VIDEO
8. Reaccionar a mensajes
9. Mencionar usuarios
10. Marcar como leído
11. Crear hilo de conversación
12. Medir tiempos de respuesta

Requiere:
- Base de datos PostgreSQL configurada
- Usuario de prueba en la base de datos
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.models.users.usuario import Usuario
from src.models.communication.chat import SalaChat, MensajeChat, ParticipanteSala


class Colors:
    """Colores ANSI para output"""
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


def print_timing(action: str, milliseconds: float):
    """Imprime tiempo de ejecución"""
    color = Colors.OKGREEN if milliseconds < 100 else Colors.WARNING if milliseconds < 500 else Colors.FAIL
    print(f"   {color}⏱️  {action}: {milliseconds:.2f}ms{Colors.ENDC}")


def create_test_users(db: Session, count: int = 3) -> list[Usuario]:
    """Obtiene usuarios de prueba existentes"""
    usuarios = db.query(Usuario).limit(count).all()
    
    if len(usuarios) >= count:
        print_success(f"Usando {count} usuarios existentes de la base de datos")
        return usuarios[:count]
    
    print_error(f"Solo hay {len(usuarios)} usuarios. Se necesitan al menos {count}")
    return usuarios


def cleanup_test_data(db: Session, sala_id: str):
    """Limpia datos de prueba"""
    try:
        # Eliminar mensajes
        db.query(MensajeChat).filter(MensajeChat.sala_id == sala_id).delete()
        
        # Eliminar participantes
        db.query(ParticipanteSala).filter(ParticipanteSala.sala_id == sala_id).delete()
        
        # Eliminar sala
        db.query(SalaChat).filter(SalaChat.id == sala_id).delete()
        
        db.commit()
        print_success("Datos de prueba limpiados")
    except Exception as e:
        print_error(f"Error al limpiar datos: {e}")
        db.rollback()


def run_chat_e2e_test():
    """Ejecuta el test end-to-end completo del sistema de chats"""
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}💬 TEST END-TO-END: SISTEMA DE CHAT Y COMUNICACIÓN{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    db = SessionLocal()
    sala_id = None
    tiempos = {}
    
    try:
        # ==================== PREPARACIÓN ====================
        print_step(0, "Preparación: Obtener usuarios de prueba")
        usuarios = create_test_users(db, count=3)
        
        if len(usuarios) < 3:
            print_error("No hay suficientes usuarios en la base de datos")
            return False
        
        creador = usuarios[0]
        participante1 = usuarios[1]
        participante2 = usuarios[2]
        
        print_info("Creador", f"{creador.nombres} {creador.apellidos} (ID: {creador.usuario_id})")
        print_info("Participante 1", f"{participante1.nombres} {participante1.apellidos}")
        print_info("Participante 2", f"{participante2.nombres} {participante2.apellidos}")
        
        # ==================== PASO 1: CREAR SALA ====================
        print_step(1, "Crear sala de chat de prueba")
        
        start = time.time()
        
        sala = SalaChat(
            id=uuid4(),
            nombre="🧪 Sala de Prueba E2E",
            descripcion="Sala para testing del sistema de chat",
            tipo_sala="GENERAL",
            creador_id=creador.usuario_id,
            es_publica=True,
            permite_archivos=True,
            permite_menciones_usuarios=True,
            permite_hilos=True,
            moderacion_activa=False,
            fecha_creacion=datetime.utcnow(),
            configuracion_json={"test_mode": True},
            tags="test,e2e"
        )
        db.add(sala)
        db.commit()
        db.refresh(sala)
        
        tiempo_crear_sala = (time.time() - start) * 1000
        tiempos['crear_sala'] = tiempo_crear_sala
        sala_id = str(sala.id)
        
        print_success("Sala creada exitosamente")
        print_info("ID", sala.id)
        print_info("Nombre", sala.nombre)
        print_info("Tipo", sala.tipo_sala)
        print_timing("Tiempo de creación", tiempo_crear_sala)
        
        # ==================== PASO 2: AGREGAR PARTICIPANTES ====================
        print_step(2, "Agregar participantes a la sala")
        
        start = time.time()
        
        # Agregar creador
        part_creador = ParticipanteSala(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=creador.usuario_id,
            rol="admin",
            puede_escribir=True,
            puede_eliminar=True,
            puede_gestionar_participantes=True,
            esta_activo=True,
            fecha_ingreso=datetime.utcnow(),
            notificaciones_activas=True
        )
        db.add(part_creador)
        
        # Agregar participante 1
        part1 = ParticipanteSala(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante1.usuario_id,
            rol="miembro",
            puede_escribir=True,
            puede_eliminar=False,
            puede_gestionar_participantes=False,
            esta_activo=True,
            fecha_ingreso=datetime.utcnow()
        )
        db.add(part1)
        
        # Agregar participante 2
        part2 = ParticipanteSala(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante2.usuario_id,
            rol="miembro",
            puede_escribir=True,
            puede_eliminar=False,
            puede_gestionar_participantes=False,
            esta_activo=True,
            fecha_ingreso=datetime.utcnow()
        )
        db.add(part2)
        
        db.commit()
        
        tiempo_agregar_participantes = (time.time() - start) * 1000
        tiempos['agregar_participantes'] = tiempo_agregar_participantes
        
        print_success("3 participantes agregados")
        print_timing("Tiempo total", tiempo_agregar_participantes)
        
        # ==================== PASO 3: MENSAJE DE TEXTO ====================
        print_step(3, "Enviar mensaje de TEXTO")
        
        start = time.time()
        
        mensaje_texto = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=creador.usuario_id,
            contenido="¡Hola! Este es un mensaje de prueba del sistema E2E 🚀",
            tipo_mensaje="TEXTO",
            fecha_creacion=datetime.utcnow(),
            estado="ENVIADO",
            es_importante=False,
            numero_respuestas=0
        )
        db.add(mensaje_texto)
        db.commit()
        db.refresh(mensaje_texto)
        
        tiempo_texto = (time.time() - start) * 1000
        tiempos['mensaje_texto'] = tiempo_texto
        
        print_success("Mensaje de texto enviado")
        print_info("ID", mensaje_texto.id)
        print_info("Contenido", mensaje_texto.contenido[:50] + "...")
        print_timing("Tiempo de envío", tiempo_texto)
        
        # ==================== PASO 4: MENSAJE CON IMAGEN ====================
        print_step(4, "Enviar mensaje con IMAGEN")
        
        start = time.time()
        
        mensaje_imagen = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante1.usuario_id,
            contenido="Miren esta captura de pantalla",
            tipo_mensaje="IMAGEN",
            metadatos_archivos={
                "url": "https://cdn.example.com/images/screenshot-123.png",
                "nombre": "screenshot.png",
                "tamano": 524288,  # 512 KB
                "tipo_mime": "image/png",
                "ancho": 1920,
                "alto": 1080
            },
            fecha_creacion=datetime.utcnow(),
            estado="ENVIADO"
        )
        db.add(mensaje_imagen)
        db.commit()
        
        tiempo_imagen = (time.time() - start) * 1000
        tiempos['mensaje_imagen'] = tiempo_imagen
        
        print_success("Mensaje con imagen enviado")
        print_info("Tipo", mensaje_imagen.tipo_mensaje)
        print_info("URL", mensaje_imagen.datos_adjuntos.get('url'))
        print_info("Tamaño", f"{mensaje_imagen.datos_adjuntos.get('tamano') / 1024:.2f} KB")
        print_timing("Tiempo de envío", tiempo_imagen)
        
        # ==================== PASO 5: MENSAJE CON ARCHIVO ====================
        print_step(5, "Enviar mensaje con ARCHIVO")
        
        start = time.time()
        
        mensaje_archivo = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante2.usuario_id,
            contenido="Les comparto el documento de la tarea",
            tipo_mensaje="ARCHIVO",
            metadatos_archivos={
                "url": "https://cdn.example.com/files/tarea-123.pdf",
                "nombre": "Proyecto_Final.pdf",
                "tamano": 2097152,  # 2 MB
                "tipo_mime": "application/pdf",
                "extension": "pdf"
            },
            fecha_creacion=datetime.utcnow(),
            estado="ENVIADO"
        )
        db.add(mensaje_archivo)
        db.commit()
        
        tiempo_archivo = (time.time() - start) * 1000
        tiempos['mensaje_archivo'] = tiempo_archivo
        
        print_success("Mensaje con archivo enviado")
        print_info("Nombre", mensaje_archivo.datos_adjuntos.get('nombre'))
        print_info("Tamaño", f"{mensaje_archivo.datos_adjuntos.get('tamano') / 1024 / 1024:.2f} MB")
        print_timing("Tiempo de envío", tiempo_archivo)
        
        # ==================== PASO 6: MENSAJE CON AUDIO ====================
        print_step(6, "Enviar mensaje con AUDIO")
        
        start = time.time()
        
        mensaje_audio = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=creador.usuario_id,
            contenido="Audio de voz",
            tipo_mensaje="AUDIO",
            metadatos_archivos={
                "url": "https://cdn.example.com/audio/voice-note-456.mp3",
                "nombre": "nota_de_voz.mp3",
                "tamano": 131072,  # 128 KB
                "tipo_mime": "audio/mpeg",
                "duracion_segundos": 15,
                "formato": "mp3"
            },
            fecha_creacion=datetime.utcnow(),
            estado="ENVIADO"
        )
        db.add(mensaje_audio)
        db.commit()
        
        tiempo_audio = (time.time() - start) * 1000
        tiempos['mensaje_audio'] = tiempo_audio
        
        print_success("Mensaje con audio enviado")
        print_info("Duración", f"{mensaje_audio.datos_adjuntos.get('duracion_segundos')}s")
        print_info("Tamaño", f"{mensaje_audio.datos_adjuntos.get('tamano') / 1024:.2f} KB")
        print_timing("Tiempo de envío", tiempo_audio)
        
        # ==================== PASO 7: MENSAJE CON VIDEO ====================
        print_step(7, "Enviar mensaje con VIDEO")
        
        start = time.time()
        
        mensaje_video = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante1.usuario_id,
            contenido="Video explicativo de la clase",
            tipo_mensaje="VIDEO",
            metadatos_archivos={
                "url": "https://cdn.example.com/videos/clase-789.mp4",
                "nombre": "explicacion_tema.mp4",
                "tamano": 10485760,  # 10 MB
                "tipo_mime": "video/mp4",
                "duracion_segundos": 120,
                "resolucion": "1280x720",
                "thumbnail_url": "https://cdn.example.com/thumbnails/video-789.jpg"
            },
            fecha_creacion=datetime.utcnow(),
            estado="ENVIADO"
        )
        db.add(mensaje_video)
        db.commit()
        
        tiempo_video = (time.time() - start) * 1000
        tiempos['mensaje_video'] = tiempo_video
        
        print_success("Mensaje con video enviado")
        print_info("Duración", f"{mensaje_video.datos_adjuntos.get('duracion_segundos')}s")
        print_info("Resolución", mensaje_video.datos_adjuntos.get('resolucion'))
        print_info("Tamaño", f"{mensaje_video.datos_adjuntos.get('tamano') / 1024 / 1024:.2f} MB")
        print_timing("Tiempo de envío", tiempo_video)
        
        # ==================== PASO 8: REACCIONES ====================
        print_step(8, "Agregar reacciones a mensajes")
        
        start = time.time()
        
        mensaje_texto.reacciones = {
            "👍": [str(participante1.usuario_id), str(participante2.usuario_id)],
            "❤️": [str(creador.usuario_id)],
            "😂": [str(participante1.usuario_id)]
        }
        db.commit()
        
        tiempo_reacciones = (time.time() - start) * 1000
        tiempos['reacciones'] = tiempo_reacciones
        
        print_success("Reacciones agregadas")
        print_info("Total reacciones", sum(len(users) for users in mensaje_texto.reacciones.values()))
        print_timing("Tiempo", tiempo_reacciones)
        
        # ==================== PASO 9: MENCIONES ====================
        print_step(9, "Enviar mensaje con MENCIONES")
        
        start = time.time()
        
        mensaje_mencion = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=creador.usuario_id,
            texto=f"@{participante1.nombres} @{participante2.nombres} revisen el documento por favor",
            tipo_mensaje="TEXTO",
            menciones_usuarios=[str(participante1.usuario_id), str(participante2.usuario_id)],
            fecha_creacion=datetime.utcnow(),
            estado="ENVIADO"
        )
        db.add(mensaje_mencion)
        db.commit()
        
        tiempo_menciones = (time.time() - start) * 1000
        tiempos['menciones'] = tiempo_menciones
        
        print_success("Mensaje con menciones enviado")
        print_info("Usuarios mencionados", len(mensaje_mencion.menciones))
        print_timing("Tiempo", tiempo_menciones)
        
        # ==================== PASO 10: HILO DE CONVERSACIÓN ====================
        print_step(10, "Crear hilo de conversación (responder mensaje)")
        
        start = time.time()
        
        respuesta = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante1.usuario_id,
            contenido="¡Perfecto! Ya lo revisé 👌",
            tipo_mensaje="TEXTO",
            mensaje_padre_id=mensaje_mencion.id,
            es_respuesta=True,
            fecha_creacion=datetime.utcnow(),
            estado="ENVIADO"
        )
        db.add(respuesta)
        
        # Actualizar contador del padre
        mensaje_mencion.total_respuestas += 1
        
        db.commit()
        
        tiempo_hilo = (time.time() - start) * 1000
        tiempos['hilo'] = tiempo_hilo
        
        print_success("Respuesta en hilo creada")
        print_info("Mensaje padre", str(mensaje_mencion.id)[:8] + "...")
        print_timing("Tiempo", tiempo_hilo)
        
        # ==================== PASO 11: ESTADÍSTICAS ====================
        print_step(11, "Obtener estadísticas de la sala")
        
        total_mensajes = db.query(MensajeChat).filter(MensajeChat.sala_id == sala.id).count()
        total_participantes = db.query(ParticipanteSala).filter(ParticipanteSala.sala_id == sala.id).count()
        
        # Actualizar sala
        sala.total_mensajes = total_mensajes
        sala.fecha_ultima_actividad = datetime.utcnow()
        db.commit()
        
        print_success("Estadísticas obtenidas")
        print_info("Total mensajes", total_mensajes)
        print_info("Total participantes", total_participantes)
        
        # ==================== RESUMEN ====================
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ TEST END-TO-END DE CHAT COMPLETADO EXITOSAMENTE{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}📊 TIPOS DE MENSAJES PROBADOS:{Colors.ENDC}")
        print_info("TEXTO", "✅")
        print_info("IMAGEN", "✅")
        print_info("ARCHIVO", "✅")
        print_info("AUDIO", "✅")
        print_info("VIDEO", "✅")
        print_info("MENCIONES", "✅")
        print_info("REACCIONES", "✅")
        print_info("HILOS", "✅")
        
        print(f"\n{Colors.BOLD}⏱️  TIEMPOS DE RESPUESTA:{Colors.ENDC}")
        tiempo_promedio = sum(tiempos.values()) / len(tiempos)
        for accion, tiempo in tiempos.items():
            print_timing(accion.replace('_', ' ').title(), tiempo)
        print(f"\n{Colors.BOLD}⏱️  Tiempo promedio: {tiempo_promedio:.2f}ms{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}🎯 RESULTADOS FINALES:{Colors.ENDC}")
        print_info("Sala creada", "✅")
        print_info("Participantes", f"{total_participantes}")
        print_info("Mensajes enviados", f"{total_mensajes}")
        print_info("Reacciones", "✅")
        print_info("Menciones", "✅")
        print_info("Hilos", "✅")
        
        # ==================== LÍMITES Y CONFIGURACIÓN ====================
        print(f"\n{Colors.BOLD}📏 LÍMITES Y CONFIGURACIÓN DEL SISTEMA:{Colors.ENDC}")
        print_info("Permite archivos", "✅" if sala.permite_archivos else "❌")
        print_info("Permite menciones", "✅" if sala.permite_menciones else "❌")
        print_info("Permite hilos", "✅" if sala.permite_hilos else "❌")
        print_info("Moderación activa", "✅" if sala.moderacion_activa else "❌")
        print_info("Sala pública", "✅" if sala.es_publica else "❌")
        
        return True
        
    except Exception as e:
        print_error(f"Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # ==================== LIMPIEZA ====================
        if sala_id:
            print(f"\n{Colors.WARNING}{Colors.BOLD}🧹 LIMPIEZA DE DATOS{Colors.ENDC}")
            cleanup_test_data(db, sala_id)
        
        db.close()
        print_info("Sesión DB", "Cerrada")


def main():
    """Punto de entrada principal"""
    try:
        success = run_chat_e2e_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Test interrumpido por el usuario{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
