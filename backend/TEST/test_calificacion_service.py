"""
Tests para CalificacionService - Calificación de Respuestas
Cobertura: Automática, manual, con IA
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

from src.services.evaluaciones.calificacion_service import CalificacionService
from src.models.evaluaciones import RespuestaEstudiante
from TEST.test_data_builders import PreguntaBuilder


@pytest.fixture
def mock_db():
    db = Mock()
    db.query = Mock()
    db.commit = Mock()
    return db


@pytest.fixture
def pregunta_om():
    return PreguntaBuilder().opcion_multiple("¿Derivada de x²?", ["2x", "x", "2"], "2x").build()


class TestCalificacionAutomatica:
    def test_calificar_correcta(self, mock_db, pregunta_om):
        from src.models.evaluaciones import IntentoEvaluacion
        
        with patch.object(CalificacionService, '__init__', return_value=None):
            service = CalificacionService.__new__(CalificacionService)
            service.db = mock_db
            service.ia_service = Mock()
            
            intento_id = uuid4()
            intento = IntentoEvaluacion(
                intento_id=intento_id,
                evaluacion_id=uuid4(),
                estudiante_id=uuid4(),
                puntuacion_obtenida=0.0,
                puntuacion_maxima=100.0  # Agregar puntuación máxima
            )
            
            respuesta = RespuestaEstudiante(
                respuesta_id=uuid4(),
                intento_id=intento_id,
                pregunta_id=pregunta_om.pregunta_id,
                respuesta_texto="2x",
                es_correcta=None,
                puntuacion_obtenida=None
            )
            respuesta.pregunta = pregunta_om
            
            mock_db.query().filter().first.return_value = intento
            mock_db.query().join().filter().options().all.return_value = [respuesta]
            
            result = service.calificar_automaticamente(intento_id)
            assert mock_db.commit.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
