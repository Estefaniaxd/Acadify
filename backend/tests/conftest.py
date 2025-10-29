"""
Pytest configuration and shared fixtures
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = Mock(spec=Session)
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    db.rollback = Mock()
    db.execute = Mock()
    return db


@pytest.fixture
def sample_uuid():
    """Generate a sample UUID"""
    return uuid4()


@pytest.fixture
def sample_curso_data():
    """Sample curso data for testing"""
    return {
        "curso_id": uuid4(),
        "nombre": "Matemáticas Avanzadas",
        "descripcion": "Curso de matemáticas nivel avanzado",
        "institucion_id": uuid4(),
        "programa_id": uuid4(),
        "modalidad": "presencial",
        "fecha_inicio": datetime.now(),
        "fecha_fin": None
    }


@pytest.fixture
def sample_usuario_data():
    """Sample usuario data for testing"""
    return {
        "usuario_id": uuid4(),
        "nombres": "Juan",
        "apellidos": "Pérez",
        "correo_institucional": "juan.perez@example.com",
        "rol": "estudiante",
        "estado_cuenta": "activo"
    }


@pytest.fixture
def sample_comentario_data():
    """Sample comentario data for testing"""
    return {
        "comentario_id": uuid4(),
        "curso_id": uuid4(),
        "autor_id": uuid4(),
        "contenido": "Este es un comentario de prueba",
        "tipo": "general",
        "comentario_padre_id": None,
        "activo": True,
        "fecha_creacion": datetime.now()
    }


@pytest.fixture
def sample_tarea_data():
    """Sample tarea data for testing"""
    return {
        "tarea_id": uuid4(),
        "titulo": "Tarea de prueba",
        "descripcion": "Descripción de la tarea",
        "clase_id": uuid4(),
        "docente_id": uuid4(),
        "fecha_asignacion": datetime.now(),
        "fecha_limite": datetime.now(),
        "permite_entregas_tardias": True
    }
