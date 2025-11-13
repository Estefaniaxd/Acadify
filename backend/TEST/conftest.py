"""
Configuración de pytest y fixtures compartidos para todos los tests
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from src.db.base_class import Base
# No importamos la app completa para evitar problemas de imports circulares
# from src.main import app
# from src.api.dependencies import get_db
from src.core.config import settings
from src.models.users.usuario import Usuario
from src.models.academic.institucion import Institucion

# Importar fixtures de los módulos
pytest_plugins = [
    "TEST.fixtures.academic_fixtures",
    "TEST.fixtures.periodo_inscripcion_fixtures",
]


# ==================== CONFIGURACIÓN DE BD DE TEST ====================

@pytest.fixture(scope="session")
def engine():
    """Engine de SQLite en memoria para tests"""
    # Importar modelos para que SQLAlchemy los registre
    from src.models.academic.curso import Curso
    from src.models.academic.programa import Programa
    from src.models.academic.grupo import Grupo
    from src.models.academic.periodo_academico import PeriodoAcademico
    from src.models.academic.inscripcion import Inscripcion
    from src.models.academic.estudiante_grupo import EstudianteGrupo
    from src.models.academic.grupo_curso import GrupoCurso
    
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    # Crear solo las tablas específicas que necesitamos para tests
    # (evitamos Institucion que tiene ARRAY incompatible con SQLite)
    from src.models.users.usuario import Usuario
    
    tables_to_create = [
        Usuario.__table__,
        Curso.__table__,
        Programa.__table__,
        Grupo.__table__,
        PeriodoAcademico.__table__,
        Inscripcion.__table__,
        EstudianteGrupo.__table__,
        GrupoCurso.__table__,
    ]
    
    for table in tables_to_create:
        try:
            table.create(bind=engine, checkfirst=True)
        except Exception as e:
            # Ignorar errores de tablas ya existentes o incompatibilidades
            print(f"Warning: Could not create table {table.name}: {e}")
    
    yield engine
    
    # Cleanup
    for table in tables_to_create:
        try:
            table.drop(bind=engine, checkfirst=True)
        except:
            pass
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Sesión de BD para cada test (se hace rollback al final)"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# Comentamos la fixture del client ya que no la necesitamos para tests unitarios
# @pytest.fixture(scope="function")
# def client(db_session) -> Generator[TestClient, None, None]:
#     """Cliente de test de FastAPI con BD de test"""
#     def override_get_db():
#         try:
#             yield db_session
#         finally:
#             pass
#     
#     app.dependency_overrides[get_db] = override_get_db
#     
#     with TestClient(app) as test_client:
#         yield test_client
#     
#     app.dependency_overrides.clear()


# ==================== FIXTURES DE USUARIOS ====================

@pytest.fixture
def institucion_test(db_session: Session):
    """Institución de prueba - Mock simple para tests"""
    # Para tests unitarios no necesitamos crear institucion real
    # Solo necesitamos un ID de institucion válido
    from uuid import uuid4
    
    class MockInstitucion:
        def __init__(self):
            self.institucion_id = uuid4()
            self.nombre = "Universidad de Prueba"
            self.usa_programas = True
            self.activo = True
    
    return MockInstitucion()


@pytest.fixture(scope="function")
def usuario_admin(db_session: Session, institucion_test: Institucion) -> Usuario:
    """Usuario con rol de administrador"""
    usuario = Usuario(
        usuario_id=uuid.uuid4(),
        nombres="Admin",
        apellidos="Test",
        username=f"admin_test_{uuid.uuid4().hex[:8]}",
        correo_institucional=f"admin_{uuid.uuid4().hex[:8]}@test.com",
        tipo_documento="cc",  # Minúsculas
        numero_documento=f"{uuid.uuid4().int % 1000000000}",
        rol="administrador",
        password_hash="hashed_password"
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture(scope="function")
def usuario_estudiante(db_session: Session, institucion_test: Institucion) -> Usuario:
    """Usuario con rol de estudiante"""
    usuario = Usuario(
        usuario_id=uuid.uuid4(),
        nombres="Estudiante",
        apellidos="Test",
        username=f"estudiante_test_{uuid.uuid4().hex[:8]}",
        correo_institucional=f"estudiante_{uuid.uuid4().hex[:8]}@test.com",
        tipo_documento="cc",  # Minúsculas
        numero_documento=f"{uuid.uuid4().int % 1000000000}",
        rol="estudiante",
        password_hash="hashed_password"
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture(scope="function")
def usuario_docente(db_session: Session, institucion_test: Institucion) -> Usuario:
    """Usuario con rol de docente"""
    usuario = Usuario(
        usuario_id=uuid.uuid4(),
        nombres="Docente",
        apellidos="Test",
        username=f"docente_test_{uuid.uuid4().hex[:8]}",
        correo_institucional=f"docente_{uuid.uuid4().hex[:8]}@test.com",
        tipo_documento="cc",  # Minúsculas
        numero_documento=f"{uuid.uuid4().int % 1000000000}",
        rol="docente",
        password_hash="hashed_password"
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def usuario_estudiante(db_session: Session, institucion_test: Institucion) -> Usuario:
    """Usuario con rol de estudiante"""
    usuario = Usuario(
        usuario_id=uuid.uuid4(),
        nombres="Estudiante",
        apellidos="Test",
        username=f"estudiante_test_{uuid.uuid4().hex[:8]}",  # Username único por test
        correo_institucional=f"estudiante_{uuid.uuid4().hex[:8]}@test.com",  # Email único
        tipo_documento="cc",  # Minúsculas para coincidir con ENUM
        numero_documento=f"{uuid.uuid4().int % 10000000000}",  # Número único
        rol="estudiante",
        password_hash="hashed_password"
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def usuario_docente(db_session: Session, institucion_test: Institucion) -> Usuario:
    """Usuario con rol de docente"""
    usuario = Usuario(
        usuario_id=uuid.uuid4(),
        nombres="Docente",
        apellidos="Test",
        username=f"docente_test_{uuid.uuid4().hex[:8]}",  # Username único por test
        correo_institucional=f"docente_{uuid.uuid4().hex[:8]}@test.com",  # Email único
        tipo_documento="cc",  # Minúsculas para coincidir con ENUM
        numero_documento=f"{uuid.uuid4().int % 10000000000}",  # Número único
        rol="docente",
        password_hash="hashed_password"
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


# ==================== FIXTURES DE AUTENTICACIÓN ====================
# Comentadas para tests unitarios, se pueden habilitar para tests de API

# @pytest.fixture
# def token_admin(client: TestClient, usuario_admin: Usuario) -> str:
#     """Token JWT para usuario administrador"""
#     response = client.post(
#         "/api/v1/auth/login",
#         json={
#             "email": usuario_admin.email,
#             "password": "admin123"
#         }
#     )
#     assert response.status_code == 200
#     return response.json()["access_token"]
#
#
# @pytest.fixture
# def token_estudiante(client: TestClient, usuario_estudiante: Usuario) -> str:
#     """Token JWT para usuario estudiante"""
#     response = client.post(
#         "/api/v1/auth/login",
#         json={
#             "email": usuario_estudiante.email,
#             "password": "estudiante123"
#         }
#     )
#     assert response.status_code == 200
#     return response.json()["access_token"]
#
#
# @pytest.fixture
# def token_docente(client: TestClient, usuario_docente: Usuario) -> str:
#     """Token JWT para usuario docente"""
#     response = client.post(
#         "/api/v1/auth/login",
#         json={
#             "email": usuario_docente.email,
#             "password": "docente123"
#         }
#     )
#     assert response.status_code == 200
#     return response.json()["access_token"]
#
#
# @pytest.fixture
# def auth_headers_admin(token_admin: str) -> dict:
#     """Headers de autenticación para admin"""
#     return {"Authorization": f"Bearer {token_admin}"}
#
#
# @pytest.fixture
# def auth_headers_estudiante(token_estudiante: str) -> dict:
#     """Headers de autenticación para estudiante"""
#     return {"Authorization": f"Bearer {token_estudiante}"}
#
#
# @pytest.fixture
# def auth_headers_docente(token_docente: str) -> dict:
#     """Headers de autenticación para docente"""
#     return {"Authorization": f"Bearer {token_docente}"}


# ==================== FIXTURES DE FECHAS ====================

@pytest.fixture
def fecha_hoy() -> date:
    """Fecha actual"""
    return date.today()


@pytest.fixture
def fecha_ayer() -> date:
    """Fecha de ayer"""
    return date.today() - timedelta(days=1)


@pytest.fixture
def fecha_manana() -> date:
    """Fecha de mañana"""
    return date.today() + timedelta(days=1)


@pytest.fixture
def fecha_proxima_semana() -> date:
    """Fecha en una semana"""
    return date.today() + timedelta(days=7)


@pytest.fixture
def fecha_mes_pasado() -> date:
    """Fecha de hace un mes"""
    return date.today() - timedelta(days=30)


@pytest.fixture
def fecha_proximo_mes() -> date:
    """Fecha en un mes"""
    return date.today() + timedelta(days=30)


# ==================== MARKERS DE PYTEST ====================

def pytest_configure(config):
    """Configuración de markers personalizados"""
    config.addinivalue_line(
        "markers", "unit: Tests unitarios de modelos"
    )
    config.addinivalue_line(
        "markers", "crud: Tests de operaciones CRUD"
    )
    config.addinivalue_line(
        "markers", "service: Tests de capa de servicio"
    )
    config.addinivalue_line(
        "markers", "api: Tests de endpoints API"
    )
    config.addinivalue_line(
        "markers", "integration: Tests de integración"
    )
    config.addinivalue_line(
        "markers", "slow: Tests que tardan más de 1 segundo"
    )


# ==================== FIXTURES ASYNC (si son necesarios) ====================

@pytest.fixture(scope="session")
def event_loop():
    """Event loop para tests asíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== UTILIDADES ====================

@pytest.fixture
def faker_seed():
    """Seed fijo para Faker para tests reproducibles"""
    return 42


# ==================== TEST DATA BUILDERS - FIXTURES PROFESIONALES ====================

# Importar los builders
try:
    from TEST.test_data_builders import (
        EvaluacionBuilder,
        PreguntaBuilder,
        IntentoBuilder,
        ConfiguracionAntiTrampaBuilder,
        CursoBuilder,
        EvaluacionMother,
        PreguntaMother,
    )
    
    @pytest.fixture
    def evaluacion_builder():
        """Builder de Evaluacion para tests"""
        return EvaluacionBuilder()
    
    @pytest.fixture
    def pregunta_builder():
        """Builder de Pregunta para tests"""
        return PreguntaBuilder()
    
    @pytest.fixture
    def intento_builder():
        """Builder de Intento para tests"""
        return IntentoBuilder()
        
    @pytest.fixture
    def evaluacion_quiz():
        """Quiz simple para pruebas"""
        return EvaluacionMother.quiz_simple()
    
    @pytest.fixture
    def evaluacion_examen():
        """Examen formal para pruebas"""
        return EvaluacionMother.examen_final()
        
except ImportError:
    # Si no están disponibles los builders, continuar sin ellos
    pass
