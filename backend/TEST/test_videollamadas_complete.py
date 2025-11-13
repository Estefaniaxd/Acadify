"""
Tests completos para el sistema de videollamadas con enums.

Este módulo prueba:
1. Enums y sus métodos helper
2. Modelos SQLAlchemy con SQLEnum
3. CRUD operations con enums
4. Schemas Pydantic con validación enum
5. Service layer con lógica de negocio

Author: AI Assistant
Date: 2025-11-01
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Imports de enums
from src.enums.communication.videollamada_enums import (
    TipoLlamada,
    EstadoVideollamada,
    CalidadConexion,
    FormatoGrabacion,
    CalidadGrabacion,
    EstadoProcesamiento,
)

# Imports de modelos
from src.models.communication.videollamada import (
    Videollamada,
    VideollamadaParticipante,
    VideollamadaGrabacion,
)
from src.db.base_class import Base

# Imports de schemas
from src.schemas.communication.videollamada_schemas import (
    VideollamadaCreate,
    VideollamadaResponse,
    ParticipanteCreate,
    GrabacionCreate,
)

# Imports de CRUD
from src.crud.communication.videollamada import crud_videollamada

# Imports de service
from src.services.communication.videollamada_service import (
    videollamada_service,
    VideollamadaNotFoundError,
    VideollamadaStateError,
    ParticipanteError,
)


# ==================== FIXTURES ====================

@pytest.fixture(scope="function")
def db_session():
    """
    Crear sesión de BD en memoria para tests.
    Se reinicia para cada test.
    """
    # Crear engine en memoria
    engine = create_engine("sqlite:///:memory:")
    
    # Crear solo las tablas necesarias para videollamadas
    # (evitamos crear todas las tablas porque algunas usan ARRAY que SQLite no soporta)
    Videollamada.__table__.create(engine, checkfirst=True)
    VideollamadaParticipante.__table__.create(engine, checkfirst=True)
    VideollamadaGrabacion.__table__.create(engine, checkfirst=True)
    
    # Crear sesión
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        # Limpiar solo las tablas que creamos
        Videollamada.__table__.drop(engine, checkfirst=True)
        VideollamadaParticipante.__table__.drop(engine, checkfirst=True)
        VideollamadaGrabacion.__table__.drop(engine, checkfirst=True)


@pytest.fixture
def usuario_id():
    """UUID de usuario de prueba."""
    return uuid4()


@pytest.fixture
def otro_usuario_id():
    """UUID de otro usuario de prueba."""
    return uuid4()


@pytest.fixture
def sala_chat_id():
    """UUID de sala de chat de prueba."""
    return uuid4()


# ==================== TESTS DE ENUMS ====================

class TestEnums:
    """Tests para validar enums y sus métodos."""
    
    def test_tipo_llamada_values(self):
        """Verificar valores de TipoLlamada."""
        assert TipoLlamada.VIDEO.value == "video"
        assert TipoLlamada.VOZ.value == "voz"
        assert len(TipoLlamada) == 2
    
    def test_estado_videollamada_values(self):
        """Verificar valores de EstadoVideollamada."""
        assert EstadoVideollamada.PROGRAMADA.value == "programada"
        assert EstadoVideollamada.ACTIVA.value == "activa"
        assert EstadoVideollamada.FINALIZADA.value == "finalizada"
        assert EstadoVideollamada.CANCELADA.value == "cancelada"
        assert len(EstadoVideollamada) == 4
    
    def test_transiciones_estado_validas(self):
        """Verificar transiciones de estado válidas."""
        # PROGRAMADA puede ir a ACTIVA o CANCELADA
        assert EstadoVideollamada.PROGRAMADA.puede_transicionar_a(EstadoVideollamada.ACTIVA)
        assert EstadoVideollamada.PROGRAMADA.puede_transicionar_a(EstadoVideollamada.CANCELADA)
        assert not EstadoVideollamada.PROGRAMADA.puede_transicionar_a(EstadoVideollamada.FINALIZADA)
        
        # ACTIVA puede ir a FINALIZADA o CANCELADA
        assert EstadoVideollamada.ACTIVA.puede_transicionar_a(EstadoVideollamada.FINALIZADA)
        assert EstadoVideollamada.ACTIVA.puede_transicionar_a(EstadoVideollamada.CANCELADA)
        assert not EstadoVideollamada.ACTIVA.puede_transicionar_a(EstadoVideollamada.PROGRAMADA)
        
        # FINALIZADA no puede ir a ningún estado
        assert not EstadoVideollamada.FINALIZADA.puede_transicionar_a(EstadoVideollamada.ACTIVA)
        assert not EstadoVideollamada.FINALIZADA.puede_transicionar_a(EstadoVideollamada.CANCELADA)
        
        # CANCELADA no puede ir a ningún estado
        assert not EstadoVideollamada.CANCELADA.puede_transicionar_a(EstadoVideollamada.ACTIVA)
    
    def test_calidad_conexion_desde_metricas(self):
        """Verificar cálculo de calidad desde métricas."""
        # Excelente: < 50ms, < 1% pérdida
        calidad = CalidadConexion.desde_metricas(30, 0.5)
        assert calidad == CalidadConexion.EXCELENTE
        
        # Buena: 50-100ms, 1-3% pérdida
        calidad = CalidadConexion.desde_metricas(80, 2)
        assert calidad == CalidadConexion.BUENA
        
        # Regular: 100-200ms, 3-5% pérdida
        calidad = CalidadConexion.desde_metricas(150, 4)
        assert calidad == CalidadConexion.REGULAR
        
        # Mala: > 200ms o > 5% pérdida
        calidad = CalidadConexion.desde_metricas(250, 2)
        assert calidad == CalidadConexion.MALA
        
        calidad = CalidadConexion.desde_metricas(50, 6)
        assert calidad == CalidadConexion.MALA
    
    def test_formato_grabacion_mime_type(self):
        """Verificar MIME types de formatos."""
        assert FormatoGrabacion.MP4.mime_type == "video/mp4"
        assert FormatoGrabacion.WEBM.mime_type == "video/webm"
        assert FormatoGrabacion.MKV.mime_type == "video/x-matroska"
        assert FormatoGrabacion.AVI.mime_type == "video/x-msvideo"
    
    def test_calidad_grabacion_resolucion(self):
        """Verificar resoluciones de calidad de grabación."""
        assert CalidadGrabacion.SD.resolucion == (720, 480)  # DVD standard
        assert CalidadGrabacion.HD.resolucion == (1280, 720)
        assert CalidadGrabacion.FHD.resolucion == (1920, 1080)
        assert CalidadGrabacion.UHD_4K.resolucion == (3840, 2160)
    
    def test_calidad_grabacion_bitrate(self):
        """Verificar bitrates recomendados por calidad."""
        assert CalidadGrabacion.SD.bitrate_recomendado_kbps == 1000
        assert CalidadGrabacion.HD.bitrate_recomendado_kbps == 2500
        assert CalidadGrabacion.FHD.bitrate_recomendado_kbps == 5000
        assert CalidadGrabacion.UHD_4K.bitrate_recomendado_kbps == 15000  # Industry standard for 4K
    
    def test_estado_procesamiento_es_final(self):
        """Verificar estados finales."""
        assert not EstadoProcesamiento.PENDIENTE.es_final
        assert not EstadoProcesamiento.PROCESANDO.es_final
        assert EstadoProcesamiento.COMPLETADO.es_final
        assert EstadoProcesamiento.ERROR.es_final


# ==================== TESTS DE SCHEMAS ====================

class TestSchemas:
    """Tests para validar schemas Pydantic con enums."""
    
    def test_videollamada_create_con_enum(self):
        """Verificar creación con enum."""
        schema = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            sala_chat_id=uuid4()
        )
        
        assert schema.tipo_llamada == TipoLlamada.VIDEO
        assert isinstance(schema.tipo_llamada, TipoLlamada)
    
    def test_videollamada_create_con_string_se_convierte(self):
        """Verificar que string se convierte a enum."""
        schema = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada="video",  # String
            sala_chat_id=uuid4()
        )
        
        assert schema.tipo_llamada == TipoLlamada.VIDEO
        assert isinstance(schema.tipo_llamada, TipoLlamada)
    
    def test_videollamada_create_con_valor_invalido_falla(self):
        """Verificar que valor inválido falla."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            VideollamadaCreate(
                jitsi_room_name="test-room",
                tipo_llamada="audio",  # Inválido
                sala_chat_id=uuid4()
            )
    
    def test_grabacion_create_con_enums(self):
        """Verificar grabación con múltiples enums."""
        schema = GrabacionCreate(
            videollamada_id=uuid4(),
            archivo_url="https://example.com/video.mp4",
            formato=FormatoGrabacion.MP4,
            calidad=CalidadGrabacion.HD,
            duracion_segundos=1800
        )
        
        assert schema.formato == FormatoGrabacion.MP4
        assert schema.calidad == CalidadGrabacion.HD


# ==================== TESTS DE CRUD ====================

class TestCRUD:
    """Tests para CRUD operations con enums."""
    
    def test_create_videollamada_con_enum(self, db_session, usuario_id):
        """Crear videollamada con enum."""
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=usuario_id
        )
        
        assert videollamada.id is not None
        assert videollamada.tipo_llamada == TipoLlamada.VIDEO
        assert videollamada.estado == EstadoVideollamada.ACTIVA
        assert isinstance(videollamada.tipo_llamada, TipoLlamada)
        assert isinstance(videollamada.estado, EstadoVideollamada)
    
    def test_get_activas_filtra_por_estado_enum(self, db_session, usuario_id):
        """Verificar filtrado por estado enum."""
        # Crear 2 activas y 1 finalizada
        v1 = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="room-1",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=usuario_id
        )
        
        v2 = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="room-2",
            tipo_llamada=TipoLlamada.VOZ,
            iniciador_id=usuario_id
        )
        
        v3 = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="room-3",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=usuario_id
        )
        
        # Finalizar v3
        crud_videollamada.finalizar_llamada(db_session, v3.id)
        
        # Obtener activas
        activas = crud_videollamada.get_activas(db_session)
        
        assert len(activas) == 2
        assert all(v.estado == EstadoVideollamada.ACTIVA for v in activas)
        assert v1.id in [v.id for v in activas]
        assert v2.id in [v.id for v in activas]
        assert v3.id not in [v.id for v in activas]
    
    def test_finalizar_llamada_cambia_estado_enum(self, db_session, usuario_id):
        """Verificar cambio de estado a FINALIZADA."""
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=usuario_id
        )
        
        assert videollamada.estado == EstadoVideollamada.ACTIVA
        
        # Finalizar
        videollamada = crud_videollamada.finalizar_llamada(db_session, videollamada.id)
        
        assert videollamada.estado == EstadoVideollamada.FINALIZADA
        assert isinstance(videollamada.estado, EstadoVideollamada)
    
    def test_cancelar_llamada_cambia_estado_enum(self, db_session, usuario_id):
        """Verificar cambio de estado a CANCELADA."""
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=usuario_id
        )
        
        # Cancelar
        videollamada = crud_videollamada.cancelar_llamada(db_session, videollamada.id)
        
        assert videollamada.estado == EstadoVideollamada.CANCELADA
        assert isinstance(videollamada.estado, EstadoVideollamada)
    
    def test_agregar_grabacion_con_enums(self, db_session, usuario_id):
        """Agregar grabación con enums."""
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=usuario_id
        )
        
        grabacion = crud_videollamada.agregar_grabacion(
            db=db_session,
            videollamada_id=videollamada.id,
            archivo_url="https://example.com/video.mp4",
            formato=FormatoGrabacion.MP4,
            calidad=CalidadGrabacion.HD,
            duracion_segundos=1800
        )
        
        assert grabacion.formato == FormatoGrabacion.MP4
        assert grabacion.calidad == CalidadGrabacion.HD
        assert grabacion.estado_procesamiento == EstadoProcesamiento.COMPLETADO
        assert isinstance(grabacion.formato, FormatoGrabacion)


# ==================== TESTS DE SERVICE LAYER ====================

class TestServiceLayer:
    """Tests para service layer con lógica de negocio."""
    
    def test_crear_videollamada(self, db_session, usuario_id):
        """Crear videollamada via servicio."""
        schema_in = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            sala_chat_id=uuid4()
        )
        
        response = videollamada_service.crear_videollamada(
            db=db_session,
            videollamada_in=schema_in,
            iniciador_id=usuario_id
        )
        
        assert response.id is not None
        assert response.tipo_llamada == TipoLlamada.VIDEO
        assert response.estado == EstadoVideollamada.ACTIVA
    
    def test_unirse_a_videollamada(self, db_session, usuario_id, otro_usuario_id):
        """Usuario puede unirse a videollamada activa."""
        # Crear videollamada
        schema_in = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO
        )
        
        videollamada = videollamada_service.crear_videollamada(
            db=db_session,
            videollamada_in=schema_in,
            iniciador_id=usuario_id
        )
        
        # Otro usuario se une
        participante = videollamada_service.unirse_a_videollamada(
            db=db_session,
            videollamada_id=videollamada.id,
            usuario_id=otro_usuario_id
        )
        
        assert participante.usuario_id == otro_usuario_id
        assert participante.videollamada_id == videollamada.id
        assert participante.es_moderador == False
    
    def test_no_puede_unirse_a_llamada_finalizada(self, db_session, usuario_id, otro_usuario_id):
        """No se puede unir a llamada finalizada."""
        # Crear y finalizar
        schema_in = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO
        )
        
        videollamada = videollamada_service.crear_videollamada(
            db=db_session,
            videollamada_in=schema_in,
            iniciador_id=usuario_id
        )
        
        videollamada_service.finalizar_videollamada(db_session, videollamada.id)
        
        # Intentar unirse debe fallar
        with pytest.raises(VideollamadaStateError):
            videollamada_service.unirse_a_videollamada(
                db=db_session,
                videollamada_id=videollamada.id,
                usuario_id=otro_usuario_id
            )
    
    def test_no_puede_unirse_duplicado(self, db_session, usuario_id):
        """No se puede unir dos veces a la misma llamada."""
        # Crear videollamada (usuario_id ya es participante como iniciador)
        schema_in = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO
        )
        
        videollamada = videollamada_service.crear_videollamada(
            db=db_session,
            videollamada_in=schema_in,
            iniciador_id=usuario_id
        )
        
        # Intentar unirse de nuevo
        with pytest.raises(ParticipanteError):
            videollamada_service.unirse_a_videollamada(
                db=db_session,
                videollamada_id=videollamada.id,
                usuario_id=usuario_id
            )
    
    def test_finalizar_valida_transicion_estado(self, db_session, usuario_id):
        """Finalizar valida transición de estado."""
        # Crear videollamada
        schema_in = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO
        )
        
        videollamada = videollamada_service.crear_videollamada(
            db=db_session,
            videollamada_in=schema_in,
            iniciador_id=usuario_id
        )
        
        # Finalizar (ACTIVA -> FINALIZADA es válido)
        response = videollamada_service.finalizar_videollamada(db_session, videollamada.id)
        assert response.estado == EstadoVideollamada.FINALIZADA
        
        # Intentar finalizar de nuevo debe fallar (FINALIZADA -> FINALIZADA no válido)
        with pytest.raises(VideollamadaStateError):
            videollamada_service.finalizar_videollamada(db_session, videollamada.id)
    
    def test_cancelar_valida_transicion_estado(self, db_session, usuario_id):
        """Cancelar valida transición de estado."""
        # Crear videollamada
        schema_in = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO
        )
        
        videollamada = videollamada_service.crear_videollamada(
            db=db_session,
            videollamada_in=schema_in,
            iniciador_id=usuario_id
        )
        
        # Cancelar
        response = videollamada_service.cancelar_videollamada(db_session, videollamada.id)
        assert response.estado == EstadoVideollamada.CANCELADA
    
    def test_salir_de_videollamada_calcula_duracion(self, db_session, usuario_id, otro_usuario_id):
        """Salir calcula duración automáticamente."""
        # Crear videollamada
        schema_in = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO
        )
        
        videollamada = videollamada_service.crear_videollamada(
            db=db_session,
            videollamada_in=schema_in,
            iniciador_id=usuario_id
        )
        
        # Otro usuario se une
        videollamada_service.unirse_a_videollamada(
            db=db_session,
            videollamada_id=videollamada.id,
            usuario_id=otro_usuario_id
        )
        
        # Usuario sale
        participante = videollamada_service.salir_de_videollamada(
            db=db_session,
            videollamada_id=videollamada.id,
            usuario_id=otro_usuario_id
        )
        
        assert participante.fecha_salida is not None
        assert participante.duracion_segundos is not None
        assert participante.duracion_segundos >= 0
    
    def test_actualizar_calidad_conexion_con_metricas(self, db_session, usuario_id, otro_usuario_id):
        """Actualizar calidad con cálculo automático desde métricas."""
        # Crear videollamada y agregar participante
        schema_in = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO
        )
        
        videollamada = videollamada_service.crear_videollamada(
            db=db_session,
            videollamada_in=schema_in,
            iniciador_id=usuario_id
        )
        
        participante = videollamada_service.unirse_a_videollamada(
            db=db_session,
            videollamada_id=videollamada.id,
            usuario_id=otro_usuario_id
        )
        
        # Actualizar con métricas que dan EXCELENTE
        updated = videollamada_service.actualizar_calidad_conexion(
            db=db_session,
            participante_id=participante.id,
            calidad=CalidadConexion.BUENA,  # Será recalculado
            latencia_ms=30.0,
            perdida_paquetes_pct=0.5
        )
        
        # Debe calcular EXCELENTE desde métricas
        assert updated.calidad_conexion == CalidadConexion.EXCELENTE
        assert updated.datos_conexion['latencia_ms'] == 30.0
        assert updated.datos_conexion['perdida_paquetes_pct'] == 0.5
    
    def test_validar_puede_unirse_comprueba_limite_participantes(self, db_session, usuario_id):
        """Validar límite de participantes."""
        # Crear videollamada con límite de 2 participantes
        schema_in = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            configuracion={"max_participantes": 2}
        )
        
        videollamada = videollamada_service.crear_videollamada(
            db=db_session,
            videollamada_in=schema_in,
            iniciador_id=usuario_id
        )
        
        # Agregar segundo participante
        usuario2 = uuid4()
        videollamada_service.unirse_a_videollamada(
            db=db_session,
            videollamada_id=videollamada.id,
            usuario_id=usuario2
        )
        
        # Intentar agregar tercero debe fallar en validación
        usuario3 = uuid4()
        result = videollamada_service.validar_puede_unirse(
            db=db_session,
            videollamada_id=videollamada.id,
            usuario_id=usuario3
        )
        
        assert result['puede_unirse'] == False
        assert 'límite' in result['razon'].lower()
    
    def test_obtener_room_name_disponible_genera_unico(self, db_session, usuario_id):
        """Generar nombre de sala único."""
        # Crear videollamada con nombre
        schema_in = VideollamadaCreate(
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO
        )
        
        videollamada_service.crear_videollamada(
            db=db_session,
            videollamada_in=schema_in,
            iniciador_id=usuario_id
        )
        
        # Intentar obtener nombre disponible con mismo base
        nombre_nuevo = videollamada_service.obtener_room_name_disponible(
            db=db_session,
            base_name="test-room"
        )
        
        # Debe generar con sufijo
        assert nombre_nuevo != "test-room"
        assert nombre_nuevo.startswith("test-room")


# ==================== TESTS DE INTEGRACIÓN ====================

class TestIntegracion:
    """Tests de integración completa."""
    
    def test_flujo_completo_videollamada(self, db_session, usuario_id, otro_usuario_id):
        """
        Test de flujo completo:
        1. Crear videollamada
        2. Agregar participante
        3. Actualizar calidad
        4. Salir participante
        5. Agregar grabación
        6. Finalizar
        """
        # 1. Crear
        schema_in = VideollamadaCreate(
            jitsi_room_name="test-room-integration",
            tipo_llamada=TipoLlamada.VIDEO,
            configuracion={"max_participantes": 10}
        )
        
        videollamada = videollamada_service.crear_videollamada(
            db=db_session,
            videollamada_in=schema_in,
            iniciador_id=usuario_id
        )
        
        assert videollamada.estado == EstadoVideollamada.ACTIVA
        
        # 2. Agregar participante
        participante = videollamada_service.unirse_a_videollamada(
            db=db_session,
            videollamada_id=videollamada.id,
            usuario_id=otro_usuario_id
        )
        
        assert participante.usuario_id == otro_usuario_id
        
        # 3. Actualizar calidad
        participante_updated = videollamada_service.actualizar_calidad_conexion(
            db=db_session,
            participante_id=participante.id,
            calidad=CalidadConexion.BUENA,
            latencia_ms=75.0,
            perdida_paquetes_pct=1.5
        )
        
        assert participante_updated.calidad_conexion == CalidadConexion.BUENA
        
        # 4. Salir participante
        participante_salida = videollamada_service.salir_de_videollamada(
            db=db_session,
            videollamada_id=videollamada.id,
            usuario_id=otro_usuario_id
        )
        
        assert participante_salida.fecha_salida is not None
        
        # 5. Agregar grabación
        grabacion_in = GrabacionCreate(
            videollamada_id=videollamada.id,
            archivo_url="https://example.com/recording.mp4",
            formato=FormatoGrabacion.MP4,
            calidad=CalidadGrabacion.FHD,
            duracion_segundos=3600,
            tamano_bytes=1024 * 1024 * 500  # 500 MB
        )
        
        grabacion = videollamada_service.agregar_grabacion(
            db=db_session,
            videollamada_id=videollamada.id,
            grabacion_in=grabacion_in
        )
        
        assert grabacion.formato == FormatoGrabacion.MP4
        assert grabacion.estado_procesamiento == EstadoProcesamiento.COMPLETADO
        
        # 6. Finalizar
        videollamada_final = videollamada_service.finalizar_videollamada(
            db=db_session,
            videollamada_id=videollamada.id,
            resumen_ia="Reunión exitosa sobre proyecto X"
        )
        
        assert videollamada_final.estado == EstadoVideollamada.FINALIZADA
        assert videollamada_final.duracion_segundos is not None
        assert videollamada_final.resumen_ia == "Reunión exitosa sobre proyecto X"


# ==================== MAIN ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
