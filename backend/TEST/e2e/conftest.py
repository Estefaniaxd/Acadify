"""Configuración de pytest para tests E2E.

Proporciona fixtures comunes para:
- Base de datos de prueba
- Cliente HTTP (TestClient)
- Tokens de autenticación
- Limpieza entre tests
"""

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.config import settings
from src.db.base_class import Base
from src.main import app

# Importar modelos principales requeridos para los tests E2E
from src.models.academic.clase import Clase  # noqa: F401
from src.models.academic.curso import Curso  # noqa: F401
from src.models.academic.grupo import Grupo  # noqa: F401
from src.models.academic.inscripcion import Inscripcion  # noqa: F401
from src.models.academic.institucion import Institucion  # noqa: F401
from src.models.academic.programa import Programa  # noqa: F401
from src.models.auth.invitation_token import InvitationToken  # noqa: F401
from src.models.evaluaciones.configuracion_antitrampa import ConfiguracionAntiTrampa  # noqa: F401
from src.models.users.administrador_sistema import AdministradorSistema  # noqa: F401
from src.models.users.coordinador import Coordinador  # noqa: F401
from src.models.users.docente import Docente  # noqa: F401
from src.models.users.estudiante import Estudiante  # noqa: F401
from src.models.users.usuario import Usuario  # noqa: F401

# Importar modelos de comunicación (para tests de chat y videollamadas)
from src.models.communication.archivo_chat import ArchivoChat  # noqa: F401
from src.models.communication.chat import (  # noqa: F401
    ConfiguracionNotificaciones,
    LecturaMensaje,
    Notificacion,
    ParticipanteSala,
    SalaChat,
)
from src.models.communication.mensaje import Mensaje  # noqa: F401
from src.models.communication.mensaje_bot import MensajeBot  # noqa: F401
from src.models.communication.reaccion import Reaccion, ReaccionMensaje  # noqa: F401
from src.models.communication.videollamada import (  # noqa: F401
    Videollamada,
    VideollamadaGrabacion,
    VideollamadaParticipante,
)


# ==================== DATABASE FIXTURES ====================


@pytest.fixture(scope="session")
def test_engine():
    """Crea engine de base de datos de prueba en memoria."""
    # Usar SQLite en memoria para tests rápidos
    # Para tests con PostgreSQL real, usar: settings.DATABASE_URL + "_test"
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Deshabilitar FKs para SQLite (evita problemas con tablas referenciadas no creadas)
    from sqlalchemy import event
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.close()
    
    # Intentar crear todas las tablas (ignorar errores de FK)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Si falla, intentar crear las tablas individualmente
        print(f"Warning: Could not create all tables at once: {e}")
        # Crear las tablas en el orden correcto manualmente
        tables_in_order = [
            "Usuario",
            "AdministradorSistema",
            "Coordinador",
            "Docente",
            "Estudiante",
            "Institucion",
            "InstitucionCoordinador",
            "invitation_tokens",
            "Programa",
            "Curso",
            "Grupo",
            "Clase",
            "inscripciones",
        ]
        # Crear tabla Institucion manualmente para SQLite (evitar JSONB y ARRAY)
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS "Institucion" (
                    institucion_id TEXT PRIMARY KEY,
                    administrador_id_creador TEXT,
                    nombre VARCHAR(150) UNIQUE NOT NULL,
                    sigla VARCHAR(20) UNIQUE,
                    lema VARCHAR(255),
                    tipo_institucion VARCHAR(50) NOT NULL,
                    usa_programas BOOLEAN NOT NULL,
                    nivel_educativo VARCHAR(50) NOT NULL,
                    sector VARCHAR(50) NOT NULL,
                    direccion VARCHAR(255),
                    ciudad VARCHAR(100),
                    pais VARCHAR(100) NOT NULL,
                    correo_institucional VARCHAR(100) UNIQUE NOT NULL,
                    telefono VARCHAR(30) NOT NULL,
                    nit VARCHAR(20) UNIQUE,
                    website VARCHAR(255),
                    redes_sociales TEXT,
                    logo_url VARCHAR(500) NOT NULL DEFAULT '',
                    color_primario VARCHAR(7),
                    color_secundario VARCHAR(7),
                    modalidad_ensenanza VARCHAR(10) NOT NULL DEFAULT 'presencial',
                    tipo_calendario VARCHAR(13),
                    jornadas TEXT,
                    dominio_principal VARCHAR(100),
                    dominios_adicionales TEXT,
                    acreditacion_nacional VARCHAR(150),
                    acreditacion_internacional VARCHAR(150),
                    fecha_acreditacion TIMESTAMP,
                    capacidad_estudiantes INTEGER,
                    numero_estudiantes_actual INTEGER DEFAULT 0,
                    numero_docentes INTEGER DEFAULT 0,
                    numero_programas_activos INTEGER DEFAULT 0,
                    configuracion_regional TEXT,
                    campos_personalizados TEXT,
                    estado VARCHAR(50) NOT NULL DEFAULT 'pendiente',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_activacion TIMESTAMP,
                    FOREIGN KEY (administrador_id_creador) REFERENCES "Usuario" (usuario_id) ON DELETE SET NULL
                )
            """))
            conn.commit()
            print("✓ Created table: Institucion (manual)")
        
        # Crear las demás tablas en orden
        for table_name in tables_in_order:
            if table_name == "Institucion":
                continue  # Ya la creamos manualmente
            for table in Base.metadata.sorted_tables:
                if table.name == table_name:
                    try:
                        table.create(bind=engine, checkfirst=True)
                        print(f"✓ Created table: {table_name}")
                    except Exception as create_error:
                        print(f"✗ Failed to create {table_name}: {create_error}")
                    break
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Proporciona sesión de base de datos para cada test.
    
    Se hace rollback después de cada test para mantener aislamiento.
    """
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )
    
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Cliente HTTP de prueba con override de dependencias."""
    from src.api.deps import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ==================== AUTHENTICATION FIXTURES ====================


@pytest.fixture
def admin_token(db_session: Session) -> str:
    """Token JWT para usuario administrador."""
    from datetime import UTC, datetime, timedelta
    from uuid import uuid4
    
    from jose import jwt
    
    from src.enums.users.usuario_enums import (
        EstadoCuentaUsuario,
        RolUsuario,
        TipoDocumentoUsuario,
    )
    from src.models.users.administrador_sistema import AdministradorSistema
    from src.models.users.usuario import Usuario
    from src.services.auth.password_service import PasswordService
    
    password_service = PasswordService()
    
    # Crear usuario base (Admin usa username, NO correo_institucional)
    unique_id = uuid4().hex[:8]
    usuario = Usuario(
        usuario_id=uuid4(),
        username=f"admin_e2e_{unique_id}",  # Admin usa username único
        correo_institucional=None,  # Admin NO tiene correo institucional
        nombres="Admin",
        apellidos="Test E2E",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento="1234567890",
        rol=RolUsuario.administrador,
        password_hash=password_service.hash_password("Admin123!"),
        estado_cuenta=EstadoCuentaUsuario.activo,
        email_verified=True,
    )
    db_session.add(usuario)
    db_session.flush()
    
    # Crear administrador
    admin = AdministradorSistema(
        administrador_id=usuario.usuario_id,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(usuario)
    
    # Generar token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(UTC) + access_token_expires
    
    to_encode = {
        "sub": str(usuario.usuario_id),
        "tipo": "administrador",
        "exp": expire,
    }
    
    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return token


@pytest.fixture
def coordinador_token(db_session: Session) -> str:
    """Token JWT para coordinador de prueba."""
    from datetime import UTC, datetime, timedelta
    from uuid import uuid4

    from jose import jwt

    from src.enums.users.usuario_enums import (
        EstadoCuentaUsuario,
        RolUsuario,
        TipoDocumentoUsuario,
    )
    from src.models.users.coordinador import Coordinador
    from src.models.users.usuario import Usuario
    from src.services.auth.password_service import PasswordService
    
    password_service = PasswordService()
    
    # Generar correo único para evitar conflictos
    unique_id = uuid4().hex[:8]
    
    # Coordinador usa correo_institucional (NO username)
    usuario = Usuario(
        usuario_id=uuid4(),
        correo_institucional=f"coord_{unique_id}@test.com",
        username=None,  # Solo admin usa username
        nombres="Coordinador",
        apellidos="Test E2E",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento="1234567891",
        rol=RolUsuario.coordinador,
        password_hash=password_service.hash_password("Coord123!"),
        estado_cuenta=EstadoCuentaUsuario.activo,
        email_verified=True,
    )
    db_session.add(usuario)
    db_session.flush()
    
    # Coordinador solo tiene: coordinador_id, horario_atencion, fecha_inicio_carrera
    from datetime import date
    coordinador = Coordinador(
        coordinador_id=usuario.usuario_id,
        horario_atencion="Lun-Vie 8:00-17:00",
        fecha_inicio_carrera=date(2024, 1, 15),
    )
    db_session.add(coordinador)
    db_session.commit()
    db_session.refresh(usuario)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(UTC) + access_token_expires
    
    to_encode = {
        "sub": str(usuario.usuario_id),
        "tipo": "coordinador",
        "exp": expire,
    }
    
    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return token


@pytest.fixture
def estudiante_token(db_session: Session) -> str:
    """Token JWT para estudiante de prueba."""
    from datetime import UTC, datetime, timedelta
    from uuid import uuid4
    
    from jose import jwt
    
    from src.enums.users.usuario_enums import (
        EstadoCuentaUsuario,
        RolUsuario,
        TipoDocumentoUsuario,
    )
    from src.models.users.estudiante import Estudiante
    from src.models.users.usuario import Usuario
    from src.services.auth.password_service import PasswordService
    
    password_service = PasswordService()
    
    # Generar correo único para evitar conflictos
    unique_id = uuid4().hex[:8]
    
    # Estudiante usa correo_institucional, NO username
    usuario = Usuario(
        usuario_id=uuid4(),
        correo_institucional=f"estudiante_{unique_id}@test.com",
        username=None,  # Solo admin usa username
        nombres="Estudiante",
        apellidos="Test E2E",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento="1234567892",
        rol=RolUsuario.estudiante,
        password_hash=password_service.hash_password("Estudiante123!"),
        estado_cuenta=EstadoCuentaUsuario.activo,
        email_verified=True,
    )
    db_session.add(usuario)
    db_session.flush()
    
    # Estudiante solo tiene: estudiante_id, programa_id, fecha_ingreso, etapa_formativa, etc
    from datetime import date
    from src.enums.users.estudiante_enums import EtapaFormativaEstudiante
    estudiante = Estudiante(
        estudiante_id=usuario.usuario_id,
        programa_id=None,  # Opcional
        fecha_ingreso=date(2024, 1, 15),
        etapa_formativa=EtapaFormativaEstudiante.i,
        creditos_aprobados=0,
        promedio_acumulado=None,
    )
    db_session.add(estudiante)
    db_session.commit()
    db_session.refresh(usuario)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(UTC) + access_token_expires
    
    to_encode = {
        "sub": str(usuario.usuario_id),
        "tipo": "estudiante",
        "exp": expire,
    }
    
    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return token


@pytest.fixture
def docente_token(db_session: Session) -> str:
    """Token JWT para docente de prueba."""
    from datetime import UTC, datetime, timedelta
    from uuid import uuid4
    
    from jose import jwt
    
    from src.enums.users.usuario_enums import (
        EstadoCuentaUsuario,
        RolUsuario,
        TipoDocumentoUsuario,
    )
    from src.models.users.docente import Docente
    from src.models.users.usuario import Usuario
    from src.services.auth.password_service import PasswordService
    
    password_service = PasswordService()
    
    # Generar correo único para evitar conflictos
    unique_id = uuid4().hex[:8]
    
    # Docente usa correo_institucional, NO username
    usuario = Usuario(
        usuario_id=uuid4(),
        correo_institucional=f"docente_{unique_id}@test.com",
        username=None,  # Solo admin usa username
        nombres="Docente",
        apellidos="Test E2E",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento="1234567893",
        rol=RolUsuario.docente,
        password_hash=password_service.hash_password("Docente123!"),
        estado_cuenta=EstadoCuentaUsuario.activo,
        email_verified=True,
    )
    db_session.add(usuario)
    db_session.flush()
    
    # Docente solo tiene: docente_id, area_conocimiento, fecha_vinculacion, tipo_vinculacion, etc
    from datetime import date
    from src.enums.users.docente_enums import TipoVinculacionDocente
    docente = Docente(
        docente_id=usuario.usuario_id,
        area_conocimiento="Ingeniería de Software",
        fecha_vinculacion=date(2024, 1, 15),
        tipo_vinculacion=TipoVinculacionDocente.planta,
        titulo_academico="Magister en Software",
        horas_semanales=40,
    )
    db_session.add(docente)
    db_session.commit()
    db_session.refresh(usuario)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(UTC) + access_token_expires
    
    to_encode = {
        "sub": str(usuario.usuario_id),
        "tipo": "docente",
        "exp": expire,
    }
    
    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return token


# ==================== UTILITY FIXTURES ====================


@pytest.fixture
def clear_database(db_session: Session):
    """Limpia todas las tablas después del test."""
    yield
    
    # Limpiar todas las tablas en orden inverso de dependencias
    tables = [
        "HistorialAccesoClase",
        "MaterialClase",
        "Clase",
        "GrupoCurso",
        "Grupo",
        "inscripciones",
        "Curso",
        "Programa",
        "PeriodoAcademico",
        "Institucion",
        "Estudiante",
        "Docente",
        "Coordinador",
        "Administrador",
        "Usuario",
    ]
    
    for table in tables:
        try:
            db_session.execute(text(f"DELETE FROM {table}"))
            db_session.commit()
        except Exception:
            # Tabla no existe o error, continuar
            db_session.rollback()


@pytest.fixture
def sample_data_generator():
    """Generador de datos de prueba consistentes."""
    from datetime import UTC, datetime
    from uuid import uuid4
    
    class DataGenerator:
        """Clase helper para generar datos de prueba."""
        
        @staticmethod
        def generate_uuid():
            """Genera UUID único."""
            return uuid4()
        
        @staticmethod
        def generate_email(prefix: str = "test"):
            """Genera email único."""
            timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
            return f"{prefix}_{timestamp}@test.com"
        
        @staticmethod
        def generate_codigo(prefix: str = "TEST"):
            """Genera código único."""
            timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
            return f"{prefix}{timestamp}"
    
    return DataGenerator()


# ==================== IMPORT FIXTURES FROM fixtures/e2e_fixtures.py ====================
# Importar todas las fixtures de e2e_fixtures.py para que pytest las reconozca
import sys
from pathlib import Path

# Agregar el directorio TEST al path si no está
test_dir = Path(__file__).parent.parent
if str(test_dir) not in sys.path:
    sys.path.insert(0, str(test_dir))

# Importar las fixtures
from fixtures.e2e_fixtures import (
    institucion_completa,
    institucion_con_coordinador,
    coordinador_test,
    docente_test,
    estudiante_test,
    programa_test,
    curso_test,
    grupo_test,
    clase_test,
    flujo_completo,
    create_bulk_estudiantes,
    bulk_estudiantes,
)

# Asegurar que pytest reconozca las fixtures importadas
__all__ = [
    "institucion_completa",
    "institucion_con_coordinador",
    "coordinador_test",
    "docente_test",
    "estudiante_test",
    "programa_test",
    "curso_test",
    "grupo_test",
    "clase_test",
    "flujo_completo",
    "create_bulk_estudiantes",
    "bulk_estudiantes",
]
