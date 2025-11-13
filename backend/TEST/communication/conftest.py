"""Fixtures para tests del sistema de comunicación.

Proporciona fixtures reutilizables para:
- Usuarios (emisor, receptor)
- Salas de chat (curso, grupo, privado)
- Mensajes (texto, archivos, respuestas)
- Videollamadas (activas, finalizadas)
- Participantes
- Notificaciones
- Configuraciones
"""

import sys
from pathlib import Path
from datetime import datetime, UTC, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

# Agregar directorio parent al path para imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Importar fixtures base del conftest de e2e
from e2e.conftest import test_engine, db_session, admin_token  # noqa: F401

# Override fixture para asegurar que las tablas de comunicación se creen correctamente
@pytest.fixture(scope="session", autouse=True)
def ensure_communication_tables(test_engine):
    """Fuerza la creación de tablas de comunicación usando SQLAlchemy metadata.
    
    Las tablas deberían crearse automáticamente con Base.metadata.create_all()
    en test_engine, pero verificamos y forzamos si es necesario.
    """
    from sqlalchemy import inspect
    from src.db.base_class import Base
    
    inspector = inspect(test_engine)
    existing_tables = inspector.get_table_names()
    
    # Verificar si las tablas de comunicación existen
    communication_tables = ["salas_chat", "mensajes", "videollamadas", "participantes_sala"]
    missing_tables = [t for t in communication_tables if t not in existing_tables]
    
    if missing_tables:
        print(f"\n⚠️  Faltan tablas de comunicación: {missing_tables}")
        print("🔧 Forzando creación con Base.metadata.create_all()...")
        
        # Crear solo las tablas de los modelos de comunicación
        from src.models.communication.chat import SalaChat, ParticipanteSala, LecturaMensaje, Notificacion, ConfiguracionNotificaciones
        from src.models.communication.mensaje import Mensaje
        from src.models.communication.videollamada import Videollamada, VideollamadaParticipante, VideollamadaGrabacion
        
        try:
            # Crear tablas individuales para evitar errores de FK
            for table in Base.metadata.sorted_tables:
                if table.name in communication_tables + ["lecturas_mensajes", "notificaciones", "configuracion_notificaciones", "videollamadas_participantes", "videollamadas_grabaciones"]:
                    try:
                        table.create(bind=test_engine, checkfirst=True)
                        print(f"  ✓ Tabla creada: {table.name}")
                    except Exception as e:
                        print(f"  ✗ Error creando {table.name}: {e}")
        except Exception as e:
            print(f"⚠️  Error durante creación de tablas: {e}")
            print("Esto puede ser normal si las tablas ya existen o hay conflictos de FK.")
        
        # Verificar que se crearon
        inspector = inspect(test_engine)
        existing_tables = inspector.get_table_names()
        still_missing = [t for t in communication_tables if t not in existing_tables]
        
        if still_missing:
            print(f"⚠️  Tablas con tipos PostgreSQL incompatibles: {still_missing}")
            print("🔧 Creando manualmente con tipos compatibles SQLite...")
            
            # Crear videollamadas manualmente (JSONB → JSON/TEXT)
            if "videollamadas" in still_missing:
                from sqlalchemy import text
                with test_engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS videollamadas (
                            id TEXT PRIMARY KEY,
                            jitsi_room_name VARCHAR(255) UNIQUE NOT NULL,
                            tipo_llamada VARCHAR(50) NOT NULL,
                            sala_chat_id TEXT,
                            iniciador_id TEXT NOT NULL,
                            estado VARCHAR(50) NOT NULL,
                            fecha_inicio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            fecha_fin TIMESTAMP,
                            duracion_segundos INTEGER,
                            grabacion_url VARCHAR(500),
                            transcripcion TEXT,
                            resumen_ia TEXT,
                            configuracion TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            deleted_at TIMESTAMP
                        )
                    """))
                    
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS videollamada_participantes (
                            id TEXT PRIMARY KEY,
                            videollamada_id TEXT NOT NULL,
                            usuario_id TEXT NOT NULL,
                            es_moderador BOOLEAN,
                            fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            fecha_salida TIMESTAMP,
                            duracion_segundos INTEGER,
                            calidad_conexion VARCHAR(50),
                            datos_conexion TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS videollamada_grabaciones (
                            id TEXT PRIMARY KEY,
                            videollamada_id TEXT NOT NULL,
                            archivo_url VARCHAR(500) NOT NULL,
                            duracion_segundos INTEGER,
                            tamano_bytes BIGINT,
                            formato VARCHAR(20),
                            thumbnail_url VARCHAR(500),
                            calidad VARCHAR(20),
                            estado_procesamiento VARCHAR(50) NOT NULL DEFAULT 'PENDIENTE',
                            metadatos TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            deleted_at TIMESTAMP
                        )
                    """))
                    
                    conn.commit()
                    print("  ✓ Tablas de videollamadas creadas manualmente")
        
        # Verificación final
        inspector = inspect(test_engine)
        existing_tables = inspector.get_table_names()
        final_missing = [t for t in communication_tables if t not in existing_tables]
        
        if not final_missing:
            print("✅ Todas las tablas de comunicación están disponibles\n")
        else:
            print(f"❌ No se pudieron crear: {final_missing}\n")
    
    return test_engine

# Importar modelos
from src.models.communication.chat import SalaChat, ParticipanteSala, TipoSala
from src.models.communication.mensaje import Mensaje
from src.models.communication.videollamada import (
    Videollamada,
    VideollamadaParticipante,
)
from src.models.users.usuario import Usuario

# Importar enums
from src.enums.communication.videollamada_enums import (
    TipoLlamada,
    EstadoVideollamada,
)
from src.enums.users.usuario_enums import TipoDocumentoUsuario, RolUsuario

# Importar servicios
from src.services.auth.password_service import PasswordService


# ==================== FIXTURES DE USUARIOS ====================


@pytest.fixture
def usuario_emisor(db_session: Session) -> Usuario:
    """
    Usuario que actúa como emisor/creador (docente).
    """
    password_service = PasswordService()
    
    # Generar correo único para evitar conflictos entre tests
    unique_suffix = str(uuid4())[:8]
    
    # Crear el objeto Usuario directamente
    usuario = Usuario(
        usuario_id=uuid4(),  # UUID object (not string) - SQLAlchemy expects UUID(as_uuid=True)
        # username NO se proporciona para roles no-administrador (CHECK constraint)
        correo_institucional=f"carlos.docente.{unique_suffix}@acadify.edu",
        nombres="Carlos",
        apellidos="Rodríguez",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"123{unique_suffix[:7]}",  # Número único
        rol=RolUsuario.docente,
        password_hash=password_service.hash_password("DocTest123!"),
        email_verified=True,
    )
    
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def usuario_receptor(db_session: Session) -> Usuario:
    """
    Usuario que actúa como receptor (estudiante).
    """
    password_service = PasswordService()
    
    # Generar correo único para evitar conflictos entre tests
    unique_suffix = str(uuid4())[:8]
    
    usuario = Usuario(
        usuario_id=uuid4(),  # UUID object (not string)
        # username NO se proporciona para roles no-administrador (CHECK constraint)
        correo_institucional=f"maria.estudiante.{unique_suffix}@acadify.edu",
        nombres="María",
        apellidos="García",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"098{unique_suffix[:7]}",  # Número único
        rol=RolUsuario.estudiante,
        password_hash=password_service.hash_password("EstTest123!"),
        email_verified=True,
    )
    
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def usuario_adicional(db_session: Session) -> Usuario:
    """
    Usuario adicional (estudiante) para tests que requieren múltiples participantes.
    """
    password_service = PasswordService()
    
    # Generar correo único para evitar conflictos entre tests
    unique_suffix = str(uuid4())[:8]
    
    usuario = Usuario(
        usuario_id=uuid4(),  # UUID object (not string)
        # username NO se proporciona para roles no-administrador (CHECK constraint)
        correo_institucional=f"pedro.estudiante.{unique_suffix}@acadify.edu",
        nombres="Pedro",
        apellidos="Martínez",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"555{unique_suffix[:7]}",  # Número único
        rol=RolUsuario.estudiante,
        password_hash=password_service.hash_password("EstTest123!"),
        email_verified=True,
    )
    
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


# ==================== FIXTURES DE SALAS DE CHAT ====================


@pytest.fixture
def sala_chat_curso(db_session: Session, usuario_emisor: Usuario) -> SalaChat:
    """Sala de chat de tipo curso."""
    sala = SalaChat(
        id=uuid4(),
        nombre="Programación I - Sala de Chat",
        descripcion="Chat del curso de Programación I",
        tipo_sala=TipoSala.CURSO,
        curso_id=uuid4(),  # Simular curso existente
        es_publica=True,
        requiere_aprobacion=False,
        permite_archivos=True,
        permite_menciones=True,
        permite_hilos=True,
        max_participantes=50,
        creador_id=usuario_emisor.usuario_id,
        esta_activa=True,
        total_mensajes=0,
    )

    db_session.add(sala)
    db_session.commit()
    db_session.refresh(sala)

    return sala


@pytest.fixture
def sala_chat_privada(
    db_session: Session, usuario_emisor: Usuario, usuario_receptor: Usuario
) -> SalaChat:
    """Sala de chat privada entre dos usuarios."""
    sala = SalaChat(
        id=uuid4(),
        nombre="Chat Privado",
        descripcion="Conversación privada",
        tipo_sala=TipoSala.PRIVADO,
        es_publica=False,
        requiere_aprobacion=False,
        permite_archivos=True,
        permite_menciones=False,
        permite_hilos=False,
        creador_id=usuario_emisor.usuario_id,
        esta_activa=True,
        total_mensajes=0,
    )

    db_session.add(sala)
    db_session.commit()

    # Agregar participantes
    participante1 = ParticipanteSala(
        id=uuid4(),
        sala_id=sala.id,
        usuario_id=usuario_emisor.usuario_id,
        rol="creador",
        es_admin=True,
        puede_escribir=True,
        esta_activo=True,
        notificaciones_activas=True,
        mensajes_no_leidos=0,
    )

    participante2 = ParticipanteSala(
        id=uuid4(),
        sala_id=sala.id,
        usuario_id=usuario_receptor.usuario_id,
        rol="miembro",
        puede_escribir=True,
        esta_activo=True,
        notificaciones_activas=True,
        mensajes_no_leidos=0,
    )

    db_session.add_all([participante1, participante2])
    db_session.commit()
    db_session.refresh(sala)

    return sala


# ==================== FIXTURES DE MENSAJES ====================


@pytest.fixture
def mensaje_texto(
    db_session: Session, sala_chat_curso: SalaChat, usuario_emisor: Usuario
) -> Mensaje:
    """Mensaje de texto básico."""
    mensaje = Mensaje(
        id=uuid4(),
        sala_id=sala_chat_curso.id,
        usuario_id=usuario_emisor.usuario_id,
        contenido="Hola a todos, bienvenidos al curso!",
        contenido_html="<p>Hola a todos, bienvenidos al curso!</p>",
        tipo_mensaje="texto",
        estado="enviado",
        es_importante=False,
        es_respuesta=False,
        tiene_respuestas=False,
        numero_respuestas=0,
        fecha_creacion=datetime.now(UTC),
    )

    db_session.add(mensaje)
    db_session.commit()
    db_session.refresh(mensaje)

    return mensaje


# ==================== FIXTURES DE VIDEOLLAMADAS ====================


@pytest.fixture
def videollamada_activa(
    db_session: Session, sala_chat_curso: SalaChat, usuario_emisor: Usuario
) -> Videollamada:
    """Videollamada activa en curso.
    
    Note: Uses CRUD method to ensure initiator is automatically added as participant.
    """
    from src.crud.communication.videollamada import CRUDVideollamada
    
    crud = CRUDVideollamada()
    videollamada = crud.create_videollamada(
        db=db_session,
        jitsi_room_name=f"room-test-{uuid4().hex[:8]}",
        tipo_llamada=TipoLlamada.VIDEO,
        sala_chat_id=sala_chat_curso.id,
        iniciador_id=usuario_emisor.usuario_id,
        configuracion={"max_participantes": 10, "grabar": True},
    )

    return videollamada


@pytest.fixture
def participante_videollamada(
    db_session: Session, videollamada_activa: Videollamada, usuario_emisor: Usuario
) -> VideollamadaParticipante:
    """Participante en videollamada (el iniciador)."""
    participante = VideollamadaParticipante(
        id=uuid4(),
        videollamada_id=videollamada_activa.id,
        usuario_id=usuario_emisor.usuario_id,
        es_moderador=True,
        fecha_union=datetime.now(UTC),
        datos_conexion={},
    )

    db_session.add(participante)
    db_session.commit()
    db_session.refresh(participante)

    return participante
