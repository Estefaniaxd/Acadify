"""
Tests de API de videollamadas con mocking completo.
Evita crear tablas reales (problema con JSONB en SQLite).
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from fastapi.testclient import TestClient

# Import models
from src.models.communication.videollamada import Videollamada, VideollamadaParticipante, VideollamadaGrabacion
from src.models.users.usuario import Usuario

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

# Import service exceptions
from src.services.communication.videollamada_service import (
    VideollamadaNotFoundError,
    VideollamadaStateError,
    ParticipanteError
)


# ============================
# Fixtures
# ============================

@pytest.fixture
def mock_db_session():
    """Mock de sesión de base de datos."""
    mock_session = MagicMock()
    return mock_session


@pytest.fixture
def mock_user():
    """Usuario mock para usar en los tests."""
    user_id = uuid.uuid4()
    user = Mock(spec=Usuario)
    user.id = user_id
    user.email = "test@example.com"
    user.nombre = "Test"
    user.apellido = "User"
    user.rol = "estudiante"
    return user


@pytest.fixture
def client(mock_db_session, mock_user):
    """
    Cliente de test con dependency overrides.
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
    """UUID de sala de chat."""
    return uuid.uuid4()


@pytest.fixture
def videollamada_id():
    """UUID de videollamada."""
    return uuid.uuid4()


# ============================
# Helper para crear mocks de videollamada
# ============================

def create_mock_videollamada(
    videollamada_id=None,
    sala_chat_id=None,
    tipo_llamada=TipoLlamada.VIDEO,
    estado=EstadoVideollamada.ACTIVA,
    titulo="Test Call",
    usuario_id_iniciador=None
):
    """Helper para crear un mock de Videollamada con todos los atributos necesarios."""
    now = datetime.now()
    vid_id = videollamada_id or uuid.uuid4()
    init_id = usuario_id_iniciador or uuid.uuid4()
    
    mock = Mock(spec=Videollamada)
    # IDs
    mock.id = vid_id
    mock.sala_chat_id = sala_chat_id or uuid.uuid4()
    mock.iniciador_id = init_id
    
    # Básicos
    mock.jitsi_room_name = f"room-{vid_id}"
    mock.tipo_llamada = tipo_llamada
    mock.estado = estado
    mock.titulo = titulo
    mock.descripcion = None
    mock.configuracion = {}
    mock.max_participantes = 50
    
    # Fechas y tiempos
    mock.fecha_inicio = now
    mock.fecha_fin = None
    mock.duracion_segundos = None
    mock.created_at = now
    mock.updated_at = now
    
    # URLs y contenido opcional
    mock.grabacion_url = None
    mock.transcripcion = None
    mock.resumen_ia = None
    
    # Contadores opcionales
    mock.total_participantes = None
    mock.participantes_activos = None
    
    # Relaciones
    mock.participantes = []
    mock.grabaciones = []
    
    return mock


def create_mock_participante(
    participante_id=None,
    videollamada_id=None,
    usuario_id=None,
    es_moderador=False,
    calidad_conexion=CalidadConexion.BUENA
):
    """Helper para crear un mock de VideollamadaParticipante."""
    now = datetime.now()
    
    mock = Mock(spec=VideollamadaParticipante)
    mock.id = participante_id or uuid.uuid4()
    mock.videollamada_id = videollamada_id or uuid.uuid4()
    mock.usuario_id = usuario_id or uuid.uuid4()
    
    # Fechas
    mock.fecha_union = now
    mock.fecha_salida = None
    mock.duracion_segundos = None
    
    # Estado y calidad
    mock.es_moderador = es_moderador
    mock.calidad_conexion = calidad_conexion
    mock.datos_conexion = {}
    
    # Timestamps
    mock.created_at = now
    
    return mock


def create_mock_grabacion(
    grabacion_id=None,
    videollamada_id=None,
    formato=FormatoGrabacion.MP4,
    calidad=CalidadGrabacion.HD
):
    """Helper para crear un mock de VideollamadaGrabacion."""
    now = datetime.now()
    
    mock = Mock(spec=VideollamadaGrabacion)
    mock.id = grabacion_id or uuid.uuid4()
    mock.videollamada_id = videollamada_id or uuid.uuid4()
    
    # Archivo
    mock.archivo_url = "https://example.com/recording.mp4"
    mock.nombre_archivo = "recording.mp4"
    mock.formato = formato
    mock.calidad = calidad
    
    # Detalles
    mock.duracion_segundos = 3600
    mock.tamano_bytes = 262144000  # ~250 MB
    mock.fecha_grabacion = now
    
    # Opcionales
    mock.thumbnail_url = None
    mock.transcripcion_url = None
    mock.metadatos = {}
    mock.estado_procesamiento = EstadoProcesamiento.COMPLETADO
    
    # Timestamps
    mock.created_at = now
    mock.updated_at = now
    
    return mock


# ============================
# Test Classes
# ============================

class TestHealthCheck:
    """Tests del endpoint de health check."""
    
    def test_health_check(self, client):
        """Health check debe retornar 200 OK."""
        response = client.get("/api/communication/videollamadas/health")
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        assert response.status_code == 200
        # MessageResponse tiene success y message
        data = response.json()
        assert data["success"] is True
        assert "videollamadas" in data["message"].lower()


class TestCrearVideollamada:
    """Tests de creación de videollamadas."""
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_crear_videollamada_exitosa(self, mock_service, client, sala_chat_id, mock_user):
        """Crear videollamada con datos válidos."""
        # Setup mock service
        mock_videollamada = create_mock_videollamada(
            sala_chat_id=sala_chat_id,
            tipo_llamada=TipoLlamada.VIDEO,
            titulo="Reunión de prueba",
            usuario_id_iniciador=mock_user.id
        )
        
        # Service is already mocked
        mock_service.crear_videollamada.return_value = mock_videollamada
        
        payload = {
            "sala_chat_id": str(sala_chat_id),
            "tipo_llamada": "video",
            "titulo": "Reunión de prueba"
        }
        
        response = client.post("/api/communication/videollamadas/", json=payload)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["tipo_llamada"] == "video"
        assert data["estado"] == "activa"
        # titulo no está en VideollamadaResponse, está en el modelo pero no en response
        assert "id" in data
        assert "jitsi_room_name" in data
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_crear_videollamada_tipo_voz(self, mock_service, client, sala_chat_id, mock_user):
        """Crear videollamada de tipo voz."""
        mock_videollamada = create_mock_videollamada(
            sala_chat_id=sala_chat_id,
            tipo_llamada=TipoLlamada.VOZ,
            titulo="Llamada de voz",
            usuario_id_iniciador=mock_user.id
        )
        
        # Service is already mocked
        mock_service.crear_videollamada.return_value = mock_videollamada
        
        payload = {
            "sala_chat_id": str(sala_chat_id),
            "tipo_llamada": "voz",
            "titulo": "Llamada de voz"
        }
        
        response = client.post("/api/communication/videollamadas/", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["tipo_llamada"] == "voz"
    
    def test_crear_videollamada_tipo_invalido(self, client, sala_chat_id):
        """Crear videollamada con tipo inválido debe retornar 422."""
        payload = {
            "sala_chat_id": str(sala_chat_id),
            "tipo_llamada": "invalido",
            "titulo": "Test"
        }
        
        response = client.post("/api/communication/videollamadas/", json=payload)
        assert response.status_code == 422
    
    def test_crear_videollamada_sin_sala_chat(self, client):
        """Crear videollamada sin sala_chat_id debe retornar error."""
        payload = {
            "tipo_llamada": "video",
            "titulo": "Test"
        }
        
        response = client.post("/api/communication/videollamadas/", json=payload)
        # Puede ser 422 (validación) o 500 (error del service)
        assert response.status_code in [422, 500]


class TestObtenerVideollamada:
    """Tests de obtención de videollamadas."""
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_obtener_videollamada_existente(self, mock_service, client, videollamada_id):
        """Obtener una videollamada existente."""
        mock_videollamada = create_mock_videollamada(videollamada_id=videollamada_id)
        
        # Service is already mocked
        mock_service.obtener_videollamada.return_value = mock_videollamada
        
        response = client.get(f"/api/communication/videollamadas/{videollamada_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(videollamada_id)
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_obtener_videollamada_no_existente(self, mock_service, client):
        """Obtener una videollamada que no existe debe retornar 404."""
        # Service is already mocked
        mock_service.obtener_videollamada.side_effect = VideollamadaNotFoundError("No encontrada")
        
        fake_id = uuid.uuid4()
        response = client.get(f"/api/communication/videollamadas/{fake_id}")
        
        assert response.status_code == 404


class TestListarVideollamadas:
    """Tests de listado de videollamadas."""
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_listar_videollamadas_vacias(self, mock_service, client):
        """Listar videollamadas cuando no hay ninguna."""
        # Service is already mocked
        mock_service.listar_videollamadas_activas.return_value = []
        
        response = client.get("/api/communication/videollamadas/")
        
        assert response.status_code == 200
        data = response.json()
        # Response es VideollamadaListResponse con paginación
        assert "items" in data
        assert len(data["items"]) == 0
        assert data["total"] == 0
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_listar_videollamadas_activas(self, mock_service, client):
        """Listar videollamadas activas."""
        mock_videollamadas = [
            create_mock_videollamada(estado=EstadoVideollamada.ACTIVA),
            create_mock_videollamada(estado=EstadoVideollamada.ACTIVA),
        ]
        
        # Service is already mocked
        mock_service.listar_videollamadas_activas.return_value = mock_videollamadas
        
        response = client.get("/api/communication/videollamadas/?solo_activas=true")
        
        assert response.status_code == 200
        data = response.json()
        # Response es VideollamadaListResponse con paginación
        assert "items" in data
        assert len(data["items"]) == 2
        assert data["total"] == 2


class TestUnirseVideollamada:
    """Tests de unirse a videollamada."""
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_unirse_a_videollamada_activa(self, mock_service, client, videollamada_id, mock_user):
        """Unirse a una videollamada activa."""
        mock_participante = create_mock_participante(
            videollamada_id=videollamada_id,
            usuario_id=mock_user.id
        )
        
        # Service is already mocked
        mock_service.unirse_a_videollamada.return_value = mock_participante
        
        payload = {"es_moderador": False}
        response = client.post(f"/api/communication/videollamadas/{videollamada_id}/join", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["videollamada_id"] == str(videollamada_id)
        assert data["usuario_id"] == str(mock_user.id)
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_unirse_a_videollamada_no_existente(self, mock_service, client):
        """Unirse a una videollamada que no existe debe retornar 404."""
        # Service is already mocked
        mock_service.unirse_a_videollamada.side_effect = VideollamadaNotFoundError("No encontrada")
        
        fake_id = uuid.uuid4()
        payload = {"es_moderador": False}
        response = client.post(f"/api/communication/videollamadas/{fake_id}/join", json=payload)
        
        assert response.status_code == 404


class TestSalirVideollamada:
    """Tests de salir de videollamada."""
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_salir_de_videollamada(self, mock_service, client, videollamada_id, mock_user):
        """Salir de una videollamada."""
        mock_participante = create_mock_participante(
            videollamada_id=videollamada_id,
            usuario_id=mock_user.id
        )
        mock_participante.hora_salida = datetime.now()
        mock_participante.duracion_minutos = 15
        
        # Service is already mocked
        mock_service.salir_de_videollamada.return_value = mock_participante
        
        response = client.post(f"/api/communication/videollamadas/{videollamada_id}/leave")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "videollamada_id" in data


class TestControlVideollamada:
    """Tests de control de videollamada (finalizar, cancelar)."""
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_finalizar_videollamada(self, mock_service, client, videollamada_id, mock_user):
        """Finalizar una videollamada como moderador."""
        now = datetime.now()
        
        # Mock de videollamada ACTIVA antes de finalizar
        mock_videollamada_activa = create_mock_videollamada(
            videollamada_id=videollamada_id,
            estado=EstadoVideollamada.ACTIVA,
            usuario_id_iniciador=mock_user.id
        )
        
        # Mock de videollamada FINALIZADA después
        mock_videollamada_final = create_mock_videollamada(
            videollamada_id=videollamada_id,
            estado=EstadoVideollamada.FINALIZADA,
            usuario_id_iniciador=mock_user.id
        )
        mock_videollamada_final.fecha_fin = now
        mock_videollamada_final.duracion_segundos = 1800  # 30 minutos
        
        # Service mocks
        mock_service.obtener_videollamada.return_value = mock_videollamada_activa
        mock_service.finalizar_videollamada.return_value = mock_videollamada_final
        
        response = client.post(f"/api/communication/videollamadas/{videollamada_id}/finalize")
        
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "finalizada"
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_cancelar_videollamada(self, mock_service, client, videollamada_id, mock_user):
        """Cancelar una videollamada como moderador."""
        # Mock de videollamada ACTIVA antes de cancelar
        mock_videollamada_activa = create_mock_videollamada(
            videollamada_id=videollamada_id,
            estado=EstadoVideollamada.ACTIVA,
            usuario_id_iniciador=mock_user.id
        )
        
        # Mock de videollamada CANCELADA después
        mock_videollamada_cancelada = create_mock_videollamada(
            videollamada_id=videollamada_id,
            estado=EstadoVideollamada.CANCELADA,
            usuario_id_iniciador=mock_user.id
        )
        
        # Service mocks
        mock_service.obtener_videollamada.return_value = mock_videollamada_activa
        mock_service.cancelar_videollamada.return_value = mock_videollamada_cancelada
        
        response = client.post(f"/api/communication/videollamadas/{videollamada_id}/cancel")
        
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "cancelada"


class TestGrabaciones:
    """Tests de grabaciones."""
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_agregar_grabacion(self, mock_service, client, videollamada_id, mock_user):
        """Agregar una grabación a una videollamada."""
        # Mock la videollamada para permitir permisos
        mock_videollamada = create_mock_videollamada(
            videollamada_id=videollamada_id,
            usuario_id_iniciador=mock_user.id
        )
        mock_grabacion = create_mock_grabacion(videollamada_id=videollamada_id)
        
        # Service mocks
        mock_service.obtener_videollamada.return_value = mock_videollamada
        mock_service.agregar_grabacion.return_value = mock_grabacion
        
        # Payload según GrabacionCreate schema
        payload = {
            "videollamada_id": str(videollamada_id),
            "archivo_url": "https://example.com/recording.mp4",
            "formato": "mp4",  # FormatoGrabacion.MP4.value = "mp4"
            "calidad": "HD"    # CalidadGrabacion.HD.value = "HD"
        }
        
        response = client.post(f"/api/communication/videollamadas/{videollamada_id}/recordings", json=payload)
        
        print(f"Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Error: {response.json()}")
        
        assert response.status_code == 201
        data = response.json()
        assert data["videollamada_id"] == str(videollamada_id)
        assert data["formato"] == "mp4"
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_listar_grabaciones(self, mock_service, client, videollamada_id):
        """Listar grabaciones de una videollamada."""
        mock_grabaciones = [
            create_mock_grabacion(videollamada_id=videollamada_id),
            create_mock_grabacion(videollamada_id=videollamada_id)
        ]
        
        # Service is already mocked
        mock_service.obtener_grabaciones.return_value = mock_grabaciones
        
        response = client.get(f"/api/communication/videollamadas/{videollamada_id}/recordings")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestUtilidades:
    """Tests de utilidades (generar room name, validar)."""
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_generar_room_name(self, mock_service, client):
        """Generar un room name único."""
        # Service is already mocked
        mock_service.obtener_room_name_disponible.return_value = "room-abc-123"
        
        # base_name es required query param
        response = client.get("/api/communication/videollamadas/room-name/generate?base_name=test-room")
        
        assert response.status_code == 200
        data = response.json()
        assert "room_name" in data
        assert data["room_name"] == "room-abc-123"
    
    @patch('src.api.routes.communication.videollamadas.videollamada_service')
    def test_validar_puede_unirse(self, mock_service, client, videollamada_id, mock_user):
        """Validar si un usuario puede unirse a una videollamada."""
        # Service retorna un diccionario, no una tupla
        mock_service.validar_puede_unirse.return_value = {
            "can_join": True,
            "reason": None,
            "current_participants": 5,
            "max_participants": 50
        }
        
        response = client.post(f"/api/communication/videollamadas/{videollamada_id}/validate-join")
        
        assert response.status_code == 200
        data = response.json()
        assert "can_join" in data
        assert data["can_join"] is True


class TestErrorHandling:
    """Tests de manejo de errores."""
    
    def test_uuid_invalido(self, client):
        """Usar un UUID inválido debe retornar 422."""
        response = client.get("/api/communication/videollamadas/not-a-uuid")
        
        assert response.status_code == 422
    
    def test_payload_invalido(self, client):
        """Payload inválido debe retornar error."""
        payload = {
            "tipo_llamada": "video"
            # Falta sala_chat_id (requerido ahora)
        }
        
        response = client.post("/api/communication/videollamadas/", json=payload)
        
        # Puede ser 422 (validación) o 500 (error del service)
        assert response.status_code in [422, 500]
