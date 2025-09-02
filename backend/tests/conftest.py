# backend/tests/conftest.py
"""
Configuración global para tests de pytest
Define fixtures reutilizables y configuración de base de datos de prueba
"""
import pytest
import asyncio
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from backend.app.database import get_database_session
from app.core.config import settings
from app.models.base import Base
from app.models.user import User, UserRole, DocumentType, AccountStatus
from app.models.institution import Institution, InstitutionType, EducationalLevel, InstitutionSector
from app.crud.user import user_crud
from app.crud.institution import institution_crud
from app.core.security import get_password_hash

# Base de datos en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Crea un event loop para toda la sesión de tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Fixture que proporciona una sesión de base de datos limpia para cada test
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Limpiar todas las tablas después del test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Fixture que proporciona un cliente de test de FastAPI
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_database_session] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Datos de usuario de prueba"""
    return {
        "institutional_email": "test@university.edu.co",
        "first_names": "Juan Carlos",
        "last_names": "Pérez García",
        "document_type": DocumentType.CC,
        "document_number": "12345678",
        "role": UserRole.STUDENT,
        "password": "TestPassword123!",
        "phone": "+573001234567",
        "biography": "Estudiante de ingeniería de sistemas"
    }

@pytest.fixture
def test_admin_data() -> Dict[str, Any]:
    """Datos de administrador de prueba"""
    return {
        "institutional_email": "admin@university.edu.co",
        "first_names": "María Elena",
        "last_names": "Rodríguez López",
        "document_type": DocumentType.CC,
        "document_number": "87654321",
        "role": UserRole.ADMINISTRATOR,
        "password": "AdminPassword123!",
        "phone": "+573009876543"
    }

@pytest.fixture
def test_teacher_data() -> Dict[str, Any]:
    """Datos de docente de prueba"""
    return {
        "institutional_email": "teacher@university.edu.co",
        "first_names": "Carlos Alberto",
        "last_names": "González Martínez",
        "document_type": DocumentType.CC,
        "document_number": "11223344",
        "role": UserRole.TEACHER,
        "password": "TeacherPassword123!",
        "phone": "+573005551234"
    }

@pytest.fixture
def test_institution_data() -> Dict[str, Any]:
    """Datos de institución de prueba"""
    return {
        "name": "Universidad Tecnológica de Prueba",
        "acronym": "UTP",
        "motto": "Ciencia, Tecnología e Innovación",
        "institution_type": InstitutionType.UNIVERSITY,
        "uses_programs": True,
        "educational_level": EducationalLevel.HIGHER,
        "sector": InstitutionSector.PUBLIC,
        "address": "Calle 123 #45-67",
        "city": "Bogotá",
        "country": "Colombia",
        "institutional_email": "info@utp.edu.co",
        "phone": "+571234567890",
        "tax_id": "900123456-7"
    }

@pytest.fixture
def created_user(db: Session, test_user_data: Dict[str, Any]) -> User:
    """Crea un usuario de prueba en la base de datos"""
    from app.schemas.user import UserCreate
    
    user_create = UserCreate(**test_user_data)
    return user_crud.create(db, obj_in=user_create)

@pytest.fixture
def created_admin(db: Session, test_admin_data: Dict[str, Any]) -> User:
    """Crea un administrador de prueba en la base de datos"""
    from app.schemas.user import UserCreate
    
    admin_create = UserCreate(**test_admin_data)
    return user_crud.create(db, obj_in=admin_create)

@pytest.fixture
def created_teacher(db: Session, test_teacher_data: Dict[str, Any]) -> User:
    """Crea un docente de prueba en la base de datos"""
    from app.schemas.user import UserCreate
    
    teacher_create = UserCreate(**test_teacher_data)
    return user_crud.create(db, obj_in=teacher_create)

@pytest.fixture
def created_institution(db: Session, test_institution_data: Dict[str, Any], created_admin: User) -> Institution:
    """Crea una institución de prueba en la base de datos"""
    from app.schemas.institution import InstitutionCreate
    
    institution_data = test_institution_data.copy()
    institution_data["administrator_id"] = str(created_admin.id)
    institution_create = InstitutionCreate(**institution_data)
    return institution_crud.create(db, obj_in=institution_create)

@pytest.fixture
def auth_headers(client: TestClient, created_user: User) -> Dict[str, str]:
    """
    Crea headers de autenticación para requests de prueba
    """
    login_data = {
        "username": created_user.institutional_email,
        "password": "TestPassword123!"
    }
    
    response = client.post("/api/v1/auth/login/oauth", data=login_data)
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['token']['access_token']}"}

@pytest.fixture
def admin_auth_headers(client: TestClient, created_admin: User) -> Dict[str, str]:
    """
    Crea headers de autenticación de administrador para requests de prueba
    """
    login_data = {
        "username": created_admin.institutional_email,
        "password": "AdminPassword123!"
    }
    
    response = client.post("/api/v1/auth/login/oauth", data=login_data)
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['token']['access_token']}"}