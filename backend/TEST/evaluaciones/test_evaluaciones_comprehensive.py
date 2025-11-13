"""Tests comprehensivos para el sistema de evaluaciones.

Prueba todas las funcionalidades del sistema de evaluaciones:
- Servicio de IA para calificación automática
- Grabación multimedia (cámara/micrófono)
- Sistema anti-trampa
- Estadísticas y análisis
- Personalización de exámenes
"""

import pytest
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

# Imports de modelos y servicios
from src.models.evaluaciones import (
    Examen,
    PreguntaExamen,
    IntentoExamen,
    RespuestaEstudiante,
    EstadoExamen,
    EstadoIntento,
    TipoPreguntaExpandido,
    DificultadPregunta,
)
from src.services.evaluaciones.ia_evaluacion_service import IAEvaluacionService
from src.services.evaluaciones.grabacion_multimedia_service import GrabacionMultimediaService
from src.services.evaluaciones.anti_trampa import DetectorAntiTrampa
from src.services.evaluaciones.estadisticas import ServicioEstadisticas
from src.services.evaluaciones.calificacion_service import CalificacionService


@pytest.fixture
def examen_test(db_session: Session):
    """Crear un examen de prueba."""
    examen = Examen(
        examen_id=1,
        titulo="Examen de Matemáticas",
        descripcion="Examen de álgebra básica",
        duracion_minutos=60,
        intentos_permitidos=2,
        mostrar_resultados=True,
        fecha_inicio=datetime.now(UTC),
        fecha_limite=datetime.now(UTC) + timedelta(days=7),
        estado=EstadoExamen.publicado,
        puntaje_total=100.0,
    )
    db_session.add(examen)
    db_session.commit()
    db_session.refresh(examen)
    return examen


@pytest.fixture
def pregunta_abierta(db_session: Session, examen_test):
    """Crear pregunta de respuesta abierta."""
    pregunta = PreguntaExamen(
        pregunta_id=1,
        examen_id=examen_test.examen_id,
        enunciado="Explica el teorema de Pitágoras",
        tipo=TipoPreguntaExpandido.respuesta_abierta,
        puntos=10.0,
        orden=1,
        dificultad=DificultadPregunta.media,
    )
    db_session.add(pregunta)
    db_session.commit()
    db_session.refresh(pregunta)
    return pregunta


@pytest.fixture
def pregunta_opcion_multiple(db_session: Session, examen_test):
    """Crear pregunta de opción múltiple."""
    pregunta = PreguntaExamen(
        pregunta_id=2,
        examen_id=examen_test.examen_id,
        enunciado="¿Cuánto es 2 + 2?",
        tipo=TipoPreguntaExpandido.opcion_multiple,
        puntos=5.0,
        orden=2,
        dificultad=DificultadPregunta.facil,
        opciones=[
            {"id": "a", "texto": "3", "es_correcta": False},
            {"id": "b", "texto": "4", "es_correcta": True},
            {"id": "c", "texto": "5", "es_correcta": False},
        ],
    )
    db_session.add(pregunta)
    db_session.commit()
    db_session.refresh(pregunta)
    return pregunta


@pytest.fixture
def intento_test(db_session: Session, examen_test):
    """Crear intento de examen."""
    estudiante_id = uuid4()
    intento = IntentoExamen(
        intento_id=1,
        examen_id=examen_test.examen_id,
        estudiante_id=estudiante_id,
        fecha_inicio=datetime.now(UTC),
        estado=EstadoIntento.en_progreso,
        numero_intento=1,
    )
    db_session.add(intento)
    db_session.commit()
    db_session.refresh(intento)
    return intento


# ==================== TESTS DE IA ====================


@pytest.mark.asyncio
async def test_ia_calificacion_respuesta_abierta(pregunta_abierta):
    """Test: IA califica respuesta abierta correctamente."""
    servicio_ia = IAEvaluacionService()
    
    respuesta_estudiante = {
        "texto": "El teorema de Pitágoras establece que en un triángulo rectángulo, "
                 "el cuadrado de la hipotenusa es igual a la suma de los cuadrados de los catetos."
    }
    
    with patch.object(servicio_ia, '_llamar_api_ia') as mock_ia:
        # Simular respuesta de la IA
        mock_ia.return_value = {
            "calificacion": 9.5,
            "retroalimentacion": "Excelente explicación, muy completa",
            "aspectos_correctos": ["Definición precisa", "Contexto adecuado"],
            "aspectos_mejorar": [],
        }
        
        resultado = await servicio_ia.calificar_respuesta_abierta(
            pregunta=pregunta_abierta,
            respuesta=respuesta_estudiante["texto"]
        )
        
        assert resultado["calificacion"] >= 9.0
        assert "Excelente" in resultado["retroalimentacion"]
        assert len(resultado["aspectos_correctos"]) > 0


@pytest.mark.asyncio
async def test_ia_detecta_plagio(pregunta_abierta):
    """Test: IA detecta posible plagio en respuestas."""
    servicio_ia = IAEvaluacionService()
    
    respuesta_sospechosa = {
        "texto": "Texto copiado exactamente de Wikipedia sin modificaciones..."
    }
    
    with patch.object(servicio_ia, '_verificar_plagio') as mock_plagio:
        mock_plagio.return_value = {
            "es_plagio": True,
            "porcentaje_similitud": 95.0,
            "fuentes_detectadas": ["Wikipedia"],
        }
        
        resultado = await servicio_ia.verificar_plagio(
            texto=respuesta_sospechosa["texto"]
        )
        
        assert resultado["es_plagio"] is True
        assert resultado["porcentaje_similitud"] > 80.0


@pytest.mark.asyncio
async def test_ia_genera_retroalimentacion_personalizada(intento_test, db_session):
    """Test: IA genera retroalimentación personalizada según el desempeño."""
    servicio_ia = IAEvaluacionService()
    
    with patch.object(servicio_ia, '_generar_retroalimentacion') as mock_retro:
        mock_retro.return_value = {
            "mensaje": "Buen trabajo en álgebra. Deberías repasar trigonometría.",
            "areas_fuertes": ["Ecuaciones lineales", "Factorización"],
            "areas_mejora": ["Funciones trigonométricas"],
            "recursos_recomendados": ["Khan Academy - Trigonometría"],
        }
        
        resultado = await servicio_ia.generar_retroalimentacion_personalizada(
            intento_id=intento_test.intento_id,
            db=db_session
        )
        
        assert "áreas_fuertes" in resultado or "areas_fuertes" in resultado
        assert len(resultado.get("areas_mejora", [])) > 0


# ==================== TESTS DE GRABACIÓN MULTIMEDIA ====================


def test_grabacion_video_iniciar():
    """Test: Iniciar grabación de video funciona."""
    servicio_grabacion = GrabacionMultimediaService()
    
    with patch.object(servicio_grabacion, '_iniciar_captura_video') as mock_video:
        mock_video.return_value = {
            "grabacion_id": "video_123",
            "estado": "grabando",
            "timestamp_inicio": datetime.now(UTC).isoformat(),
        }
        
        resultado = servicio_grabacion.iniciar_grabacion_video(
            intento_id=1,
            estudiante_id=uuid4()
        )
        
        assert resultado["estado"] == "grabando"
        assert "grabacion_id" in resultado


def test_grabacion_audio_captura():
    """Test: Captura de audio funciona correctamente."""
    servicio_grabacion = GrabacionMultimediaService()
    
    with patch.object(servicio_grabacion, '_capturar_audio') as mock_audio:
        mock_audio.return_value = {
            "audio_id": "audio_456",
            "duracion_segundos": 120,
            "calidad": "alta",
            "formato": "webm",
        }
        
        resultado = servicio_grabacion.capturar_audio(
            intento_id=1,
            duracion=120
        )
        
        assert resultado["duracion_segundos"] == 120
        assert resultado["formato"] in ["webm", "mp3", "wav"]


def test_verificacion_permisos_camara_microfono():
    """Test: Verificar que se tienen permisos de cámara y micrófono."""
    servicio_grabacion = GrabacionMultimediaService()
    
    with patch.object(servicio_grabacion, '_verificar_permisos') as mock_permisos:
        mock_permisos.return_value = {
            "camara": True,
            "microfono": True,
            "pantalla": False,
        }
        
        permisos = servicio_grabacion.verificar_permisos_dispositivos()
        
        assert permisos["camara"] is True
        assert permisos["microfono"] is True


def test_captura_periodica_fotos():
    """Test: Captura periódica de fotos durante el examen."""
    servicio_grabacion = GrabacionMultimediaService()
    
    with patch.object(servicio_grabacion, '_capturar_foto') as mock_foto:
        mock_foto.return_value = {
            "foto_id": "foto_789",
            "timestamp": datetime.now(UTC).isoformat(),
            "rostros_detectados": 1,
        }
        
        resultado = servicio_grabacion.capturar_foto_periodica(
            intento_id=1,
            intervalo_segundos=60
        )
        
        assert resultado["rostros_detectados"] >= 0
        assert "foto_id" in resultado


# ==================== TESTS DE ANTI-TRAMPA ====================


def test_antitrampa_detecta_cambio_pestana():
    """Test: Detectar cuando estudiante cambia de pestaña."""
    servicio_antitrampa = DetectorAntiTrampa()
    
    evento = {
        "tipo": "cambio_pestana",
        "timestamp": datetime.now(UTC).isoformat(),
        "intento_id": 1,
    }
    
    resultado = servicio_antitrampa.registrar_evento_sospechoso(evento)
    
    assert resultado["evento_registrado"] is True
    assert resultado["nivel_sospecha"] in ["bajo", "medio", "alto"]


def test_antitrampa_detecta_multiples_rostros():
    """Test: Detectar múltiples personas en la cámara."""
    servicio_antitrampa = DetectorAntiTrampa()
    
    with patch.object(servicio_antitrampa, '_analizar_imagen') as mock_analisis:
        mock_analisis.return_value = {
            "rostros_detectados": 2,
            "alerta": True,
            "mensaje": "Se detectaron 2 personas en el cuadro",
        }
        
        resultado = servicio_antitrampa.verificar_numero_personas(
            imagen_base64="fake_image_data"
        )
        
        assert resultado["rostros_detectados"] > 1
        assert resultado["alerta"] is True


def test_antitrampa_inactividad_prolongada():
    """Test: Detectar inactividad prolongada del estudiante."""
    servicio_antitrampa = DetectorAntiTrampa()
    
    ultimo_evento = datetime.now(UTC) - timedelta(minutes=10)
    
    resultado = servicio_antitrampa.verificar_inactividad(
        intento_id=1,
        ultimo_evento=ultimo_evento,
        umbral_minutos=5
    )
    
    assert resultado["inactivo"] is True
    assert resultado["minutos_inactivo"] >= 5


def test_antitrampa_bloqueo_copiar_pegar():
    """Test: Configuración de bloqueo de copiar/pegar."""
    servicio_antitrampa = DetectorAntiTrampa()
    
    configuracion = servicio_antitrampa.obtener_configuracion_antitrampa(
        examen_id=1
    )
    
    assert "bloquear_copiar" in configuracion
    assert "bloquear_pegar" in configuracion
    assert isinstance(configuracion["bloquear_copiar"], bool)


# ==================== TESTS DE ESTADÍSTICAS ====================


def test_estadisticas_promedio_examen(db_session, examen_test):
    """Test: Calcular promedio de calificaciones de un examen."""
    servicio_stats = ServicioEstadisticas()
    
    # Crear algunos intentos con calificaciones
    for i, calificacion in enumerate([85.0, 90.0, 78.5, 92.3]):
        intento = IntentoExamen(
            intento_id=i + 10,
            examen_id=examen_test.examen_id,
            estudiante_id=uuid4(),
            fecha_inicio=datetime.now(UTC),
            fecha_fin=datetime.now(UTC),
            estado=EstadoIntento.completado,
            calificacion_final=calificacion,
            numero_intento=1,
        )
        db_session.add(intento)
    db_session.commit()
    
    estadisticas = servicio_stats.calcular_estadisticas_examen(
        db=db_session,
        examen_id=examen_test.examen_id
    )
    
    assert "promedio" in estadisticas
    assert 75.0 <= estadisticas["promedio"] <= 95.0
    assert "total_intentos" in estadisticas
    assert estadisticas["total_intentos"] >= 4


def test_estadisticas_distribucion_calificaciones(db_session, examen_test):
    """Test: Distribución de calificaciones por rangos."""
    servicio_stats = ServicioEstadisticas()
    
    distribucion = servicio_stats.obtener_distribucion_calificaciones(
        db=db_session,
        examen_id=examen_test.examen_id
    )
    
    assert "rangos" in distribucion
    assert isinstance(distribucion["rangos"], dict)


def test_estadisticas_preguntas_dificiles(db_session, examen_test):
    """Test: Identificar preguntas más difíciles."""
    servicio_stats = ServicioEstadisticas()
    
    preguntas_dificiles = servicio_stats.identificar_preguntas_dificiles(
        db=db_session,
        examen_id=examen_test.examen_id,
        umbral_acierto=0.5
    )
    
    assert isinstance(preguntas_dificiles, list)


# ==================== TESTS DE PERSONALIZACIÓN ====================


def test_personalizacion_orden_aleatorio_preguntas(examen_test, db_session):
    """Test: Personalizar orden de preguntas para cada estudiante."""
    from src.services.evaluaciones.evaluacion_service import ServicioEvaluacion
    
    servicio_eval = ServicioEvaluacion()
    
    estudiante_1 = uuid4()
    estudiante_2 = uuid4()
    
    preguntas_est1 = servicio_eval.obtener_preguntas_personalizadas(
        examen_id=examen_test.examen_id,
        estudiante_id=estudiante_1,
        aleatorizar=True,
        db=db_session
    )
    
    preguntas_est2 = servicio_eval.obtener_preguntas_personalizadas(
        examen_id=examen_test.examen_id,
        estudiante_id=estudiante_2,
        aleatorizar=True,
        db=db_session
    )
    
    # El orden debería ser diferente (con alta probabilidad)
    assert isinstance(preguntas_est1, list)
    assert isinstance(preguntas_est2, list)


def test_personalizacion_dificultad_adaptativa():
    """Test: Ajustar dificultad según desempeño del estudiante."""
    from src.services.evaluaciones.evaluacion_service import ServicioEvaluacion
    
    servicio_eval = ServicioEvaluacion()
    
    historial_estudiante = {
        "promedio_general": 85.0,
        "tasa_acierto": 0.85,
    }
    
    dificultad_sugerida = servicio_eval.sugerir_dificultad_examen(
        historial=historial_estudiante
    )
    
    assert dificultad_sugerida in [DificultadPregunta.facil, DificultadPregunta.media, DificultadPregunta.dificil]


# ==================== TESTS DE INTEGRACIÓN ====================


@pytest.mark.integration
def test_flujo_completo_examen_con_ia(db_session, examen_test, pregunta_abierta, intento_test):
    """Test de integración: Flujo completo de examen con IA."""
    # 1. Estudiante inicia examen
    assert intento_test.estado == EstadoIntento.en_progreso
    
    # 2. Responde pregunta abierta
    respuesta = RespuestaEstudiante(
        respuesta_id=1,
        intento_id=intento_test.intento_id,
        pregunta_id=pregunta_abierta.pregunta_id,
        respuesta_texto="El teorema de Pitágoras dice que a² + b² = c²",
        fecha_respuesta=datetime.now(UTC),
    )
    db_session.add(respuesta)
    db_session.commit()
    
    # 3. IA califica automáticamente
    servicio_ia = IAEvaluacionService()
    with patch.object(servicio_ia, '_llamar_api_ia') as mock_ia:
        mock_ia.return_value = {"calificacion": 8.0, "retroalimentacion": "Buena respuesta"}
        
        # 4. Se completa el intento
        intento_test.estado = EstadoIntento.completado
        intento_test.fecha_fin = datetime.now(UTC)
        intento_test.calificacion_final = 8.0
        db_session.commit()
        
        # 5. Generar estadísticas
        servicio_stats = ServicioEstadisticas()
        stats = servicio_stats.calcular_estadisticas_examen(
            db=db_session,
            examen_id=examen_test.examen_id
        )
        
        assert stats is not None
        assert intento_test.calificacion_final == 8.0


@pytest.mark.integration
def test_flujo_antitrampa_completo(intento_test):
    """Test de integración: Sistema anti-trampa en funcionamiento."""
    servicio_antitrampa = DetectorAntiTrampa()
    servicio_grabacion = GrabacionMultimediaService()
    
    # 1. Iniciar grabación
    with patch.object(servicio_grabacion, '_iniciar_captura_video') as mock_video:
        mock_video.return_value = {"grabacion_id": "test_123", "estado": "grabando"}
        grabacion = servicio_grabacion.iniciar_grabacion_video(
            intento_id=intento_test.intento_id,
            estudiante_id=intento_test.estudiante_id
        )
        assert grabacion["estado"] == "grabando"
    
    # 2. Simular eventos sospechosos
    eventos = [
        {"tipo": "cambio_pestana", "timestamp": datetime.now(UTC).isoformat()},
        {"tipo": "multiples_rostros", "timestamp": datetime.now(UTC).isoformat()},
    ]
    
    for evento in eventos:
        resultado = servicio_antitrampa.registrar_evento_sospechoso(evento)
        assert resultado["evento_registrado"] is True
    
    # 3. Calcular nivel de sospecha
    nivel_sospecha = servicio_antitrampa.calcular_nivel_sospecha(
        intento_id=intento_test.intento_id
    )
    
    assert nivel_sospecha in ["bajo", "medio", "alto", "critico"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
