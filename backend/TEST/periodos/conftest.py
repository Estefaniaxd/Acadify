"""
Fixtures compartidos para tests de Períodos Académicos
"""
import pytest
import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from src.models.academic.periodo_academico import PeriodoAcademico
from src.enums.academic import TipoPeriodo, EstadoPeriodo


@pytest.fixture
def institucion_id():
    """Retorna un UUID fijo para institución (sin crear el objeto)"""
    return uuid4()


@pytest.fixture
def usuario_coordinador_id():
    """Retorna un UUID fijo para usuario coordinador (sin crear el objeto)"""
    return uuid4()


def _codigo_unico():
    """Genera un código único"""
    return f"TEST-{random.randint(10000, 99999)}"


@pytest.fixture
def periodo_base_data(institucion_id):
    """Datos base para crear un período"""
    hoy = date.today()
    return {
        "institucion_id": institucion_id,
        "nombre": "Semestre 2024-1",
        "codigo": _codigo_unico(),  # Código único
        "descripcion": "Primer semestre académico de 2024",
        "tipo": TipoPeriodo.semestral,
        "estado": EstadoPeriodo.programado,
        "anio": 2024,
        "numero_periodo": 1,
        
        # Fechas principales
        "fecha_inicio": hoy + timedelta(days=30),
        "fecha_fin": hoy + timedelta(days=180),
        
        # Inscripciones
        "fecha_inicio_inscripciones": hoy + timedelta(days=10),
        "fecha_fin_inscripciones": hoy + timedelta(days=25),
        
        # Clases
        "fecha_inicio_clases": hoy + timedelta(days=30),
        "fecha_fin_clases": hoy + timedelta(days=170),
        
        # Configuración
        "permite_inscripciones": True,
        "permite_ajustes": True,
        "permite_retiros": True,
        "visible_estudiantes": True,
        "visible_profesores": True,
        
        # Límites
        "creditos_minimos": 12,
        "creditos_maximos": 20,
        "cursos_minimos": 4,
        "cursos_maximos": 6,
        
        # Costos
        "costo_matricula": Decimal("500000.00"),
        "costo_por_credito": Decimal("150000.00"),
        "moneda": "COP",
        
        "activo": True,
        "es_actual": False
    }


@pytest.fixture
def periodo_base(db_session, periodo_base_data):
    """Crea un período académico base"""
    periodo = PeriodoAcademico(**periodo_base_data)
    db_session.add(periodo)
    db_session.commit()
    db_session.refresh(periodo)
    return periodo


@pytest.fixture
def periodo_en_inscripciones(db_session, institucion_id):
    """Crea un período con inscripciones abiertas"""
    hoy = date.today()
    periodo = PeriodoAcademico(
        institucion_id=institucion_id,
        nombre="Semestre 2024-2",
        codigo=_codigo_unico(),  # Código único
        tipo=TipoPeriodo.semestral,
        estado=EstadoPeriodo.inscripciones_abiertas,
        anio=2024,
        numero_periodo=2,
        
        fecha_inicio=hoy - timedelta(days=10),
        fecha_fin=hoy + timedelta(days=150),
        
        fecha_inicio_inscripciones=hoy - timedelta(days=5),
        fecha_fin_inscripciones=hoy + timedelta(days=10),
        
        fecha_inicio_clases=hoy + timedelta(days=15),
        fecha_fin_clases=hoy + timedelta(days=145),
        
        permite_inscripciones=True,
        activo=True,
        es_actual=True
    )
    db_session.add(periodo)
    db_session.commit()
    db_session.refresh(periodo)
    return periodo


@pytest.fixture
def periodo_en_curso(db_session, institucion_id):
    """Crea un período en curso"""
    hoy = date.today()
    periodo = PeriodoAcademico(
        institucion_id=institucion_id,
        nombre="Trimestre Q1-2024",
        codigo=_codigo_unico(),  # Código único
        tipo=TipoPeriodo.trimestral,
        estado=EstadoPeriodo.en_curso,
        anio=2024,
        numero_periodo=1,
        
        fecha_inicio=hoy - timedelta(days=30),
        fecha_fin=hoy + timedelta(days=60),
        
        fecha_inicio_inscripciones=hoy - timedelta(days=50),
        fecha_fin_inscripciones=hoy - timedelta(days=35),
        
        fecha_inicio_clases=hoy - timedelta(days=30),
        fecha_fin_clases=hoy + timedelta(days=55),
        
        permite_inscripciones=False,
        activo=True,
        es_actual=True
    )
    db_session.add(periodo)
    db_session.commit()
    db_session.refresh(periodo)
    return periodo


@pytest.fixture
def periodo_finalizado(db_session, institucion_id):
    """Crea un período finalizado"""
    hoy = date.today()
    periodo = PeriodoAcademico(
        institucion_id=institucion_id,
        nombre="Semestre 2023-2",
        codigo=_codigo_unico(),  # Código único
        tipo=TipoPeriodo.semestral,
        estado=EstadoPeriodo.finalizado,
        anio=2023,
        numero_periodo=2,
        
        fecha_inicio=hoy - timedelta(days=200),
        fecha_fin=hoy - timedelta(days=20),
        
        fecha_inicio_inscripciones=hoy - timedelta(days=220),
        fecha_fin_inscripciones=hoy - timedelta(days=205),
        
        fecha_inicio_clases=hoy - timedelta(days=200),
        fecha_fin_clases=hoy - timedelta(days=25),
        
        permite_inscripciones=False,
        activo=True,
        es_actual=False
    )
    db_session.add(periodo)
    db_session.commit()
    db_session.refresh(periodo)
    return periodo
