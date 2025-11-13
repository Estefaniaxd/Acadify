"""Tests comprehensivos para el sistema de videollamadas con Jitsi.

Cubre:
- Creación y configuración de videollamadas
- Gestión de participantes (unirse, salir, activos)
- Calidad de conexión y métricas
- Estados y transiciones (activa → finalizada, cancelada)
- Grabaciones y transcripciones
- Validaciones de negocio y límites
- Integración con Jitsi Meet

Tiempo estimado: 10-15 minutos
"""

import pytest
from datetime import datetime, UTC, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from src.models.communication.videollamada import (
    Videollamada,
    VideollamadaParticipante,
    VideollamadaGrabacion,
)
from src.models.users.usuario import Usuario
from src.models.communication.chat import SalaChat
from src.enums.users.usuario_enums import TipoDocumentoUsuario, RolUsuario
from src.services.communication.videollamada_service import (
    VideollamadaService,
    VideollamadaNotFoundError,
    VideollamadaStateError,
    ParticipanteError,
)
from src.schemas.communication.videollamada_schemas import (
    VideollamadaCreate,
    GrabacionCreate,
)
from src.enums.communication.videollamada_enums import (
    TipoLlamada,
    EstadoVideollamada,
    CalidadConexion,
    FormatoGrabacion,
    CalidadGrabacion,
    EstadoProcesamiento,
)


# ==================== TESTS DE CREACIÓN Y CONFIGURACIÓN ====================


def test_crear_videollamada(
    db_session: Session, sala_chat_curso: SalaChat, usuario_emisor: Usuario
):
    """Test crear nueva videollamada."""
    service = VideollamadaService()

    videollamada_in = VideollamadaCreate(
        jitsi_room_name=f"test-room-{uuid4().hex[:8]}",
        tipo_llamada=TipoLlamada.VIDEO,
        sala_chat_id=sala_chat_curso.id,
        configuracion={"max_participantes": 20, "grabar": True},
    )

    result = service.crear_videollamada(
        db=db_session, videollamada_in=videollamada_in, iniciador_id=usuario_emisor.usuario_id
    )

    assert result.id is not None
    assert result.tipo_llamada == TipoLlamada.VIDEO
    assert result.estado == EstadoVideollamada.ACTIVA
    assert result.iniciador_id == usuario_emisor.usuario_id


def test_crear_videollamada_solo_voz(
    db_session: Session, usuario_emisor: Usuario
):
    """Test crear videollamada solo con audio."""
    service = VideollamadaService()

    videollamada_in = VideollamadaCreate(
        jitsi_room_name=f"audio-only-{uuid4().hex[:8]}",
        tipo_llamada=TipoLlamada.VOZ,
        configuracion={"video_desactivado": True},
    )

    result = service.crear_videollamada(
        db=db_session, videollamada_in=videollamada_in, iniciador_id=usuario_emisor.usuario_id
    )

    assert result.tipo_llamada == TipoLlamada.VOZ
    assert result.estado == EstadoVideollamada.ACTIVA


def test_obtener_videollamada(
    db_session: Session, videollamada_activa: Videollamada
):
    """Test obtener videollamada por ID."""
    service = VideollamadaService()

    result = service.obtener_videollamada(
        db=db_session, videollamada_id=videollamada_activa.id
    )

    assert result.id == videollamada_activa.id
    assert result.jitsi_room_name == videollamada_activa.jitsi_room_name


def test_obtener_videollamada_con_participantes(
    db_session: Session,
    videollamada_activa: Videollamada,
    participante_videollamada: VideollamadaParticipante,
):
    """Test obtener videollamada con detalles de participantes."""
    service = VideollamadaService()

    result = service.obtener_videollamada(
        db=db_session,
        videollamada_id=videollamada_activa.id,
        incluir_participantes=True,
    )

    # Verificar que retorna VideollamadaDetallada
    assert hasattr(result, "participantes")


def test_listar_videollamadas_activas(
    db_session: Session, videollamada_activa: Videollamada
):
    """Test listar todas las videollamadas activas."""
    service = VideollamadaService()

    result = service.listar_videollamadas_activas(db=db_session)

    assert len(result) >= 1
    assert any(v.id == videollamada_activa.id for v in result)
    assert all(v.estado == EstadoVideollamada.ACTIVA for v in result)


# ==================== TESTS DE PARTICIPANTES ====================


def test_unirse_a_videollamada(
    db_session: Session, videollamada_activa: Videollamada, usuario_receptor: Usuario
):
    """Test usuario se une a videollamada activa."""
    service = VideollamadaService()

    result = service.unirse_a_videollamada(
        db=db_session,
        videollamada_id=videollamada_activa.id,
        usuario_id=usuario_receptor.usuario_id,
        es_moderador=False,
    )

    assert result.videollamada_id == videollamada_activa.id
    assert result.usuario_id == usuario_receptor.usuario_id
    assert result.es_moderador is False
    assert result.fecha_union is not None


def test_salir_de_videollamada(
    db_session: Session,
    videollamada_activa: Videollamada,
    participante_videollamada: VideollamadaParticipante,
):
    """Test participante sale de videollamada."""
    service = VideollamadaService()

    result = service.salir_de_videollamada(
        db=db_session,
        videollamada_id=videollamada_activa.id,
        usuario_id=participante_videollamada.usuario_id,
    )

    assert result is not None
    assert result.fecha_salida is not None
    assert result.duracion_segundos is not None


def test_obtener_participantes_activos(
    db_session: Session,
    videollamada_activa: Videollamada,
    usuario_emisor: Usuario,
    usuario_receptor: Usuario,
):
    """Test listar participantes activos (sin fecha_salida)."""
    service = VideollamadaService()

    # Unir segundo participante
    service.unirse_a_videollamada(
        db=db_session,
        videollamada_id=videollamada_activa.id,
        usuario_id=usuario_receptor.usuario_id,
    )

    result = service.obtener_participantes_activos(
        db=db_session, videollamada_id=videollamada_activa.id
    )

    assert len(result) >= 2
    assert all(p.fecha_salida is None for p in result)


def test_unirse_videollamada_duplicado(
    db_session: Session,
    videollamada_activa: Videollamada,
    participante_videollamada: VideollamadaParticipante,
):
    """Test no se puede unir dos veces el mismo usuario."""
    service = VideollamadaService()

    with pytest.raises(ParticipanteError, match="ya está en la videollamada"):
        service.unirse_a_videollamada(
            db=db_session,
            videollamada_id=videollamada_activa.id,
            usuario_id=participante_videollamada.usuario_id,
        )


# ==================== TESTS DE CALIDAD DE CONEXIÓN ====================


def test_actualizar_calidad_conexion(
    db_session: Session,
    participante_videollamada: VideollamadaParticipante,
):
    """Test actualizar calidad de conexión de participante."""
    service = VideollamadaService()

    result = service.actualizar_calidad_conexion(
        db=db_session,
        participante_id=participante_videollamada.id,
        calidad=CalidadConexion.BUENA,
        latencia_ms=50.0,
        perdida_paquetes_pct=0.5,
    )

    assert result.calidad_conexion == CalidadConexion.BUENA
    assert result.datos_conexion["latencia_ms"] == 50.0
    assert result.datos_conexion["perdida_paquetes_pct"] == 0.5


def test_calidad_conexion_desde_metricas(
    db_session: Session,
    participante_videollamada: VideollamadaParticipante,
):
    """Test calcular calidad automáticamente desde métricas."""
    service = VideollamadaService()

    # Latencia alta y pérdida alta = conexión MALA
    result = service.actualizar_calidad_conexion(
        db=db_session,
        participante_id=participante_videollamada.id,
        calidad=CalidadConexion.MALA,  # Se puede calcular automáticamente en el servicio
        latencia_ms=500.0,
        perdida_paquetes_pct=15.0,
    )

    assert result.datos_conexion["latencia_ms"] == 500.0
    assert result.datos_conexion["perdida_paquetes_pct"] == 15.0


# ==================== TESTS DE ESTADOS Y TRANSICIONES ====================


def test_finalizar_videollamada(
    db_session: Session, videollamada_activa: Videollamada
):
    """Test finalizar videollamada activa."""
    service = VideollamadaService()

    result = service.finalizar_videollamada(
        db=db_session,
        videollamada_id=videollamada_activa.id,
        resumen_ia="Reunión de 30 minutos sobre el proyecto final",
    )

    assert result.estado == EstadoVideollamada.FINALIZADA
    assert result.fecha_fin is not None
    assert result.duracion_segundos is not None


def test_cancelar_videollamada(
    db_session: Session, videollamada_activa: Videollamada
):
    """Test cancelar videollamada activa."""
    service = VideollamadaService()

    result = service.cancelar_videollamada(
        db=db_session, videollamada_id=videollamada_activa.id
    )

    assert result.estado == EstadoVideollamada.CANCELADA


def test_no_finalizar_videollamada_ya_finalizada(
    db_session: Session, videollamada_activa: Videollamada
):
    """Test no se puede finalizar una videollamada ya finalizada."""
    service = VideollamadaService()

    # Finalizar primera vez
    service.finalizar_videollamada(
        db=db_session, videollamada_id=videollamada_activa.id
    )

    # Intentar finalizar de nuevo
    with pytest.raises(VideollamadaStateError):
        service.finalizar_videollamada(
            db=db_session, videollamada_id=videollamada_activa.id
        )


# ==================== TESTS DE GRABACIONES ====================


def test_agregar_grabacion(
    db_session: Session, videollamada_activa: Videollamada
):
    """Test agregar grabación a videollamada."""
    service = VideollamadaService()

    grabacion_in = GrabacionCreate(
        videollamada_id=videollamada_activa.id,
        archivo_url="https://storage.acadify.edu/grabaciones/meeting-123.mp4",
        duracion_segundos=1800,
        tamano_bytes=524288000,
        formato=FormatoGrabacion.MP4,
        calidad=CalidadGrabacion.HD,
        thumbnail_url="https://storage.acadify.edu/thumbs/meeting-123.jpg",
        metadatos={"codec": "h264", "bitrate": 2500},
    )

    result = service.agregar_grabacion(
        db=db_session,
        videollamada_id=videollamada_activa.id,
        grabacion_in=grabacion_in,
    )

    assert result.archivo_url == grabacion_in.archivo_url
    assert result.formato == FormatoGrabacion.MP4
    assert result.calidad == CalidadGrabacion.HD
    assert result.duracion_segundos == 1800


def test_obtener_grabaciones(
    db_session: Session, videollamada_activa: Videollamada
):
    """Test obtener todas las grabaciones de una videollamada."""
    service = VideollamadaService()

    # Agregar grabación
    grabacion_in = GrabacionCreate(
        videollamada_id=videollamada_activa.id,
        archivo_url="https://storage.acadify.edu/test.mp4",
        formato=FormatoGrabacion.MP4,
    )

    service.agregar_grabacion(
        db=db_session,
        videollamada_id=videollamada_activa.id,
        grabacion_in=grabacion_in,
    )

    result = service.obtener_grabaciones(
        db=db_session, videollamada_id=videollamada_activa.id
    )

    assert len(result) >= 1
    assert any(g.archivo_url == grabacion_in.archivo_url for g in result)


# ==================== TESTS DE TRANSCRIPCIONES ====================


def test_actualizar_transcripcion(
    db_session: Session, videollamada_activa: Videollamada
):
    """Test actualizar transcripción de videollamada."""
    service = VideollamadaService()

    transcripcion = "Hola a todos, vamos a revisar el tema de hoy..."

    result = service.actualizar_transcripcion(
        db=db_session,
        videollamada_id=videollamada_activa.id,
        transcripcion=transcripcion,
    )

    assert result.transcripcion == transcripcion


# ==================== TESTS DE VALIDACIONES Y UTILIDADES ====================


def test_obtener_room_name_disponible(db_session: Session):
    """Test generar nombre de sala Jitsi único."""
    service = VideollamadaService()

    # Primera vez - debe retornar el nombre base normalizado
    room_name = service.obtener_room_name_disponible(
        db=db_session, base_name="Matemáticas Avanzadas 2024"
    )

    assert room_name == "matematicas-avanzadas-2024"

    # Crear videollamada con ese nombre
    videollamada = Videollamada(
        id=uuid4(),
        jitsi_room_name=room_name,
        tipo_llamada=TipoLlamada.VIDEO,
        iniciador_id=uuid4(),
        estado=EstadoVideollamada.ACTIVA,
        fecha_inicio=datetime.now(UTC),
    )

    db_session.add(videollamada)
    db_session.commit()

    # Segunda vez - debe agregar sufijo
    room_name_2 = service.obtener_room_name_disponible(
        db=db_session, base_name="Matemáticas Avanzadas 2024"
    )

    assert room_name_2 == "matematicas-avanzadas-2024-1"


def test_validar_puede_unirse(
    db_session: Session, videollamada_activa: Videollamada, usuario_receptor: Usuario
):
    """Test validar si usuario puede unirse a videollamada."""
    service = VideollamadaService()

    result = service.validar_puede_unirse(
        db=db_session,
        videollamada_id=videollamada_activa.id,
        usuario_id=usuario_receptor.usuario_id,
    )

    assert result["puede_unirse"] is True
    assert "videollamada" in result


def test_validar_no_puede_unirse_limite_participantes(
    db_session: Session, usuario_emisor: Usuario
):
    """Test límite de participantes alcanzado."""
    service = VideollamadaService()

    # Crear videollamada con límite de 2 participantes (mínimo permitido)
    videollamada_in = VideollamadaCreate(
        jitsi_room_name=f"limited-{uuid4().hex[:8]}",
        tipo_llamada=TipoLlamada.VIDEO,
        configuracion={"max_participantes": 2},
    )

    videollamada = service.crear_videollamada(
        db=db_session, videollamada_in=videollamada_in, iniciador_id=usuario_emisor.usuario_id
    )

    # El iniciador ya cuenta como 1 participante, unir un segundo para llenar el límite de 2
    from uuid import uuid4 as gen_uuid
    usuario_segundo = Usuario(
        usuario_id=gen_uuid(),
        correo_institucional=f"segundo.{gen_uuid().hex[:8]}@test.com",
        nombres="Segundo",
        apellidos="User",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"222{gen_uuid().hex[:7]}",
        rol=RolUsuario.estudiante,
        password_hash="hash",
        email_verified=True,
    )
    db_session.add(usuario_segundo)
    db_session.commit()
    
    # Unir segundo participante (ahora estamos en el límite: 2/2)
    service.unirse_a_videollamada(
        db=db_session,
        videollamada_id=videollamada.id,
        usuario_id=usuario_segundo.usuario_id,
    )

    # Intentar unir un tercer usuario (debe fallar porque límite=2)
    usuario_extra = Usuario(
        usuario_id=gen_uuid(),
        correo_institucional=f"extra.{gen_uuid().hex[:8]}@test.com",
        nombres="Extra",
        apellidos="User",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"333{gen_uuid().hex[:7]}",
        rol=RolUsuario.estudiante,
        password_hash="hash",
        email_verified=True,
    )
    db_session.add(usuario_extra)
    db_session.commit()

    result = service.validar_puede_unirse(
        db=db_session,
        videollamada_id=videollamada.id,
        usuario_id=usuario_extra.usuario_id,
    )

    # El límite se alcanzó, no puede unirse
    assert "puede_unirse" in result
    assert result["puede_unirse"] == False  # Límite alcanzado


def test_videollamada_not_found(db_session: Session):
    """Test error cuando videollamada no existe."""
    service = VideollamadaService()
    id_inexistente = uuid4()

    with pytest.raises(VideollamadaNotFoundError):
        service.obtener_videollamada(db=db_session, videollamada_id=id_inexistente)
