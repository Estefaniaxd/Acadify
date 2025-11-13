"""
Tests para EvaluacionService - Sistema de Evaluaciones
Cobertura: CRUD, validaciones, estadísticas
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import HTTPException

from src.services.evaluaciones.evaluacion_service import EvaluacionService
from src.models.evaluaciones.evaluacion_expandida import Evaluacion, EstadoEvaluacion, TipoEvaluacion
from src.schemas.evaluaciones.evaluacion_schemas import EvaluacionCreate, EvaluacionUpdate
from TEST.test_data_builders import EvaluacionBuilder, CursoBuilder


@pytest.fixture
def mock_db():
    db = Mock()
    db.query = Mock()
    db.commit = Mock()
    db.add = Mock()
    db.delete = Mock()
    return db


@pytest.fixture
def service(mock_db):
    return EvaluacionService(db=mock_db)


@pytest.fixture
def curso():
    return CursoBuilder().con_nombre("Matematicas").build()


class TestCrear:
    def test_crear_exitoso(self, service, mock_db, curso):
        schema = EvaluacionCreate(
            titulo="Quiz 1",
            curso_id=curso.curso_id,
            tipo_evaluacion=TipoEvaluacion.QUIZ,
            puntuacion_total=50.0,
            total_preguntas=5,  # Schema lo requiere
            tiempo_limite_minutos=30
        )
        mock_db.query().filter().first.return_value = curso
        usuario_id = uuid4()
        service.crear_evaluacion(schema, usuario_id)
        assert mock_db.add.called


class TestObtener:
    def test_obtener_existente(self, service, mock_db):
        ev = EvaluacionBuilder().build()
        mock_db.query().filter().first.return_value = ev
        result = service.obtener_evaluacion(ev.evaluacion_id)
        assert result.evaluacion_id == ev.evaluacion_id


class TestListar:
    def test_listar_evaluaciones(self, service, mock_db):
        evaluaciones = [
            EvaluacionBuilder().build(),
            EvaluacionBuilder().build()
        ]
        
        # Mock completo para toda la cadena de query
        mock_query = Mock()
        
        # Configurar filter() para retornar self (comportamiento real)
        mock_query.filter.return_value = mock_query
        
        # Configurar order_by() para retornar self
        mock_query.order_by.return_value = mock_query
        
        # Configurar count() para retornar número
        mock_query.count.return_value = 2
        
        # Configurar la cadena offset().limit().all()
        mock_limit = Mock()
        mock_limit.all.return_value = evaluaciones
        
        mock_offset = Mock()
        mock_offset.limit.return_value = mock_limit
        
        mock_query.offset.return_value = mock_offset
        
        # Conectar el query inicial
        mock_db.query.return_value = mock_query
        
        # Pasa parámetros que no active filtros complejos
        from src.schemas.evaluaciones.evaluacion_schemas import EvaluacionFiltros
        filtros = EvaluacionFiltros()
        resultado = service.listar_evaluaciones(filtros)
        
        assert len(resultado[0]) == 2
        assert resultado[1] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
