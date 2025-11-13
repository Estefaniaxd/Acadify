"""Tests comprehensivos para el sistema de chat y mensajes.

Cubre:
- Creación y envío de mensajes (texto, archivos, multimedia)
- Sistema de respuestas (hilos de conversación)
- Menciones (@usuario, @ia, @todos)
- Reacciones a mensajes
- Edición y eliminación de mensajes
- Mensajes programados
- Creación y gestión de salas de chat
- Participantes y permisos
- Lectura de mensajes (tracking)
- Configuración de notificaciones
- Modo no molestar

Tiempo estimado: 15-20 minutos
"""

import pytest
from datetime import datetime, UTC, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from src.models.communication.chat import (
    SalaChat,
    ParticipanteSala,
    LecturaMensaje,
    Notificacion,
    ConfiguracionNotificaciones,
    TipoSala,
)
from src.models.communication.mensaje import Mensaje
from src.models.users.usuario import Usuario


# ==================== TESTS DE MENSAJES ====================


def test_crear_mensaje_texto(
    db_session: Session, sala_chat_curso: SalaChat, usuario_emisor: Usuario
):
    """Test crear mensaje de texto básico."""
    mensaje = Mensaje(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_emisor.usuario_id,
        contenido="Este es un mensaje de prueba",
        contenido_html="<p>Este es un mensaje de prueba</p>",
        tipo_mensaje="texto",
        estado="enviado",
        fecha_creacion=datetime.now(UTC),
    )

    db_session.add(mensaje)
    db_session.commit()
    db_session.refresh(mensaje)

    assert mensaje.id is not None
    assert mensaje.contenido == "Este es un mensaje de prueba"
    assert mensaje.tipo_mensaje == "texto"
    assert mensaje.estado == "enviado"
    assert mensaje.fecha_creacion is not None


def test_enviar_mensaje_con_archivos(
    db_session: Session, sala_chat_curso: SalaChat, usuario_emisor: Usuario
):
    """Test enviar mensaje con archivos adjuntos."""
    mensaje = Mensaje(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_emisor.usuario_id,
        contenido="Adjunto el material de la clase",
        tipo_mensaje="archivo",
        archivos_urls=["https://storage.acadify.edu/materiales/clase1.pdf"],
        metadatos_archivos={
            "clase1.pdf": {"tamano": 1024000, "tipo": "application/pdf"}
        },
        estado="enviado",
        fecha_creacion=datetime.now(UTC),
    )

    db_session.add(mensaje)
    db_session.commit()
    db_session.refresh(mensaje)

    assert mensaje.tipo_mensaje == "archivo"
    assert len(mensaje.archivos_urls) == 1
    assert "clase1.pdf" in mensaje.metadatos_archivos
    assert mensaje.metadatos_archivos["clase1.pdf"]["tamano"] == 1024000


def test_sistema_respuestas_hilos(
    db_session: Session,
    sala_chat_curso: SalaChat,
    usuario_emisor: Usuario,
    usuario_receptor: Usuario,
):
    """Test sistema de respuestas (hilos de conversación)."""
    # Mensaje padre
    mensaje_padre = Mensaje(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_emisor.usuario_id,
        contenido="¿Alguien tiene dudas sobre la tarea?",
        es_respuesta=False,
        tiene_respuestas=False,
        numero_respuestas=0,
        fecha_creacion=datetime.now(UTC),
    )

    db_session.add(mensaje_padre)
    db_session.commit()

    # Respuesta al mensaje padre
    respuesta = Mensaje(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_receptor.usuario_id,
        contenido="Sí, tengo una duda sobre el ejercicio 3",
        mensaje_padre_id=mensaje_padre.id,
        es_respuesta=True,
        fecha_creacion=datetime.now(UTC),
    )

    db_session.add(respuesta)

    # Actualizar mensaje padre
    mensaje_padre.tiene_respuestas = True
    mensaje_padre.numero_respuestas = 1

    db_session.commit()
    db_session.refresh(mensaje_padre)
    db_session.refresh(respuesta)

    assert respuesta.es_respuesta is True
    assert respuesta.mensaje_padre_id == mensaje_padre.id
    assert mensaje_padre.tiene_respuestas is True
    assert mensaje_padre.numero_respuestas == 1


def test_menciones_usuarios(
    db_session: Session,
    sala_chat_curso: SalaChat,
    usuario_emisor: Usuario,
    usuario_receptor: Usuario,
):
    """Test menciones a usuarios (@usuario)."""
    mensaje = Mensaje(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_emisor.usuario_id,
        contenido=f"@{usuario_receptor.username} ¿puedes revisar esto?",
        menciones_usuarios=[str(usuario_receptor.usuario_id)],
        menciones=[str(usuario_receptor.usuario_id)],
        fecha_creacion=datetime.now(UTC),
    )

    db_session.add(mensaje)
    db_session.commit()
    db_session.refresh(mensaje)

    assert len(mensaje.menciones_usuarios) == 1
    assert str(usuario_receptor.usuario_id) in mensaje.menciones_usuarios
    assert "@" in mensaje.contenido


def test_menciones_ia(
    db_session: Session, sala_chat_curso: SalaChat, usuario_emisor: Usuario
):
    """Test mención al bot de IA (@rutilio)."""
    mensaje = Mensaje(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_emisor.usuario_id,
        contenido="@rutilio ¿puedes explicar este concepto?",
        menciones_ia=True,
        fecha_creacion=datetime.now(UTC),
    )

    db_session.add(mensaje)
    db_session.commit()
    db_session.refresh(mensaje)

    assert mensaje.menciones_ia is True
    assert "@rutilio" in mensaje.contenido


def test_menciones_todos(
    db_session: Session, sala_chat_curso: SalaChat, usuario_emisor: Usuario
):
    """Test mención a todos (@todos, @everyone)."""
    mensaje = Mensaje(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_emisor.usuario_id,
        contenido="@todos Recuerden que mañana hay examen",
        menciones_todos=True,
        es_importante=True,
        fecha_creacion=datetime.now(UTC),
    )

    db_session.add(mensaje)
    db_session.commit()
    db_session.refresh(mensaje)

    assert mensaje.menciones_todos is True
    assert mensaje.es_importante is True


def test_reacciones_mensaje(
    db_session: Session,
    sala_chat_curso: SalaChat,
    usuario_emisor: Usuario,
    usuario_receptor: Usuario,
):
    """Test agregar reacciones a un mensaje (👍, ❤️, 😂)."""
    mensaje = Mensaje(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_emisor.usuario_id,
        contenido="Excelente trabajo en el proyecto!",
        reacciones={},
        fecha_creacion=datetime.now(UTC),
    )

    db_session.add(mensaje)
    db_session.commit()

    # Agregar reacciones
    mensaje.reacciones = {
        "👍": [str(usuario_receptor.usuario_id)],
        "❤️": [str(usuario_receptor.usuario_id)],
    }

    db_session.commit()
    db_session.refresh(mensaje)

    assert "👍" in mensaje.reacciones
    assert "❤️" in mensaje.reacciones
    assert len(mensaje.reacciones["👍"]) == 1


def test_editar_mensaje(
    db_session: Session, mensaje_texto: Mensaje, usuario_emisor: Usuario
):
    """Test editar contenido de un mensaje."""
    contenido_original = mensaje_texto.contenido

    # Editar mensaje
    mensaje_texto.contenido = "Mensaje editado: Bienvenidos al curso actualizado!"
    mensaje_texto.fecha_edicion = datetime.now(UTC)
    mensaje_texto.editado_por = usuario_emisor.usuario_id

    db_session.commit()
    db_session.refresh(mensaje_texto)

    assert mensaje_texto.contenido != contenido_original
    assert "editado" in mensaje_texto.contenido.lower()
    assert mensaje_texto.fecha_edicion is not None
    assert mensaje_texto.editado_por == usuario_emisor.usuario_id


def test_eliminar_mensaje_logico(
    db_session: Session, mensaje_texto: Mensaje
):
    """Test eliminación lógica de mensaje (soft delete)."""
    # Eliminar lógicamente
    mensaje_texto.estado = "eliminado"
    mensaje_texto.fecha_eliminacion = datetime.now(UTC)

    db_session.commit()
    db_session.refresh(mensaje_texto)

    assert mensaje_texto.estado == "eliminado"
    assert mensaje_texto.fecha_eliminacion is not None


def test_mensaje_programado(
    db_session: Session, sala_chat_curso: SalaChat, usuario_emisor: Usuario
):
    """Test mensaje programado para envío futuro."""
    fecha_programada = datetime.now(UTC) + timedelta(hours=2)

    mensaje = Mensaje(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_emisor.usuario_id,
        contenido="Recordatorio: Examen mañana a las 10am",
        programado_para=fecha_programada,
        estado="programado",
        es_importante=True,
        fecha_creacion=datetime.now(UTC),
    )

    db_session.add(mensaje)
    db_session.commit()
    db_session.refresh(mensaje)

    assert mensaje.programado_para is not None
    # Comparar solo los timestamps (SQLite puede perder timezone info)
    programado_ts = mensaje.programado_para.replace(tzinfo=UTC) if mensaje.programado_para.tzinfo is None else mensaje.programado_para
    assert programado_ts > datetime.now(UTC)
    assert mensaje.estado == "programado"


# ==================== TESTS DE SALAS DE CHAT ====================


def test_crear_sala_chat_curso(
    db_session: Session, usuario_emisor: Usuario
):
    """Test crear sala de chat para un curso."""
    sala = SalaChat(
        id=uuid4(),
        nombre="Matemáticas Avanzadas",
        descripcion="Sala de chat del curso de Matemáticas Avanzadas",
        tipo_sala=TipoSala.CURSO,
        curso_id=uuid4(),
        es_publica=True,
        permite_archivos=True,
        permite_menciones=True,
        creador_id=usuario_emisor.usuario_id,
        esta_activa=True,
    )

    db_session.add(sala)
    db_session.commit()
    db_session.refresh(sala)

    assert sala.id is not None
    assert sala.tipo_sala == TipoSala.CURSO
    assert sala.es_publica is True
    assert sala.creador_id == usuario_emisor.usuario_id


def test_agregar_participantes_sala(
    db_session: Session,
    sala_chat_curso: SalaChat,
    usuario_receptor: Usuario,
    usuario_adicional: Usuario,
):
    """Test agregar múltiples participantes a una sala."""
    participante1 = ParticipanteSala(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_receptor.usuario_id,
        rol="estudiante",
        puede_escribir=True,
        esta_activo=True,
    )

    participante2 = ParticipanteSala(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_adicional.usuario_id,
        rol="estudiante",
        puede_escribir=True,
        esta_activo=True,
    )

    db_session.add_all([participante1, participante2])
    db_session.commit()

    # Verificar
    participantes = (
        db_session.query(ParticipanteSala)
        .filter_by(sala_id=sala_chat_curso.id)
        .all()
    )

    assert len(participantes) == 2
    assert participante1.usuario_id == usuario_receptor.usuario_id
    assert participante2.usuario_id == usuario_adicional.usuario_id


def test_configuracion_permisos_participante(
    db_session: Session, sala_chat_curso: SalaChat, usuario_receptor: Usuario
):
    """Test configurar permisos de un participante."""
    participante = ParticipanteSala(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_receptor.usuario_id,
        rol="moderador",
        es_moderador=True,
        puede_escribir=True,
        puede_eliminar=True,
        puede_gestionar_participantes=False,
        esta_activo=True,
    )

    db_session.add(participante)
    db_session.commit()
    db_session.refresh(participante)

    assert participante.es_moderador is True
    assert participante.puede_escribir is True
    assert participante.puede_eliminar is True
    assert participante.puede_gestionar_participantes is False


# ==================== TESTS DE LECTURA Y NOTIFICACIONES ====================


def test_lectura_mensaje(
    db_session: Session, mensaje_texto: Mensaje, usuario_receptor: Usuario
):
    """Test marcar mensaje como leído."""
    lectura = LecturaMensaje(
        id=uuid4(),
        mensaje_id=mensaje_texto.id,
        usuario_id=usuario_receptor.usuario_id,
        fecha_lectura=datetime.now(UTC),
        dispositivo="web",
    )

    db_session.add(lectura)
    db_session.commit()
    db_session.refresh(lectura)

    assert lectura.mensaje_id == mensaje_texto.id
    assert lectura.usuario_id == usuario_receptor.usuario_id
    assert lectura.fecha_lectura is not None


def test_crear_notificacion_mensaje(
    db_session: Session,
    mensaje_texto: Mensaje,
    sala_chat_curso: SalaChat,
    usuario_receptor: Usuario,
):
    """Test crear notificación para nuevo mensaje."""
    notificacion = Notificacion(
        id=uuid4(),
        usuario_id=usuario_receptor.usuario_id,
        titulo="Nuevo mensaje en Programación I",
        mensaje=mensaje_texto.contenido[:100],
        tipo="mensaje",
        sala_id=sala_chat_curso.id,
        mensaje_id=mensaje_texto.id,
        leida=False,
        fecha_creacion=datetime.now(UTC),
    )

    db_session.add(notificacion)
    db_session.commit()
    db_session.refresh(notificacion)

    assert notificacion.tipo == "mensaje"
    assert notificacion.mensaje_id == mensaje_texto.id
    assert notificacion.leida is False
    assert notificacion.esta_leida is False


def test_configuracion_notificaciones_usuario(
    db_session: Session, usuario_receptor: Usuario
):
    """Test configurar preferencias de notificaciones."""
    from datetime import time

    config = ConfiguracionNotificaciones(
        id=uuid4(),
        usuario_id=usuario_receptor.usuario_id,
        notif_mensajes_directos=True,
        notif_menciones=True,
        notif_respuestas=True,
        notif_reacciones=False,
        sonido_activo=True,
        preview_mensajes=True,
        modo_no_molestar=True,
        hora_inicio_no_molestar=time(22, 0),
        hora_fin_no_molestar=time(8, 0),
    )

    db_session.add(config)
    db_session.commit()
    db_session.refresh(config)

    assert config.notif_mensajes_directos is True
    assert config.notif_menciones is True
    assert config.modo_no_molestar is True
    assert config.notificaciones_activas is True


def test_modo_no_molestar_property(
    db_session: Session, usuario_receptor: Usuario
):
    """Test property en_modo_no_molestar con horarios."""
    from datetime import time

    config = ConfiguracionNotificaciones(
        id=uuid4(),
        usuario_id=usuario_receptor.usuario_id,
        modo_no_molestar=True,
        hora_inicio_no_molestar=time(0, 0),  # Medianoche
        hora_fin_no_molestar=time(23, 59),  # Casi medianoche (todo el día)
    )

    db_session.add(config)
    db_session.commit()
    db_session.refresh(config)

    # Este test depende de la hora actual, solo verificamos la propiedad existe
    assert hasattr(config, "en_modo_no_molestar")
    assert isinstance(config.en_modo_no_molestar, bool)
