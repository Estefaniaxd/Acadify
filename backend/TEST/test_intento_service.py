"""
Tests para IntentoService - Gestión de Intentos
Cobertura: Iniciar, responder, pausar, finalizar
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from fastapi import HTTPException

from src.services.evaluaciones.intento_service import IntentoService
from src.models.evaluaciones import IntentoEvaluacion, RespuestaEstudiante, EstadoIntento
from src.schemas.evaluaciones.evaluacion_schemas import IniciarIntentoRequest, ResponderPreguntaRequest
from TEST.test_data_builders import EvaluacionBuilder, PreguntaBuilder, IntentoBuilder


@pytest.fixture
def mock_db():
    db = Mock()
    db.query = Mock()
    db.commit = Mock()
    db.add = Mock()
    return db


@pytest.fixture
def evaluacion():
    ev = EvaluacionBuilder().publicada().build()
    ev.num_preguntas_mostrar = None
    return ev


@pytest.fixture
def pregunta():
    return PreguntaBuilder().opcion_multiple("¿Derivada de x³?", ["3x²", "x²"], "3x²").build()


class TestIniciar:
    def test_iniciar_exitoso(self, mock_db, evaluacion, pregunta):
        request = IniciarIntentoRequest(
            evaluacion_id=evaluacion.evaluacion_id,
            codigo_acceso=evaluacion.codigo_acceso
        )
        # Agregar atributos que el servicio espera
        request.ip_address = "127.0.0.1"
        request.user_agent = "Test Agent"
        
        with patch.object(IntentoService, '__init__', return_value=None):
            service = IntentoService.__new__(IntentoService)
            service.db = mock_db
            service.evaluacion_service = Mock()
            service.ia_service = Mock()
            service.multimedia_service = Mock()
            
            service.evaluacion_service.obtener_evaluacion.return_value = evaluacion
            service.evaluacion_service.validar_acceso_estudiante.return_value = (True, "OK")
            pregunta.orden = 1
            mock_db.query().filter().order_by().all.return_value = [pregunta]
            mock_db.query().filter().order_by().limit().all.return_value = []
            
            intento = service.iniciar_intento(request, uuid4())
            assert mock_db.add.called


class TestResponder:
    def test_responder_correcta(self, mock_db, evaluacion, pregunta):
        estudiante_id = uuid4()
        intento = IntentoBuilder().en_progreso().build()
        intento.estudiante_id = estudiante_id
        intento.evaluacion_id = evaluacion.evaluacion_id
        intento.preguntas_respondidas = 0  # Inicializar
        intento.puntuacion_obtenida = 0.0  # Inicializar
        intento.pregunta_actual = 1  # Inicializar
        
        # Asegurarse que pregunta pertenece a la evaluación
        pregunta.evaluacion_id = evaluacion.evaluacion_id
        
        request = ResponderPreguntaRequest(
            intento_id=intento.intento_id,
            pregunta_id=pregunta.pregunta_id,
            respuesta="3x²",
            tiempo_respuesta_segundos=30
        )
        
        with patch.object(IntentoService, '__init__', return_value=None):
            service = IntentoService.__new__(IntentoService)
            service.db = mock_db
            service.evaluacion_service = Mock()
            service.ia_service = Mock()
            service.multimedia_service = Mock()
            
            mock_db.query().filter().first.side_effect = [intento, pregunta, None]
            service.evaluacion_service.obtener_evaluacion.return_value = evaluacion
            
            respuesta = service.responder_pregunta(request, estudiante_id)
            assert mock_db.add.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
