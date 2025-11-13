"""
Tests completos de la API de videollamadas usando TestClient.
Incluye tests de integración para todos los endpoints refactorizados.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

# Import models
from src.models.communication.videollamada import Videollamada, VideollamadaParticipante, VideollamadaGrabacion
from src.models.auth.usuario import Usuario

# Import enums
from src.enums.communication.videollamada_enums import (
    TipoLlamada,
    EstadoVideollamada,
    CalidadConexion,
    FormatoGrabacion,
    CalidadGrabacion,
    EstadoProcesamiento
)

# Import app and dependencies
from src.main import app
from src.api.dependencies import get_db, get_current_user


# ============================
# Fixtures
# ============================

@pytest.fixture
def mock_db_session():
    """Mock de sesión de base de datos."""
    mock_session = MagicMock()
    mock_session.query = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    mock_session.refresh = MagicMock()
    mock_session.rollback = MagicMock()
    return mock_session


@pytest.fixture
def mock_user():
    """Usuario mock para usar en los tests."""
    user = Usuario(
        id=uuid.uuid4(),
        email="test@example.com",
        nombre="Test",
        apellido="User",
        rol="estudiante"
    )
    # Asegurarse de que tiene todos los atributos necesarios
    user.hashed_password = "hashed"
    user.is_active = True
    return user


@pytest.fixture
def client(mock_db_session, mock_user):
    """
    Cliente de test con dependency overrides.
    Override get_db y get_current_user para usar mocks.
    """
    def override_get_db():
        try:
            yield mock_db_session
        finally:
            pass
    
    def override_get_current_user():
        return mock_user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def sala_chat_id():
    """UUID de sala de chat para usar en tests."""
    return uuid.uuid4()


@pytest.fixture
def otro_usuario_id():
    """UUID de otro usuario para tests de participantes."""
    return uuid.uuid4()

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

# FastAPI app
from src.main import app

# Database
from src.db.base_class import Base
from src.api.dependencies import get_db, get_current_user

# Models
from src.models.users.usuario import Usuario
from src.models.communication.videollamada import (
    Videollamada,
    VideollamadaParticipante,
    VideollamadaGrabacion
)

# Enums
from src.enums.communication.videollamada_enums import (
    TipoLlamada,
    EstadoVideollamada,
    CalidadConexion,
    FormatoGrabacion,
    CalidadGrabacion
)


# ==================== FIXTURES ====================

@pytest.fixture(scope="function")
def db_engine():
    """
    Engine SQLite en memoria para tests.
    """
    engine = create_engine("sqlite:///:memory:")
    
    # Crear solo las tablas necesarias
    Videollamada.__table__.create(engine, checkfirst=True)
    VideollamadaParticipante.__table__.create(engine, checkfirst=True)
    VideollamadaGrabacion.__table__.create(engine, checkfirst=True)
    
    yield engine
    
    # Cleanup
    Videollamada.__table__.drop(engine, checkfirst=True)
    VideollamadaParticipante.__table__.drop(engine, checkfirst=True)
    VideollamadaGrabacion.__table__.drop(engine, checkfirst=True)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Sesión de BD para tests.
    """
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture(scope="function")
def mock_user():
    """
    Usuario mock para autenticación.
    """
    return Usuario(
        id=uuid4(),
        email="test@example.com",
        nombre="Test",
        apellido="User",
        password_hash="hashed_password",
        rol="estudiante"
    )


@pytest.fixture(scope="function")
def client(db_session, mock_user):
    """
    TestClient de FastAPI con overrides de dependencias.
    """
    # Override de get_db
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override de get_current_user
    def override_get_current_user():
        return mock_user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def sala_chat_id():
    """UUID de sala de chat para tests."""
    return uuid4()


@pytest.fixture
def otro_usuario_id():
    """UUID de otro usuario para tests de participantes."""
    return uuid4()


# ==================== TESTS DE HEALTH CHECK ====================

class TestHealthCheck:
    """Tests del endpoint de health check."""
    
    def test_health_check(self, client):
        """Health check debe retornar 200."""
        response = client.get("/api/communication/videollamadas/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "operativo" in data["message"].lower()


# ==================== TESTS DE CREAR VIDEOLLAMADA ====================

class TestCrearVideollamada:
    """Tests del endpoint POST /videollamadas/."""
    
    def test_crear_videollamada_exitosa(self, client, sala_chat_id):
        """Crear videollamada con datos válidos."""
        payload = {
            "sala_chat_id": str(sala_chat_id),
            "tipo_llamada": "video",
            "titulo": "Reunión de prueba",
            "descripcion": "Descripción de prueba"
        }
        
        response = client.post(
            "/api/communication/videollamadas/",
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Validar estructura
        assert "id" in data
        assert data["tipo_llamada"] == "video"
        assert data["estado"] == "activa"
        assert data["titulo"] == "Reunión de prueba"
        assert "jitsi_room_name" in data
        assert "iniciador_id" in data
    
    def test_crear_videollamada_tipo_voz(self, client, sala_chat_id):
        """Crear videollamada de tipo VOZ."""
        payload = {
            "sala_chat_id": str(sala_chat_id),
            "tipo_llamada": "voz",
            "titulo": "Llamada de voz"
        }
        
        response = client.post(
            "/api/communication/videollamadas/",
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["tipo_llamada"] == "voz"
    
    def test_crear_videollamada_tipo_invalido(self, client, sala_chat_id):
        """Crear con tipo inválido debe fallar."""
        payload = {
            "sala_chat_id": str(sala_chat_id),
            "tipo_llamada": "invalido",
            "titulo": "Test"
        }
        
        response = client.post(
            "/api/communication/videollamadas/",
            json=payload
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_crear_videollamada_sin_sala_chat(self, client):
        """Crear sin sala_chat_id debe fallar."""
        payload = {
            "tipo_llamada": "video",
            "titulo": "Test"
        }
        
        response = client.post(
            "/api/communication/videollamadas/",
            json=payload
        )
        
        assert response.status_code == 422


# ==================== TESTS DE OBTENER VIDEOLLAMADA ====================

class TestObtenerVideollamada:
    """Tests del endpoint GET /videollamadas/{id}."""
    
    def test_obtener_videollamada_existente(self, client, db_session, mock_user, sala_chat_id):
        """Obtener videollamada que existe."""
        # Crear videollamada directamente en DB
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=mock_user.id
        )
        
        response = client.get(
            f"/api/communication/videollamadas/{videollamada.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(videollamada.id)
        assert data["jitsi_room_name"] == "test-room"
    
    def test_obtener_videollamada_no_existente(self, client):
        """Obtener videollamada que no existe debe retornar 404."""
        fake_id = uuid4()
        response = client.get(
            f"/api/communication/videollamadas/{fake_id}"
        )
        
        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"].lower()
    
    def test_obtener_con_participantes(self, client, db_session, mock_user):
        """Obtener videollamada con participantes."""
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=mock_user.id
        )
        
        response = client.get(
            f"/api/communication/videollamadas/{videollamada.id}",
            params={"incluir_participantes": True}
        )
        
        assert response.status_code == 200


# ==================== TESTS DE LISTAR VIDEOLLAMADAS ====================

class TestListarVideollamadas:
    """Tests del endpoint GET /videollamadas/."""
    
    def test_listar_videollamadas_vacias(self, client):
        """Listar cuando no hay videollamadas."""
        response = client.get("/api/communication/videollamadas/")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 0
        assert data["total"] == 0
    
    def test_listar_videollamadas_activas(self, client, db_session, mock_user):
        """Listar videollamadas activas."""
        from src.crud.communication.videollamada import crud_videollamada
        
        # Crear 2 videollamadas activas
        for i in range(2):
            crud_videollamada.create_videollamada(
                db=db_session,
                jitsi_room_name=f"test-room-{i}",
                tipo_llamada=TipoLlamada.VIDEO,
                iniciador_id=mock_user.id
            )
        
        response = client.get(
            "/api/communication/videollamadas/",
            params={"solo_activas": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2
    
    def test_listar_con_paginacion(self, client, db_session, mock_user):
        """Listar con paginación."""
        from src.crud.communication.videollamada import crud_videollamada
        
        # Crear 3 videollamadas
        for i in range(3):
            crud_videollamada.create_videollamada(
                db=db_session,
                jitsi_room_name=f"test-room-{i}",
                tipo_llamada=TipoLlamada.VIDEO,
                iniciador_id=mock_user.id
            )
        
        response = client.get(
            "/api/communication/videollamadas/",
            params={"skip": 1, "limit": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 1
        assert data["limit"] == 2


# ==================== TESTS DE UNIRSE ====================

class TestUnirseVideollamada:
    """Tests del endpoint POST /videollamadas/{id}/join."""
    
    def test_unirse_a_videollamada_activa(self, client, db_session, mock_user):
        """Unirse a videollamada activa exitosamente."""
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=uuid4()  # Otro usuario es el iniciador
        )
        
        response = client.post(
            f"/api/communication/videollamadas/{videollamada.id}/join",
            json={"es_moderador": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["usuario_id"] == str(mock_user.id)
        assert data["es_moderador"] is False
    
    def test_unirse_a_videollamada_no_existente(self, client):
        """Unirse a videollamada que no existe."""
        fake_id = uuid4()
        response = client.post(
            f"/api/communication/videollamadas/{fake_id}/join",
            json={"es_moderador": False}
        )
        
        assert response.status_code == 404
    
    def test_unirse_como_moderador(self, client, db_session, mock_user):
        """Unirse como moderador."""
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=uuid4()
        )
        
        response = client.post(
            f"/api/communication/videollamadas/{videollamada.id}/join",
            json={"es_moderador": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["es_moderador"] is True


# ==================== TESTS DE SALIR ====================

class TestSalirVideollamada:
    """Tests del endpoint POST /videollamadas/{id}/leave."""
    
    def test_salir_de_videollamada(self, client, db_session, mock_user):
        """Salir de videollamada donde se está participando."""
        from src.crud.communication.videollamada import crud_videollamada
        
        # Crear y unirse
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=uuid4()
        )
        
        crud_videollamada.agregar_participante(
            db=db_session,
            videollamada_id=videollamada.id,
            usuario_id=mock_user.id,
            es_moderador=False
        )
        
        # Salir
        response = client.post(
            f"/api/communication/videollamadas/{videollamada.id}/leave"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "salido" in data["message"].lower()


# ==================== TESTS DE PARTICIPANTES ====================

class TestParticipantes:
    """Tests de endpoints de participantes."""
    
    def test_obtener_participantes_activos(self, client, db_session, mock_user):
        """Obtener lista de participantes activos."""
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=mock_user.id
        )
        
        response = client.get(
            f"/api/communication/videollamadas/{videollamada.id}/participants"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_actualizar_calidad_con_metricas(self, client, db_session, mock_user):
        """Actualizar calidad usando métricas de red."""
        from src.crud.communication.videollamada import crud_videollamada
        
        # Crear videollamada y participante
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=uuid4()
        )
        
        participante = crud_videollamada.agregar_participante(
            db=db_session,
            videollamada_id=videollamada.id,
            usuario_id=mock_user.id,
            es_moderador=False
        )
        
        # Actualizar calidad con métricas
        response = client.patch(
            f"/api/communication/videollamadas/participants/{participante.id}/quality",
            json={
                "latencia_ms": 30,
                "perdida_paquetes_pct": 0.5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        # Debe calcularse como EXCELENTE (< 50ms, < 1%)
        assert data["calidad_conexion"] in ["excelente", "EXCELENTE"]


# ==================== TESTS DE FINALIZAR/CANCELAR ====================

class TestControlVideollamada:
    """Tests de endpoints de control."""
    
    def test_finalizar_videollamada(self, client, db_session, mock_user):
        """Finalizar videollamada como moderador."""
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=mock_user.id  # Usuario actual es iniciador
        )
        
        response = client.post(
            f"/api/communication/videollamadas/{videollamada.id}/finalize",
            json={"resumen_ia": "Resumen de la reunión"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "finalizada"
    
    def test_cancelar_videollamada(self, client, db_session, mock_user):
        """Cancelar videollamada como moderador."""
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=mock_user.id
        )
        
        response = client.post(
            f"/api/communication/videollamadas/{videollamada.id}/cancel"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "cancelada"
    
    def test_finalizar_sin_permisos(self, client, db_session, mock_user):
        """Intentar finalizar sin ser moderador debe fallar."""
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=uuid4()  # Otro usuario es iniciador
        )
        
        response = client.post(
            f"/api/communication/videollamadas/{videollamada.id}/finalize"
        )
        
        assert response.status_code == 403


# ==================== TESTS DE GRABACIONES ====================

class TestGrabaciones:
    """Tests de endpoints de grabaciones."""
    
    def test_agregar_grabacion(self, client, db_session, mock_user):
        """Agregar grabación como moderador."""
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=mock_user.id
        )
        
        payload = {
            "archivo_url": "https://cdn.example.com/rec_123.mp4",
            "formato": "mp4",
            "calidad": "FHD",
            "duracion_segundos": 3600,
            "tamano_bytes": 524288000
        }
        
        response = client.post(
            f"/api/communication/videollamadas/{videollamada.id}/recordings",
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["archivo_url"] == payload["archivo_url"]
        assert data["formato"] == "mp4"
        assert data["calidad"] == "FHD"
    
    def test_listar_grabaciones(self, client, db_session, mock_user):
        """Listar grabaciones de una videollamada."""
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=mock_user.id
        )
        
        # Agregar grabación
        crud_videollamada.agregar_grabacion(
            db=db_session,
            videollamada_id=videollamada.id,
            archivo_url="https://example.com/rec.mp4",
            formato=FormatoGrabacion.MP4,
            calidad=CalidadGrabacion.HD,
            duracion_segundos=1800
        )
        
        response = client.get(
            f"/api/communication/videollamadas/{videollamada.id}/recordings"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1


# ==================== TESTS DE TRANSCRIPCIÓN ====================

class TestTranscripcion:
    """Tests de endpoint de transcripción."""
    
    def test_actualizar_transcripcion(self, client, db_session, mock_user):
        """Actualizar transcripción como moderador."""
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=mock_user.id
        )
        
        transcripcion_texto = "John: Hola a todos..."
        
        response = client.patch(
            f"/api/communication/videollamadas/{videollamada.id}/transcription",
            json={"transcripcion": transcripcion_texto}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["transcripcion"] == transcripcion_texto


# ==================== TESTS DE UTILIDADES ====================

class TestUtilidades:
    """Tests de endpoints de utilidades."""
    
    def test_generar_room_name(self, client):
        """Generar room name único."""
        response = client.get(
            "/api/communication/videollamadas/room-name/generate",
            params={"base_name": "sala-matematicas"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "room_name" in data
        assert "sala-matematicas" in data["room_name"]
    
    def test_validar_puede_unirse(self, client, db_session, mock_user):
        """Validar si puede unirse a videollamada."""
        from src.crud.communication.videollamada import crud_videollamada
        
        videollamada = crud_videollamada.create_videollamada(
            db=db_session,
            jitsi_room_name="test-room",
            tipo_llamada=TipoLlamada.VIDEO,
            iniciador_id=uuid4()
        )
        
        response = client.post(
            f"/api/communication/videollamadas/{videollamada.id}/validate-join"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "can_join" in data
        assert isinstance(data["can_join"], bool)


# ==================== TESTS DE ERRORES ====================

class TestErrorHandling:
    """Tests de manejo de errores."""
    
    def test_uuid_invalido(self, client):
        """UUID inválido debe retornar 422."""
        response = client.get(
            "/api/communication/videollamadas/invalid-uuid"
        )
        
        assert response.status_code == 422
    
    def test_payload_invalido(self, client):
        """Payload inválido debe retornar 422."""
        response = client.post(
            "/api/communication/videollamadas/",
            json={"invalid": "data"}
        )
        
        assert response.status_code == 422
    
    def test_enum_invalido_en_body(self, client, sala_chat_id):
        """Enum inválido en body debe retornar 422."""
        payload = {
            "sala_chat_id": str(sala_chat_id),
            "tipo_llamada": "tipo_invalido",
            "titulo": "Test"
        }
        
        response = client.post(
            "/api/communication/videollamadas/",
            json=payload
        )
        
        assert response.status_code == 422


# ==================== RESUMEN ====================

if __name__ == "__main__":
    print("Tests de API de Videollamadas")
    print("=" * 50)
    print("Cobertura:")
    print("- ✅ Health check")
    print("- ✅ Crear videollamada")
    print("- ✅ Obtener videollamada")
    print("- ✅ Listar videollamadas")
    print("- ✅ Unirse/Salir")
    print("- ✅ Participantes")
    print("- ✅ Finalizar/Cancelar")
    print("- ✅ Grabaciones")
    print("- ✅ Transcripción")
    print("- ✅ Utilidades")
    print("- ✅ Manejo de errores")
    print("=" * 50)
    print("Ejecutar con: pytest TEST/test_videollamadas_api.py -v")
