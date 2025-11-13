"""
Test Simplificado para Sistema de Chat - End to End
Prueba SOLO las funcionalidades básicas del sistema de chat con los campos correctos de la BD
"""

import sys
import time
from datetime import datetime
from uuid import uuid4

# Setup path
sys.path.append(".")

from src.db.session import SessionLocal
from src.models.users.usuario import Usuario
from src.models.communication.chat import (
    SalaChat, ParticipanteSala, MensajeChat, TipoMensaje, EstadoMensaje
)


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_step(num, desc):
    print(f"\n{Colors.BOLD}[PASO {num}]{Colors.ENDC} {desc}")


def print_success(msg):
    print(f"   {Colors.OKGREEN}✅ {msg}{Colors.ENDC}")


def print_error(msg):
    print(f"   {Colors.FAIL}❌ {msg}{Colors.ENDC}")


def print_info(label, value):
    print(f"   {Colors.OKCYAN}• {label}:{Colors.ENDC} {value}")


def print_timing(label, ms):
    if ms < 100:
        color = Colors.OKGREEN
    elif ms < 500:
        color = Colors.WARNING
    else:
        color = Colors.FAIL
    print(f"   {color}⏱️  {label}: {ms:.2f}ms{Colors.ENDC}")


def get_test_users(db, count=3):
    """Obtiene usuarios de prueba de la base de datos"""
    usuarios = db.query(Usuario).limit(count).all()
    if len(usuarios) < count:
        raise Exception(f"Se necesitan al menos {count} usuarios en la base de datos")
    return usuarios


def run_simple_test():
    """Ejecuta test simplificado del sistema de chat"""
    print(f"\n{Colors.HEADER}{'='*70}")
    print(f"💬 TEST SIMPLIFICADO: SISTEMA DE CHAT")
    print(f"{'='*70}{Colors.ENDC}\n")
    
    db = SessionLocal()
    tiempos = {}
    sala_id = None
    mensaje_ids = []
    
    try:
        # ==================== PASO 0: Obtener usuarios ====================
        print_step(0, "Preparación: Obtener usuarios de prueba")
        usuarios = get_test_users(db, 3)
        creador, participante1, participante2 = usuarios
        
        print_success(f"Usando 3 usuarios existentes de la base de datos")
        print_info("Creador", f"{creador.nombres} {creador.apellidos} (ID: {creador.usuario_id})")
        print_info("Participante 1", f"{participante1.nombres} {participante1.apellidos}")
        print_info("Participante 2", f"{participante2.nombres} {participante2.apellidos}")
        
        # ==================== PASO 1: Crear sala ====================
        print_step(1, "Crear sala de chat de prueba")
        
        start = time.time()
        
        sala = SalaChat(
            id=uuid4(),
            nombre="🧪 Sala Test Simple",
            descripcion="Sala para testing simplificado",
            tipo_sala="GENERAL",
            creador_id=creador.usuario_id,
            es_publica=True,
            permite_archivos=True,
            permite_menciones=True,
            permite_hilos=True,
            fecha_creacion=datetime.now(),
            configuracion_json={"test": True},
            tags="test"
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
        print_timing("Tiempo de creación", tiempo_crear_sala)
        
        # ==================== PASO 2: Agregar participantes ====================
        print_step(2, "Agregar participantes a la sala")
        
        start = time.time()
        
        # Creador como admin
        part_creador = ParticipanteSala(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=creador.usuario_id,
            rol="ADMIN",
            puede_escribir=True,
            puede_eliminar=True,
            puede_gestionar_participantes=True,
            fecha_ingreso=datetime.now(),
            esta_activo=True,
            notificaciones_activas=True
        )
        db.add(part_creador)
        
        # Participante 1
        part1 = ParticipanteSala(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante1.usuario_id,
            rol="MIEMBRO",
            puede_escribir=True,
            fecha_ingreso=datetime.now(),
            esta_activo=True
        )
        db.add(part1)
        
        # Participante 2
        part2 = ParticipanteSala(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante2.usuario_id,
            rol="MIEMBRO",
            puede_escribir=True,
            fecha_ingreso=datetime.now(),
            esta_activo=True
        )
        db.add(part2)
        
        db.commit()
        
        tiempo_participantes = (time.time() - start) * 1000
        tiempos['agregar_participantes'] = tiempo_participantes
        
        print_success("3 participantes agregados")
        print_timing("Tiempo total", tiempo_participantes)
        
        # ==================== PASO 3: Mensaje TEXTO ====================
        print_step(3, "Enviar mensaje de TEXTO")
        
        start = time.time()
        
        mensaje_texto = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=creador.usuario_id,
            contenido="¡Hola! Este es un mensaje de prueba 🚀",
            tipo_mensaje="TEXTO",
            fecha_creacion=datetime.now(),
            estado="ENVIADO",
            es_importante=False
        )
        db.add(mensaje_texto)
        db.commit()
        db.refresh(mensaje_texto)
        mensaje_ids.append(mensaje_texto.id)
        
        tiempo_texto = (time.time() - start) * 1000
        tiempos['mensaje_texto'] = tiempo_texto
        
        print_success("Mensaje de texto enviado")
        print_info("ID", mensaje_texto.id)
        print_info("Contenido", mensaje_texto.contenido[:40])
        print_timing("Tiempo de envío", tiempo_texto)
        
        # ==================== PASO 4: Mensaje IMAGEN ====================
        print_step(4, "Enviar mensaje con IMAGEN")
        
        start = time.time()
        
        mensaje_imagen = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante1.usuario_id,
            contenido="Miren esta imagen:",
            tipo_mensaje="IMAGEN",
            archivos_urls=["https://storage.acadify.com/imagenes/test.png"],
            metadatos_archivos={
                "url": "https://storage.acadify.com/imagenes/test.png",
                "tamano": 524288,
                "tipo_mime": "image/png",
                "ancho": 1920,
                "alto": 1080
            },
            fecha_creacion=datetime.now(),
            estado="ENVIADO"
        )
        db.add(mensaje_imagen)
        db.commit()
        db.refresh(mensaje_imagen)
        mensaje_ids.append(mensaje_imagen.id)
        
        tiempo_imagen = (time.time() - start) * 1000
        tiempos['mensaje_imagen'] = tiempo_imagen
        
        print_success("Mensaje con imagen enviado")
        print_info("ID", mensaje_imagen.id)
        print_info("Tamaño", f"{mensaje_imagen.metadatos_archivos['tamano'] / 1024:.1f} KB")
        print_timing("Tiempo de envío", tiempo_imagen)
        
        # ==================== PASO 5: Mensaje ARCHIVO ====================
        print_step(5, "Enviar mensaje con ARCHIVO (PDF)")
        
        start = time.time()
        
        mensaje_archivo = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante2.usuario_id,
            contenido="Documento adjunto:",
            tipo_mensaje="ARCHIVO",
            archivos_urls=["https://storage.acadify.com/documentos/test.pdf"],
            metadatos_archivos={
                "url": "https://storage.acadify.com/documentos/test.pdf",
                "nombre": "documento_prueba.pdf",
                "tamano": 1048576,
                "tipo_mime": "application/pdf",
                "paginas": 5
            },
            fecha_creacion=datetime.now(),
            estado="ENVIADO"
        )
        db.add(mensaje_archivo)
        db.commit()
        db.refresh(mensaje_archivo)
        mensaje_ids.append(mensaje_archivo.id)
        
        tiempo_archivo = (time.time() - start) * 1000
        tiempos['mensaje_archivo'] = tiempo_archivo
        
        print_success("Mensaje con archivo enviado")
        print_info("Archivo", mensaje_archivo.metadatos_archivos['nombre'])
        print_info("Tamaño", f"{mensaje_archivo.metadatos_archivos['tamano'] / (1024*1024):.1f} MB")
        print_timing("Tiempo de envío", tiempo_archivo)
        
        # ==================== PASO 6: Agregar reacciones ====================
        print_step(6, "Agregar reacciones a los mensajes")
        
        start = time.time()
        
        # Agregar reacciones al mensaje de texto
        mensaje_texto.reacciones = {
            "👍": [str(participante1.usuario_id), str(participante2.usuario_id)],
            "❤️": [str(creador.usuario_id)]
        }
        db.commit()
        
        tiempo_reacciones = (time.time() - start) * 1000
        tiempos['agregar_reacciones'] = tiempo_reacciones
        
        print_success("Reacciones agregadas")
        print_info("Emoji 👍", "2 usuarios")
        print_info("Emoji ❤️", "1 usuario")
        print_timing("Tiempo total", tiempo_reacciones)
        
        # ==================== PASO 7: Mensaje con mención ====================
        print_step(7, "Enviar mensaje con mención")
        
        start = time.time()
        
        mensaje_mencion = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante1.usuario_id,
            contenido=f"@{participante2.nombres} ¿Ya viste el documento?",
            tipo_mensaje="TEXTO",
            menciones_usuarios=[str(participante2.usuario_id)],
            fecha_creacion=datetime.now(),
            estado="ENVIADO"
        )
        db.add(mensaje_mencion)
        db.commit()
        db.refresh(mensaje_mencion)
        mensaje_ids.append(mensaje_mencion.id)
        
        tiempo_mencion = (time.time() - start) * 1000
        tiempos['mensaje_mencion'] = tiempo_mencion
        
        print_success("Mensaje con mención enviado")
        print_info("Menciones", f"1 usuario mencionado")
        print_timing("Tiempo de envío", tiempo_mencion)
        
        # ==================== PASO 8: Crear hilo (respuesta) ====================
        print_step(8, "Crear hilo de conversación")
        
        start = time.time()
        
        respuesta = MensajeChat(
            id=uuid4(),
            sala_id=sala.id,
            usuario_id=participante2.usuario_id,
            contenido="Sí, acabo de revisarlo. Gracias por enviarlo 👌",
            tipo_mensaje="TEXTO",
            mensaje_padre_id=mensaje_archivo.id,
            fecha_creacion=datetime.now(),
            estado="ENVIADO"
        )
        db.add(respuesta)
        
        # Actualizar el mensaje padre
        mensaje_archivo.tiene_respuestas = True
        mensaje_archivo.numero_respuestas = 1
        
        db.commit()
        mensaje_ids.append(respuesta.id)
        
        tiempo_hilo = (time.time() - start) * 1000
        tiempos['crear_hilo'] = tiempo_hilo
        
        print_success("Hilo creado exitosamente")
        print_info("Mensaje padre", str(mensaje_archivo.id)[:8])
        print_info("Respuesta", str(respuesta.id)[:8])
        print_timing("Tiempo total", tiempo_hilo)
        
        # ==================== RESUMEN FINAL ====================
        print(f"\n{Colors.BOLD}{'='*70}")
        print(f"📊 RESUMEN DE RENDIMIENTO")
        print(f"{'='*70}{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}⏱️  TIEMPOS DE RESPUESTA:{Colors.ENDC}")
        for operacion, tiempo_ms in tiempos.items():
            print_timing(operacion.replace('_', ' ').title(), tiempo_ms)
        
        promedio = sum(tiempos.values()) / len(tiempos)
        print(f"\n{Colors.BOLD}   Promedio general: {promedio:.2f}ms{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}📏 ESTADÍSTICAS:{Colors.ENDC}")
        print_info("Total de mensajes", len(mensaje_ids))
        print_info("Sala creada", sala_id[:13] + "...")
        print_info("Participantes", "3 usuarios")
        print_info("Reacciones", "3 total")
        print_info("Menciones", "1 usuario")
        print_info("Hilos", "1 respuesta")
        
        print(f"\n{Colors.BOLD}✅ Configuración de sala:{Colors.ENDC}")
        print_info("Permite archivos", "✅" if sala.permite_archivos else "❌")
        print_info("Permite menciones", "✅" if sala.permite_menciones else "❌")
        print_info("Permite hilos", "✅" if sala.permite_hilos else "❌")
        print_info("Sala pública", "✅" if sala.es_publica else "❌")
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ TEST COMPLETADO EXITOSAMENTE{Colors.ENDC}\n")
        
        return True
        
    except Exception as e:
        print_error(f"Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Limpieza
        if sala_id:
            try:
                print(f"\n{Colors.WARNING}🧹 LIMPIEZA DE DATOS{Colors.ENDC}")
                # Eliminar mensajes
                db.query(MensajeChat).filter(MensajeChat.id.in_(mensaje_ids)).delete(synchronize_session=False)
                # Eliminar participantes
                db.query(ParticipanteSala).filter(ParticipanteSala.sala_id == sala.id).delete(synchronize_session=False)
                # Eliminar sala
                db.query(SalaChat).filter(SalaChat.id == sala.id).delete(synchronize_session=False)
                db.commit()
                print_success("Datos de prueba eliminados")
            except Exception as e:
                print_error(f"Error al limpiar datos: {e}")
                db.rollback()
        
        print_info("Sesión DB", "Cerrada")
        db.close()


if __name__ == "__main__":
    success = run_simple_test()
    sys.exit(0 if success else 1)
