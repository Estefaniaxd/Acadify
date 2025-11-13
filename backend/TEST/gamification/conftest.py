"""Fixtures para tests de gamificación."""

import pytest
from datetime import datetime, UTC
from uuid import uuid4
from sqlalchemy.orm import Session

from src.models.users.usuario import Usuario
from src.models.gamification.historial_puntos import HistorialPuntos
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.models.gamification.recompensa import Recompensa
from src.models.gamification.usuario_recompensa import UsuarioRecompensa
from src.models.gamification.insignia import Insignia
from src.models.gamification.usuario_insignia import UsuarioInsignia
from src.models.avatar.user_avatar import UserAvatar
from src.enums.users.usuario_enums import TipoDocumentoUsuario, RolUsuario
from src.enums.gamification.recompensa_enums import TipoRecompensa
from src.enums.gamification.insignia_enums import TipoInsignia
from src.services.auth.password_service import PasswordService


# ==================== SETUP DE TABLAS ====================


@pytest.fixture(scope="session", autouse=True)
def ensure_gamification_tables(engine):
    """Asegurar que las tablas de gamificación existan."""
    from sqlalchemy import inspect, text
    from src.db.base_class import Base
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    required_tables = [
        'UsuarioPuntos', 'HistorialPuntos', 'Recompensa', 
        'UsuarioRecompensa', 'Insignia', 'UsuarioInsignia', 'user_avatar'
    ]
    
    missing_tables = [t for t in required_tables if t not in existing_tables]
    
    if missing_tables:
        print(f"\n⚠️  Faltan tablas de gamificación: {missing_tables}")
        
        try:
            # Intentar crear con SQLAlchemy
            Base.metadata.create_all(bind=engine, checkfirst=True)
            print("✅ Tablas de gamificación creadas con SQLAlchemy")
        except Exception as e:
            print(f"⚠️  Error creando tablas: {e}")
            # Crear manualmente para SQLite
            with engine.connect() as conn:
                # UsuarioPuntos
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS UsuarioPuntos (
                        usuario_id TEXT PRIMARY KEY,
                        puntos_acumulados INTEGER NOT NULL DEFAULT 0,
                        cambio INTEGER NOT NULL,
                        motivo TEXT,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE,
                        CHECK (cambio <> 0)
                    )
                """))
                
                # HistorialPuntos
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS HistorialPuntos (
                        historial_id TEXT PRIMARY KEY,
                        usuario_id TEXT NOT NULL,
                        cambio INTEGER NOT NULL,
                        motivo TEXT,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE,
                        CHECK (cambio <> 0)
                    )
                """))
                
                # Recompensa
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS Recompensa (
                        recompensa_id TEXT PRIMARY KEY,
                        nombre VARCHAR(100) NOT NULL,
                        descripcion TEXT,
                        costo_puntos INTEGER NOT NULL,
                        tipo VARCHAR(50) NOT NULL DEFAULT 'otro',
                        CHECK (costo_puntos >= 0)
                    )
                """))
                
                # UsuarioRecompensa
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS UsuarioRecompensa (
                        usuario_recompensa_id TEXT PRIMARY KEY,
                        usuario_id TEXT NOT NULL,
                        recompensa_id TEXT NOT NULL,
                        fecha_canje TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE,
                        FOREIGN KEY (recompensa_id) REFERENCES Recompensa(recompensa_id) ON DELETE CASCADE
                    )
                """))
                
                # Insignia
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS Insignia (
                        insignia_id TEXT PRIMARY KEY,
                        nombre VARCHAR(100) NOT NULL UNIQUE,
                        descripcion TEXT,
                        imagen_url TEXT,
                        tipo VARCHAR(50) NOT NULL DEFAULT 'manual',
                        es_unica BOOLEAN NOT NULL
                    )
                """))
                
                # UsuarioInsignia
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS UsuarioInsignia (
                        usuario_id TEXT NOT NULL,
                        insignia_id TEXT NOT NULL,
                        otorgada_por TEXT,
                        fecha_otorgada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (usuario_id, insignia_id),
                        FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE,
                        FOREIGN KEY (insignia_id) REFERENCES Insignia(insignia_id) ON DELETE CASCADE,
                        FOREIGN KEY (otorgada_por) REFERENCES Usuario(usuario_id) ON DELETE SET NULL
                    )
                """))
                
                # user_avatar
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS user_avatar (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        base_gender VARCHAR(20) NOT NULL DEFAULT 'male',
                        layers TEXT NOT NULL,
                        image_url VARCHAR(500) NOT NULL,
                        layers_hash VARCHAR(64) NOT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT 0,
                        is_public BOOLEAN NOT NULL DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE
                    )
                """))
                
                conn.commit()
                print("✅ Tablas de gamificación creadas manualmente (SQLite)")
    else:
        print("✅ Todas las tablas de gamificación ya existen")


# ==================== FIXTURES DE USUARIOS ====================


@pytest.fixture
def password_service():
    """Servicio de passwords."""
    return PasswordService()


@pytest.fixture
def estudiante_1(db_session: Session, password_service: PasswordService) -> Usuario:
    """Estudiante para tests de gamificación."""
    unique_suffix = str(uuid4())[:8]
    usuario = Usuario(
        usuario_id=uuid4(),
        correo_institucional=f"estudiante1.{unique_suffix}@acadify.edu",
        nombres="Carlos",
        apellidos="Estudiante",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"100{unique_suffix[:7]}",
        rol=RolUsuario.estudiante,
        password_hash=password_service.hash_password("Estudiante123!"),
        email_verified=True,
    )
    
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    
    return usuario


@pytest.fixture
def estudiante_2(db_session: Session, password_service: PasswordService) -> Usuario:
    """Segundo estudiante para tests de ranking."""
    unique_suffix = str(uuid4())[:8]
    usuario = Usuario(
        usuario_id=uuid4(),
        correo_institucional=f"estudiante2.{unique_suffix}@acadify.edu",
        nombres="María",
        apellidos="López",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"200{unique_suffix[:7]}",
        rol=RolUsuario.estudiante,
        password_hash=password_service.hash_password("Estudiante123!"),
        email_verified=True,
    )
    
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    
    return usuario


@pytest.fixture
def estudiante_3(db_session: Session, password_service: PasswordService) -> Usuario:
    """Tercer estudiante para tests de ranking."""
    unique_suffix = str(uuid4())[:8]
    usuario = Usuario(
        usuario_id=uuid4(),
        correo_institucional=f"estudiante3.{unique_suffix}@acadify.edu",
        nombres="Pedro",
        apellidos="García",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"300{unique_suffix[:7]}",
        rol=RolUsuario.estudiante,
        password_hash=password_service.hash_password("Estudiante123!"),
        email_verified=True,
    )
    
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    
    return usuario


@pytest.fixture
def coordinador(db_session: Session, password_service: PasswordService) -> Usuario:
    """Coordinador que otorga insignias."""
    unique_suffix = str(uuid4())[:8]
    usuario = Usuario(
        usuario_id=uuid4(),
        correo_institucional=f"coordinador.{unique_suffix}@acadify.edu",
        nombres="Ana",
        apellidos="Coordinadora",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"400{unique_suffix[:7]}",
        rol=RolUsuario.coordinador,
        password_hash=password_service.hash_password("Coord123!"),
        email_verified=True,
    )
    
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    
    return usuario


# ==================== FIXTURES DE PUNTOS ====================


@pytest.fixture
def usuario_con_puntos(db_session: Session, estudiante_1: Usuario) -> UsuarioPuntos:
    """Usuario con puntos iniciales."""
    usuario_puntos = UsuarioPuntos(
        usuario_id=estudiante_1.usuario_id,
        puntos_acumulados=100,
        cambio=100,
        motivo="Puntos iniciales de prueba",
    )
    
    db_session.add(usuario_puntos)
    db_session.commit()
    db_session.refresh(usuario_puntos)
    
    return usuario_puntos


@pytest.fixture
def historial_puntos_inicial(
    db_session: Session, estudiante_1: Usuario
) -> HistorialPuntos:
    """Entrada inicial en historial de puntos."""
    historial = HistorialPuntos(
        historial_id=uuid4(),
        usuario_id=estudiante_1.usuario_id,
        cambio=100,
        motivo="Puntos iniciales de prueba",
    )
    
    db_session.add(historial)
    db_session.commit()
    db_session.refresh(historial)
    
    return historial


# ==================== FIXTURES DE RECOMPENSAS ====================


@pytest.fixture
def recompensa_basica(db_session: Session) -> Recompensa:
    """Recompensa básica de bajo costo."""
    recompensa = Recompensa(
        recompensa_id=uuid4(),
        nombre="Avatar Especial",
        descripcion="Desbloquea un avatar único",
        costo_puntos=50,
        tipo=TipoRecompensa.avatar,
    )
    
    db_session.add(recompensa)
    db_session.commit()
    db_session.refresh(recompensa)
    
    return recompensa


@pytest.fixture
def recompensa_premium(db_session: Session) -> Recompensa:
    """Recompensa premium de alto costo."""
    recompensa = Recompensa(
        recompensa_id=uuid4(),
        nombre="Tema Premium",
        descripcion="Tema visual exclusivo para la plataforma",
        costo_puntos=200,
        tipo=TipoRecompensa.tema,
    )
    
    db_session.add(recompensa)
    db_session.commit()
    db_session.refresh(recompensa)
    
    return recompensa


@pytest.fixture
def recompensa_basica(db_session: Session) -> Recompensa:
    """Recompensa básica de bajo costo."""
    recompensa = Recompensa(
        recompensa_id=uuid4(),
        nombre="Foto de Perfil Especial",
        descripcion="Desbloquea una foto de perfil única",
        costo_puntos=50,
        tipo=TipoRecompensa.foto_perfil,
    )
    
    db_session.add(recompensa)
    db_session.commit()
    db_session.refresh(recompensa)
    
    return recompensa


@pytest.fixture
def recompensa_premium(db_session: Session) -> Recompensa:
    """Recompensa premium de alto costo."""
    recompensa = Recompensa(
        recompensa_id=uuid4(),
        nombre="Estilo de Chat Premium",
        descripcion="Estilo visual exclusivo para el chat",
        costo_puntos=200,
        tipo=TipoRecompensa.estilo_chat,
    )
    
    db_session.add(recompensa)
    db_session.commit()
    db_session.refresh(recompensa)
    
    return recompensa


@pytest.fixture
def recompensa_titulo(db_session: Session) -> Recompensa:
    """Recompensa de sticker especial."""
    recompensa = Recompensa(
        recompensa_id=uuid4(),
        nombre="Sticker Dorado",
        descripcion="Sticker exclusivo para usar en comentarios",
        costo_puntos=150,
        tipo=TipoRecompensa.sticker,
    )
    
    db_session.add(recompensa)
    db_session.commit()
    db_session.refresh(recompensa)
    
    return recompensa


# ==================== FIXTURES DE INSIGNIAS ====================


@pytest.fixture
def insignia_primera_tarea(db_session: Session) -> Insignia:
    """Insignia por completar primera tarea."""
    insignia = Insignia(
        insignia_id=uuid4(),
        nombre="Primera Tarea",
        descripcion="Completaste tu primera tarea",
        imagen_url="/static/badges/first-task.png",
        tipo=TipoInsignia.automatico,
        es_unica=False,
    )
    
    db_session.add(insignia)
    db_session.commit()
    db_session.refresh(insignia)
    
    return insignia


@pytest.fixture
def insignia_racha_7_dias(db_session: Session) -> Insignia:
    """Insignia por racha de 7 días."""
    insignia = Insignia(
        insignia_id=uuid4(),
        nombre="Racha de 7 Días",
        descripcion="Ingresaste 7 días consecutivos",
        imagen_url="/static/badges/7-day-streak.png",
        tipo=TipoInsignia.automatico,
        es_unica=False,
    )
    
    db_session.add(insignia)
    db_session.commit()
    db_session.refresh(insignia)
    
    return insignia


@pytest.fixture
def insignia_excelencia(db_session: Session) -> Insignia:
    """Insignia única de excelencia."""
    insignia = Insignia(
        insignia_id=uuid4(),
        nombre="Excelencia Académica",
        descripcion="Insignia especial otorgada por el coordinador",
        imagen_url="/static/badges/excellence.png",
        tipo=TipoInsignia.manual,
        es_unica=True,
    )
    
    db_session.add(insignia)
    db_session.commit()
    db_session.refresh(insignia)
    
    return insignia


# ==================== FIXTURES DE AVATARES ====================


@pytest.fixture
def avatar_basico(db_session: Session, estudiante_1: Usuario) -> UserAvatar:
    """Avatar básico del estudiante."""
    avatar = UserAvatar(
        id=uuid4(),
        user_id=estudiante_1.usuario_id,
        name="Avatar Inicial",
        base_gender="male",
        layers=[{"category": "hair", "file": "hair/short_black.png"}],
        layers_hash="hash_basico",
        image_url="/static/avatars/avatar_basico.png",
        is_active=True,
        is_public=False,
    )
    
    db_session.add(avatar)
    db_session.commit()
    db_session.refresh(avatar)
    
    return avatar


@pytest.fixture
def avatar_premium(db_session: Session, estudiante_1: Usuario) -> UserAvatar:
    """Avatar premium bloqueado."""
    avatar = UserAvatar(
        id=uuid4(),
        user_id=estudiante_1.usuario_id,
        name="Avatar Premium",
        base_gender="male",
        layers=[
            {"category": "hair", "file": "hair/premium_style.png"},
            {"category": "clothes", "file": "clothes/premium_suit.png"}
        ],
        layers_hash="hash_premium",
        image_url="/static/avatars/avatar_premium.png",
        is_active=False,
        is_public=False,
    )
    
    db_session.add(avatar)
    db_session.commit()
    db_session.refresh(avatar)
    
    return avatar


@pytest.fixture
def avatar_premium(db_session: Session, estudiante_1: Usuario) -> UserAvatar:
    """Avatar premium bloqueado."""
    avatar = UserAvatar(
        id=uuid4(),
        user_id=estudiante_1.usuario_id,
        name="Avatar Premium",
        base_gender="male",
        layers={"head": "head_premium", "body": "body_premium"},
        layers_hash="hash_premium",
        image_url="/static/avatars/avatar_premium.png",
        is_active=False,
        is_public=False,
    )
    
    db_session.add(avatar)
    db_session.commit()
    db_session.refresh(avatar)
    
    return avatar
