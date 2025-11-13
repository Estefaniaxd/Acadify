"""
Fixtures compartidas para tests de gamificación.

Provee:
- Cliente HTTP de prueba
- Base de datos de prueba
- Usuarios de prueba (admin, coordinador, estudiante)
- Tokens JWT de autenticación
- Datos de prueba (puntos, etiquetas, items, rachas)

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
Version: 1.0.0
"""

import pytest
import asyncio
from typing import AsyncGenerator
from datetime import datetime, timedelta, date
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from faker import Faker

from src.main import app
from src.api.deps import get_db
from src.db.base_class import Base
from src.models.users.usuario import Usuario
from src.models.gamification import (
    UsuarioPuntos, HistorialPuntos, Insignia, UsuarioInsignia,
    EtiquetaPerfil, UsuarioEtiqueta,
    TiendaItem, TransaccionTienda, InventarioUsuario,
    RachaUsuario, HistorialRacha, RecompensaRacha
)
from src.services.auth.token_service import TokenService
from src.services.auth.redis_service import RedisService
from src.services.auth.password_service import PasswordService
from src.enums.users.usuario_enums import RolUsuario, EstadoCuentaUsuario, TipoDocumentoUsuario
from src.enums.gamification import (
    CategoriaEtiqueta, RarezaEtiqueta,
    CategoriaItem, RarezaItem
)

fake = Faker('es_ES')


# =============================================================================
# GLOBAL MOCKS (se aplican a todos los tests)
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def mock_redis_globally():
    """Mock global de Redis para todos los tests."""
    from unittest.mock import MagicMock, AsyncMock
    import src.api.dependencies as deps_module
    
    # Crear mock de cliente Redis
    mock_redis_client = MagicMock()
    mock_redis_client.exists = MagicMock(return_value=False)
    mock_redis_client.get = MagicMock(return_value=None)
    mock_redis_client.set = MagicMock(return_value=True)
    mock_redis_client.delete = MagicMock(return_value=True)
    mock_redis_client.expire = MagicMock(return_value=True)
    
    # Patchear el redis_service que ya está instanciado en dependencies
    deps_module.redis_service.redis = mock_redis_client
    deps_module.redis_service.is_token_blacklisted = AsyncMock(return_value=False)
    deps_module.redis_service.blacklist_token = AsyncMock(return_value=True)
    deps_module.redis_service.check_rate_limit = AsyncMock(return_value=(True, 100, None))
    
    # También patchear el token_service para que use el mock
    deps_module.token_service.redis_service.redis = mock_redis_client
    deps_module.token_service.redis_service.is_token_blacklisted = AsyncMock(return_value=False)
    deps_module.token_service.redis_service.blacklist_token = AsyncMock(return_value=True)
    
    yield mock_redis_client


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

@pytest.fixture(scope="function")
async def db_engine():
    """Motor de base de datos async en memoria para tests."""
    from sqlalchemy import event
    
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Registrar listener para generar UUIDs y defaults automáticamente antes de INSERT
    @event.listens_for(Usuario, "before_insert", propagate=True)
    def _generate_usuario_defaults(mapper, connection, target):
        """Genera UUID y defaults para Usuario."""
        if target.usuario_id is None:
            target.usuario_id = uuid4()
        if target.failed_login_attempts is None:
            target.failed_login_attempts = 0
        if target.twofa_enabled is None:
            target.twofa_enabled = False
        if target.fecha_creacion is None:
            target.fecha_creacion = datetime.now()
        if target.ultimo_acceso is None:
            target.ultimo_acceso = datetime.now()
        # Agregar tipo_documento por defecto si no existe
        if target.tipo_documento is None:
            target.tipo_documento = TipoDocumentoUsuario.cc
        if target.numero_documento is None:
            target.numero_documento = "1234567890"
    
    # Listener para UsuarioPuntos
    @event.listens_for(UsuarioPuntos, "before_insert", propagate=True)
    def _generate_usuario_puntos_defaults(mapper, connection, target):
        """Genera defaults para UsuarioPuntos."""
        if target.fecha is None:
            target.fecha = datetime.now()
    
    # Listener para HistorialPuntos
    @event.listens_for(HistorialPuntos, "before_insert", propagate=True)
    def _generate_historial_puntos_defaults(mapper, connection, target):
        """Genera UUID y defaults para HistorialPuntos."""
        if target.historial_id is None:
            target.historial_id = uuid4()
        if target.fecha is None:
            target.fecha = datetime.now()
    
    # Similar para otras tablas con UUID
    for model in [Insignia, EtiquetaPerfil, 
                  UsuarioEtiqueta, TiendaItem, TransaccionTienda, InventarioUsuario,
                  RachaUsuario, HistorialRacha, RecompensaRacha]:
        @event.listens_for(model, "before_insert", propagate=True)
        def _generate_model_uuid(mapper, connection, target, model=model):
            """Genera UUIDs para campos _id del modelo."""
            for col in mapper.columns:
                if col.name.endswith('_id') and col.primary_key:
                    if getattr(target, col.name) is None:
                        setattr(target, col.name, uuid4())
                # Agregar fecha si existe y está vacía
                if col.name == 'fecha' and getattr(target, col.name) is None:
                    setattr(target, col.name, datetime.now())
    
    # Crear solo las tablas necesarias para gamificación
    tables_to_create = [
        'Usuario',
        'UsuarioPuntos',
        'HistorialPuntos',
        'Insignia',
        'UsuarioInsignia',
        'EtiquetaPerfil',
        'UsuarioEtiqueta',
        'TiendaItem',
        'TransaccionTienda',
        'InventarioUsuario',
        'RachaUsuario',
        'HistorialRacha',
        'RecompensaRacha'
    ]
    
    # Crear tablas específicas
    async with engine.begin() as conn:
        tables = [Base.metadata.tables[name] for name in tables_to_create if name in Base.metadata.tables]
        # Remover server_defaults de PostgreSQL que no funcionan en SQLite
        for table in tables:
            for column in table.columns:
                if column.server_default is not None:
                    column.server_default = None
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, tables=tables))
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(sync_conn, tables=tables))
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Sesión async de base de datos para tests."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture(scope="function")
async def client(db_session, redis_service) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP async de prueba con base de datos y Redis mockeados."""
    from src.api.dependencies import get_redis_service
    
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    async def override_get_redis():
        return redis_service
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis_service] = override_get_redis
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# =============================================================================
# USUARIO FIXTURES
# =============================================================================

@pytest.fixture
def password_service():
    """Servicio de passwords."""
    return PasswordService()


@pytest.fixture
async def admin_user(db_session, password_service) -> Usuario:
    """Usuario administrador de prueba."""
    admin = Usuario(
        correo_institucional="admin@test.com",
        username="admin_test",
        nombres="Admin",
        apellidos="Test",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento="1234567890",
        rol=RolUsuario.administrador,
        password_hash=password_service.hash_password("admin123"),
        estado_cuenta=EstadoCuentaUsuario.activo,
        email_verified=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
async def coordinador_user(db_session, password_service) -> Usuario:
    """Usuario coordinador de prueba."""
    coord = Usuario(
        correo_institucional="coord@test.com",
        username="coord_test",
        nombres="Coordinador",
        apellidos="Test",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento="1234567891",
        rol=RolUsuario.coordinador,
        password_hash=password_service.hash_password("coord123"),
        estado_cuenta=EstadoCuentaUsuario.activo,
        email_verified=True
    )
    db_session.add(coord)
    await db_session.commit()
    await db_session.refresh(coord)
    return coord


@pytest.fixture
async def estudiante_user(db_session, password_service) -> Usuario:
    """Usuario estudiante de prueba."""
    estudiante = Usuario(
        correo_institucional="estudiante@test.com",
        username="estudiante_test",
        nombres="Estudiante",
        apellidos="Test",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento="1234567892",
        rol=RolUsuario.estudiante,
        password_hash=password_service.hash_password("estudiante123"),
        estado_cuenta=EstadoCuentaUsuario.activo,
        email_verified=True
    )
    db_session.add(estudiante)
    await db_session.commit()
    await db_session.refresh(estudiante)
    return estudiante


@pytest.fixture
async def multiple_users(db_session, password_service) -> list[Usuario]:
    """Lista de múltiples usuarios para tests de ranking."""
    users = []
    for i in range(10):
        user = Usuario(
            correo_institucional=f"user{i}@test.com",
            nombres=f"User{i}",
            apellidos="Test",
            rol=RolUsuario.estudiante,
            estado_cuenta=EstadoCuentaUsuario.activo,
            email_verified=True,
            password_hash=password_service.hash_password(f"pass{i}")
        )
        db_session.add(user)
        users.append(user)
    
    await db_session.commit()
    for user in users:
        await db_session.refresh(user)
    
    return users


# =============================================================================
# TOKEN FIXTURES
# =============================================================================

@pytest.fixture
def redis_service():
    """Servicio Redis mockeado para tests."""
    from unittest.mock import MagicMock, AsyncMock
    
    # Crear instancia real de RedisService
    service = RedisService()
    
    # Mockear el cliente redis interno
    service.redis = MagicMock()
    service.redis.exists = MagicMock(return_value=False)
    service.redis.get = MagicMock(return_value=None)
    service.redis.set = MagicMock(return_value=True)
    service.redis.delete = MagicMock(return_value=True)
    service.redis.expire = MagicMock(return_value=True)
    
    # Patchear métodos async del servicio
    service.is_token_blacklisted = AsyncMock(return_value=False)
    service.blacklist_token = AsyncMock(return_value=True)
    service.check_rate_limit = AsyncMock(return_value=(True, 100, None))
    
    return service


@pytest.fixture
def token_service(redis_service):
    """Servicio de tokens."""
    return TokenService(redis_service)


@pytest.fixture
def admin_token(admin_user, token_service) -> str:
    """Token JWT para usuario administrador."""
    access_token, _ = token_service.create_access_token(
        user_id=str(admin_user.usuario_id),
        roles=[str(admin_user.rol)]
    )
    return access_token


@pytest.fixture
def estudiante_token(estudiante_user, token_service) -> str:
    """Token JWT para usuario estudiante."""
    access_token, _ = token_service.create_access_token(
        user_id=str(estudiante_user.usuario_id),
        roles=[str(estudiante_user.rol)]
    )
    return access_token


@pytest.fixture
def auth_headers(admin_token) -> dict:
    """Headers con autorización para admin."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def estudiante_headers(estudiante_token) -> dict:
    """Headers con autorización para estudiante."""
    return {"Authorization": f"Bearer {estudiante_token}"}


# =============================================================================
# PUNTOS FIXTURES
# =============================================================================

@pytest.fixture
async def usuario_puntos(db_session, estudiante_user) -> UsuarioPuntos:
    """Puntos del usuario estudiante."""
    puntos = UsuarioPuntos(
        usuario_id=estudiante_user.usuario_id,
        puntos_acumulados=1000,
        cambio=1000,
        motivo="Puntos iniciales de prueba"
    )
    db_session.add(puntos)
    await db_session.commit()
    await db_session.refresh(puntos)
    return puntos


@pytest.fixture
async def historial_puntos(db_session, estudiante_user) -> list[HistorialPuntos]:
    """Historial de puntos para tests."""
    historial = []
    for i in range(5):
        entrada = HistorialPuntos(
            historial_id=uuid4(),
            usuario_id=estudiante_user.usuario_id,
            cambio=50 * (i + 1),
            motivo=f"Test acción {i}",
            fecha=datetime.utcnow() - timedelta(days=i)
        )
        db_session.add(entrada)
        historial.append(entrada)
    
    await db_session.commit()
    for entrada in historial:
        await db_session.refresh(entrada)
    
    return historial


@pytest.fixture
async def insignia_sample(db_session) -> Insignia:
    """Insignia de prueba."""
    insignia = Insignia(
        insignia_id=uuid4(),
        nombre="Test Badge",
        motivo="Badge for testing",
        imagen_url="/assets/test_badge.png",
        tipo="logro",
        requisitos={"puntos_minimos": 1000}
    )
    db_session.add(insignia)
    await db_session.commit()
    await db_session.refresh(insignia)
    return insignia


# =============================================================================
# ETIQUETAS FIXTURES
# =============================================================================

@pytest.fixture
async def etiqueta_sample(db_session) -> EtiquetaPerfil:
    """Etiqueta de prueba."""
    etiqueta = EtiquetaPerfil(
        etiqueta_id=uuid4(),
        nombre="Python Master",
        motivo="Maestro de Python",
        categoria=CategoriaEtiqueta.PROGRAMACION,
        rareza=RarezaEtiqueta.EPICO,
        icono_url="/assets/python_master.png",
        color_hex="#3776AB",
        precio_puntos=800,
        es_comprable=True
    )
    db_session.add(etiqueta)
    await db_session.commit()
    await db_session.refresh(etiqueta)
    return etiqueta


@pytest.fixture
async def etiquetas_catalogo(db_session) -> list[EtiquetaPerfil]:
    """Catálogo de etiquetas para tests."""
    etiquetas = []
    categorias = [CategoriaEtiqueta.PROGRAMACION, CategoriaEtiqueta.MATEMATICAS, CategoriaEtiqueta.CIENCIAS]
    rarezas = [RarezaEtiqueta.COMUN, RarezaEtiqueta.RARO, RarezaEtiqueta.EPICO]
    
    for i, (cat, rar) in enumerate(zip(categorias, rarezas)):
        etiqueta = EtiquetaPerfil(
            etiqueta_id=uuid4(),
            nombre=f"Badge {i}",
            motivo=f"Test badge {i}",
            categoria=cat,
            rareza=rar,
            precio_puntos=100 * (i + 1),
            es_comprable=True
        )
        db_session.add(etiqueta)
        etiquetas.append(etiqueta)
    
    await db_session.commit()
    for etiqueta in etiquetas:
        await db_session.refresh(etiqueta)
    
    return etiquetas


@pytest.fixture
async def usuario_etiqueta(db_session, estudiante_user, etiqueta_sample) -> UsuarioEtiqueta:
    """Etiqueta en posesión del usuario."""
    ue = UsuarioEtiqueta(
        usuario_etiqueta_id=uuid4(),
        usuario_id=estudiante_user.usuario_id,
        etiqueta_id=etiqueta_sample.etiqueta_id,
        fecha_obtencion=datetime.utcnow(),
        metodo_obtencion="compra",
        esta_equipada=False,
        orden_visualizacion=0,
        veces_equipada=0
    )
    db_session.add(ue)
    await db_session.commit()
    await db_session.refresh(ue)
    return ue


# =============================================================================
# TIENDA FIXTURES
# =============================================================================

@pytest.fixture
async def item_tienda_sample(db_session) -> TiendaItem:
    """Item de tienda de muestra."""
    item = TiendaItem(
        item_id=uuid4(),
        nombre="Cabello Azul Neon",
        motivo="Peinado futurista",
        categoria=CategoriaItem.AVATAR_CABEZA,
        rareza=RarezaItem.EPICO,
        imagen_url="/assets/cabello_azul.png",
        precio_puntos=800,
        es_disponible=True,
        es_comprable=True
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item


@pytest.fixture
async def items_catalogo(db_session) -> list[TiendaItem]:
    """Catálogo de items para tests."""
    items = []
    categorias = [CategoriaItem.AVATAR_CABEZA, CategoriaItem.AVATAR_TORSO, CategoriaItem.AVATAR_PIERNAS]
    
    for i, cat in enumerate(categorias):
        item = TiendaItem(
            item_id=uuid4(),
            nombre=f"Item {i}",
            motivo=f"Test item {i}",
            categoria=cat,
            rareza=RarezaItem.COMUN,
            precio_puntos=200 * (i + 1),
            es_disponible=True,
            es_comprable=True
        )
        db_session.add(item)
        items.append(item)
    
    await db_session.commit()
    for item in items:
        await db_session.refresh(item)
    
    return items


@pytest.fixture
async def inventario_item(db_session, estudiante_user, item_tienda_sample) -> InventarioUsuario:
    """Item en inventario del usuario."""
    inv = InventarioUsuario(
        inventario_id=uuid4(),
        usuario_id=estudiante_user.usuario_id,
        item_id=item_tienda_sample.item_id,
        cantidad=1,
        fecha_adquisicion=datetime.utcnow(),
        metodo_adquisicion="compra",
        esta_equipado=False,
        veces_usado=0
    )
    db_session.add(inv)
    await db_session.commit()
    await db_session.refresh(inv)
    return inv


# =============================================================================
# RACHAS FIXTURES
# =============================================================================

@pytest.fixture
async def racha_usuario(db_session, estudiante_user) -> RachaUsuario:
    """Racha activa del usuario."""
    racha = RachaUsuario(
        usuario_id=estudiante_user.usuario_id,
        racha_actual=15,
        mejor_racha=45,
        fecha_ultimo_dia=date.today(),
        recuperaciones_disponibles=3,
        notificacion_enviada=False,
        ultima_recompensa_dia=0
    )
    db_session.add(racha)
    await db_session.commit()
    await db_session.refresh(racha)
    return racha


@pytest.fixture
async def milestones_racha(db_session) -> list[RecompensaRacha]:
    """Milestones de racha para tests."""
    milestones = [
        (3, "Primera Racha", 50),
        (7, "Primera Semana", 100),
        (30, "Racha de 30 Días", 500),
        (60, "Racha de 60 Días", 1000),
        (90, "Racha de 90 Días", 2000),
    ]
    
    recompensas = []
    for dias, nombre, puntos in milestones:
        r = RecompensaRacha(
            recompensa_id=uuid4(),
            milestone_dias=dias,
            nombre=nombre,
            motivo=f"Alcanza {dias} días de racha",
            puntos_otorgados=puntos,
            etiqueta_id=None
        )
        db_session.add(r)
        recompensas.append(r)
    
    await db_session.commit()
    for r in recompensas:
        await db_session.refresh(r)
    
    return recompensas


@pytest.fixture
async def historial_racha_data(db_session, estudiante_user, racha_usuario) -> list[HistorialRacha]:
    """Historial de eventos de racha."""
    historial = []
    for i in range(5):
        h = HistorialRacha(
            historial_id=uuid4(),
            racha_id=racha_usuario.racha_id,
            usuario_id=estudiante_user.usuario_id,
            tipo_evento="verificacion",
            dias_racha=10 + i,
            motivo=f"Verificación día {i}",
            fecha=datetime.utcnow() - timedelta(days=i)
        )
        db_session.add(h)
        historial.append(h)
    
    await db_session.commit()
    for h in historial:
        await db_session.refresh(h)
    
    return historial


# =============================================================================
# UTILITY FIXTURES
# =============================================================================

@pytest.fixture
def fake_data():
    """Generador Faker para datos aleatorios."""
    return fake


@pytest.fixture
def sample_date_range():
    """Rango de fechas para tests."""
    return {
        "start": date.today() - timedelta(days=30),
        "end": date.today(),
        "middle": date.today() - timedelta(days=15)
    }
