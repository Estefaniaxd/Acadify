"""
Tests de Integración: Sistema de Puntos + Evaluaciones

Tests completos para verificar la integración entre:
- PuntosService (gamificación)
- PuntosIntegrationService (bridge)
- IntentoService (evaluaciones)

Author: GitHub Copilot & Team
Date: 31 octubre 2025
"""

import pytest
import asyncio
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.db.base_class import Base
from src.models.evaluaciones.evaluacion_expandida import Evaluacion, PreguntaEvaluacion
from src.models.evaluaciones import IntentoEvaluacion, RespuestaEstudiante
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.models.gamification.historial_puntos import HistorialPuntos
from src.models.gamification.insignia import Insignia
from src.models.gamification.usuario_insignia import UsuarioInsignia
from src.services.evaluaciones.puntos_integration_service import PuntosIntegrationService
from src.services.gamification.puntos_service import PuntosService
from src.models.evaluaciones.evaluacion_expandida import TipoPreguntaExpandido, TipoEvaluacion
from src.models.evaluaciones.intento_respuesta_gamificacion import EstadoIntento


# ==================== CONFIGURACIÓN DE TEST ====================

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/acadify_test"

@pytest.fixture(scope="session")
def event_loop():
    """Crea un event loop para toda la sesión de tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Crea el engine de base de datos para tests"""
    engine = create_async_engine(
        TEST_DB_URL,
        echo=False,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db(engine) -> AsyncSession:
    """Crea una sesión de base de datos para cada test"""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def estudiante_id():
    """ID de estudiante de prueba"""
    return uuid4()


@pytest.fixture
async def evaluacion_con_puntos(db: AsyncSession, estudiante_id: UUID):
    """Crea una evaluación configurada para otorgar puntos"""
    evaluacion = Evaluacion(
        evaluacion_id=uuid4(),
        titulo="Evaluación de Prueba con Puntos",
        descripcion="Test de integración puntos",
        tipo_evaluacion=TipoEvaluacion.EXAMEN_FINAL,
        otorga_puntos=True,
        puntos_base=100,
        puntos_por_acierto=10,
        multiplicador_puntos=1.5,
        tiempo_limite_minutos=60,
        puntuacion_total=100,
        puntuacion_minima_aprobacion=60,
        estado="PUBLICADO",
        fecha_creacion=datetime.now(timezone.utc)
    )
    
    db.add(evaluacion)
    await db.flush()
    
    # Agregar preguntas
    for i in range(5):
        pregunta = PreguntaEvaluacion(
            evaluacion_id=evaluacion.evaluacion_id,
            enunciado=f"Pregunta {i+1}",
            tipo_pregunta=TipoPreguntaExpandido.OPCION_MULTIPLE,
            opciones=["A", "B", "C", "D"],
            respuesta_correcta="A",
            puntuacion=20.0
        )
        db.add(pregunta)
    
    await db.commit()
    await db.refresh(evaluacion)
    
    return evaluacion


@pytest.fixture
async def intento_completo(
    db: AsyncSession,
    evaluacion_con_puntos: Evaluacion,
    estudiante_id: UUID
):
    """Crea un intento completo y listo para finalizar"""
    intento = IntentoEvaluacion(
        evaluacion_id=evaluacion_con_puntos.id,
        estado=EstadoIntento.EN_PROGRESO) - timedelta(minutes=30),  # 85% de calificación,
        porcentaje=85.0,  # 30 minutos        nivel_riesgo="NINGUNO")
    
    db.add(intento)
    await db.flush()
    
    # Agregar respuestas (4 correctas, 1 incorrecta)
    preguntas = await db.execute(
        "SELECT id FROM preguntas_evaluacion WHERE evaluacion_id = :eval_id",
        {"eval_id": evaluacion_con_puntos.id}
    )
    pregunta_ids = [row[0] for row in preguntas.fetchall()]
    
    for idx, pregunta_id in enumerate(pregunta_ids):
        respuesta = RespuestaEstudiante(
            respuesta_id=uuid4(),
            intento_id=intento.intento_id,
            pregunta_id=pregunta_id,
            respuesta_texto="A" if idx < 4 else "B",  # 4 correctas,
            es_correcta=idx < 4,
            puntuacion_maxima=20)
        db.add(respuesta)
    
    await db.commit()
    await db.refresh(intento)
    
    return intento


@pytest.fixture
async def insignias_base(db: AsyncSession):
    """Crea insignias base para pruebas"""
    insignias = [
        Insignia(
            insignia_id=uuid4(),
            nombre="Novato",
            descripcion="Otorgada al alcanzar 100 puntos",
            umbral_puntos=100,
            imagen_url="https://example.com/novato.png",
        ),
        Insignia(
            insignia_id=uuid4(),
            nombre="Primera Evaluación",
            descripcion="Completar tu primera evaluación",
            umbral_puntos=0,
            imagen_url="https://example.com/primera.png",
        ),
        Insignia(
            insignia_id=uuid4(),
            nombre="Perfeccionista",
            descripcion="Obtener 100% en una evaluación",
            umbral_puntos=0,
            imagen_url="https://example.com/perfeccionista.png",
        ),
        Insignia(
            insignia_id=uuid4(),
            nombre="Velocista",
            descripcion="Completar evaluación en menos del 50% del tiempo",
            umbral_puntos=0,
            imagen_url="https://example.com/velocista.png",
        ),
    ]
    
    for insignia in insignias:
        db.add(insignia)
    
    await db.commit()
    return insignias


# ==================== TESTS DE INTEGRACIÓN ====================

@pytest.mark.asyncio
async def test_procesar_evaluacion_completada_basico(
    db: AsyncSession,
    intento_completo: IntentoEvaluacion,
    estudiante_id: UUID,
    insignias_base: list
):
    """Test básico: Procesar evaluación completada otorga puntos"""
    
    # Arrange
    service = PuntosIntegrationService(db)
    intento_completo.estado = EstadoIntento.FINALIZADO,
    intento_completo.fecha_cierre= datetime.now(timezone.utc)
    await db.commit()
    
    # Act
    resultado = await service.procesar_evaluacion_completada(
        intento_id=intento_completo.id,
        estudiante_id=estudiante_id,
    )
    
    # Assert
    assert resultado["success"] is True
    assert resultado["puntos_ganados"] > 0
    assert "puntos_acumulados" in resultado
    assert "nivel_actual" in resultado
    assert resultado["calificacion"] == 85.0
    
    # Verificar que se actualizó el intento
    await db.refresh(intento_completo)
    assert intento_completo.puntos_ganados > 0
    assert intento_completo.multiplicador_aplicado > 0


@pytest.mark.asyncio
async def test_calcular_puntos_con_bonificaciones(
    db: AsyncSession,
    evaluacion_con_puntos: Evaluacion,
    estudiante_id: UUID
):
    """Test: Calcular puntos con bonus por tiempo y precisión"""
    
    # Arrange - Intento rápido (20 minutos) y con alta calificación (95%)
    intento = IntentoEvaluacion(
        evaluacion_id=evaluacion_con_puntos.id,
        estado=EstadoIntento.FINALIZADO) - timedelta(minutes=20),
        fecha_cierre=datetime.now(timezone.utc),  # 20 minutos (< 70% del límite)
        aprobado=True,
    )
    
    db.add(intento)
    await db.commit()
    
    service = PuntosIntegrationService(db)
    
    # Act
    resultado = await service.procesar_evaluacion_completada(
        intento_id=intento.intento_id,
        estudiante_id=estudiante_id,
    )
    
    # Assert
    assert resultado["success"] is True
    assert resultado["bonus_tiempo"] > 0  # Debe tener bonus por tiempo
    assert resultado["bonus_precision"] > 0  # Debe tener bonus por precisión (>90%)
    assert resultado["multiplicador_aplicado"] >= 1.5  # Multiplicador de la evaluación
    
    # Los puntos totales deben ser mayores al base
    assert resultado["puntos_ganados"] > evaluacion_con_puntos.puntos_base


@pytest.mark.asyncio
async def test_multiplicador_racha(
    db: AsyncSession,
    evaluacion_con_puntos: Evaluacion,
    estudiante_id: UUID
):
    """Test: Verificar multiplicador por racha de evaluaciones aprobadas"""
    
    # Arrange - Crear 5 intentos previos aprobados (racha)
    for i in range(5):
        intento_previo = IntentoEvaluacion(
            evaluacion_id=evaluacion_con_puntos.id,
            estado=EstadoIntento.FINALIZADO) - timedelta(days=i+1),
            fecha_cierre=datetime.now(timezone.utc) - timedelta(days=i+1),
            porcentaje=80.0)
        db.add(intento_previo)
    
    await db.commit()
    
    # Nuevo intento
    intento_nuevo = IntentoEvaluacion(
        evaluacion_id=evaluacion_con_puntos.id,
        estado=EstadoIntento.FINALIZADO) - timedelta(minutes=30),
        fecha_cierre=datetime.now(timezone.utc),
        tiempo_total_segundos=1800)
    
    db.add(intento_nuevo)
    await db.commit()
    
    service = PuntosIntegrationService(db)
    
    # Act
    resultado = await service.procesar_evaluacion_completada(
        intento_id=intento_nuevo.id,
        estudiante_id=estudiante_id,
    )
    
    # Assert
    assert resultado["success"] is True
    # Con racha de 5, debe aplicar multiplicador 1.2
    desglose = resultado["desglose"]
    assert desglose["multiplicador_racha"] == 1.2
    assert "5" in desglose["formula"] or "racha" in str(desglose).lower()


@pytest.mark.asyncio
async def test_otorgar_insignia_primera_evaluacion(
    db: AsyncSession,
    intento_completo: IntentoEvaluacion,
    estudiante_id: UUID,
    insignias_base: list
):
    """Test: Otorgar insignia 'Primera Evaluación' al completar la primera"""
    
    # Arrange
    service = PuntosIntegrationService(db)
    intento_completo.estado = EstadoIntento.FINALIZADO,
    intento_completo.fecha_cierre= datetime.now(timezone.utc)
    await db.commit()
    
    # Act
    resultado = await service.procesar_evaluacion_completada(
        intento_id=intento_completo.id,
        estudiante_id=estudiante_id,
    )
    
    # Assert
    assert "nuevas_insignias" in resultado
    insignias = resultado["nuevas_insignias"]
    
    # Debe tener al menos la insignia "Primera Evaluación"
    nombres_insignias = [i["nombre"] for i in insignias]
    assert "Primera Evaluación" in nombres_insignias
    
    # Verificar en base de datos
    usuario_insignias = await db.execute(
        "SELECT COUNT(*) FROM usuario_insignias WHERE usuario_id = :user_id",
        {"user_id": estudiante_id}
    )
    count = usuario_insignias.scalar()
    assert count > 0


@pytest.mark.asyncio
async def test_otorgar_insignia_perfeccionista(
    db: AsyncSession,
    evaluacion_con_puntos: Evaluacion,
    estudiante_id: UUID,
    insignias_base: list
):
    """Test: Otorgar insignia 'Perfeccionista' al obtener 100%"""
    
    # Arrange - Intento con 100% de calificación
    intento = IntentoEvaluacion(
        evaluacion_id=evaluacion_con_puntos.id,
        estado=EstadoIntento.FINALIZADO) - timedelta(minutes=30),
        fecha_cierre=datetime.now(timezone.utc),
        tiempo_total_segundos=1800)
    
    db.add(intento)
    await db.commit()
    
    service = PuntosIntegrationService(db)
    
    # Act
    resultado = await service.procesar_evaluacion_completada(
        intento_id=intento.intento_id,
        estudiante_id=estudiante_id,
    )
    
    # Assert
    insignias = resultado["nuevas_insignias"]
    nombres = [i["nombre"] for i in insignias]
    assert "Perfeccionista" in nombres


@pytest.mark.asyncio
async def test_otorgar_insignia_velocista(
    db: AsyncSession,
    evaluacion_con_puntos: Evaluacion,
    estudiante_id: UUID,
    insignias_base: list
):
    """Test: Otorgar insignia 'Velocista' al completar en <50% del tiempo"""
    
    # Arrange - Completar en 20 minutos (33% del límite de 60 min)
    intento = IntentoEvaluacion(
        evaluacion_id=evaluacion_con_puntos.id,
        estado=EstadoIntento.FINALIZADO) - timedelta(minutes=20),
        fecha_cierre=datetime.now(timezone.utc),  # 20 minutos,
        aprobado=True,
    )
    
    db.add(intento)
    await db.commit()
    
    service = PuntosIntegrationService(db)
    
    # Act
    resultado = await service.procesar_evaluacion_completada(
        intento_id=intento.intento_id,
        estudiante_id=estudiante_id,
    )
    
    # Assert
    insignias = resultado["nuevas_insignias"]
    nombres = [i["nombre"] for i in insignias]
    assert "Velocista" in nombres


@pytest.mark.asyncio
async def test_ranking_evaluacion(
    db: AsyncSession,
    evaluacion_con_puntos: Evaluacion
):
    """Test: Obtener ranking de una evaluación"""
    
    # Arrange - Crear 5 estudiantes con diferentes puntajes
    estudiantes = [uuid4() for _ in range(5)]
    puntajes = [150, 200, 175, 125, 190]
    
    for idx, estudiante_id in enumerate(estudiantes):
        intento = IntentoEvaluacion(
            evaluacion_id=evaluacion_con_puntos.id,
            estado=EstadoIntento.FINALIZADO,
            fecha_cierre=datetime.now(timezone.utc),
            tiempo_total_segundos=1800,
        )
        db.add(intento)
    
    await db.commit()
    
    service = PuntosIntegrationService(db)
    
    # Act
    ranking = await service.obtener_ranking_evaluacion(
        evaluacion_id=evaluacion_con_puntos.id,
        limite=10,
    )
    
    # Assert
    assert ranking["success"] is True
    assert ranking["total_participantes"] == 5
    
    # Verificar orden (mayor a menor puntos)
    ranking_list = ranking["ranking"]
    assert ranking_list[0]["posicion"] == 1,
    assert ranking_list[0]["puntos_ganados"] == 200  # Mayor puntaje,
    assert ranking_list[1]["puntos_ganados"] == 190,
    assert ranking_list[2]["puntos_ganados"] == 175,
    assert ranking_list[3]["puntos_ganados"] == 150,
    assert ranking_list[4]["puntos_ganados"] == 125  # Menor puntaje


@pytest.mark.asyncio
async def test_no_otorgar_puntos_duplicados(
    db: AsyncSession,
    intento_completo: IntentoEvaluacion,
    estudiante_id: UUID
):
    """Test: No otorgar puntos si ya fueron otorgados previamente"""
    
    # Arrange
    service = PuntosIntegrationService(db)
    intento_completo.estado = EstadoIntento.FINALIZADO,
    intento_completo.fecha_cierre= datetime.now(timezone.utc)
    await db.commit()
    
    # Primera ejecución
    resultado1 = await service.procesar_evaluacion_completada(
        intento_id=intento_completo.id,
        estudiante_id=estudiante_id,
    )
    
    puntos_primera_vez = resultado1["puntos_ganados"]
    
    # Act - Segunda ejecución (debería detectar duplicado)
    resultado2 = await service.procesar_evaluacion_completada(
        intento_id=intento_completo.id,
        estudiante_id=estudiante_id,
    )
    
    # Assert
    assert resultado2["ya_procesado"] is True
    assert resultado2["puntos_ganados"] == puntos_primera_vez
    
    # Verificar que no se duplicaron en historial
    historial = await db.execute(
        "SELECT COUNT(*) FROM historial_puntos WHERE usuario_id = :user_id",
        {"user_id": estudiante_id}
    )
    count = historial.scalar()
    assert count == 1  # Solo debe haber 1 entrada


@pytest.mark.asyncio
async def test_evaluacion_sin_puntos(
    db: AsyncSession,
    estudiante_id: UUID
):
    """Test: Evaluaciones con otorga_puntos=False no otorgan puntos"""
    
    # Arrange - Evaluación sin puntos
    evaluacion = Evaluacion(
        evaluacion_id=uuid4(),
        titulo="Evaluación Sin Puntos",
        otorga_puntos=False,  # ← Clave,
        puntuacion_total=100,
        estado="PUBLICADO",
        fecha_creacion=datetime.now(timezone.utc)
    )
    
    db.add(evaluacion)
    await db.flush()
    
    intento = IntentoEvaluacion(
        evaluacion_id=evaluacion.evaluacion_id,
        estado=EstadoIntento.FINALIZADO,
        fecha_cierre=datetime.now(timezone.utc),
        porcentaje=85.0,
    )
    
    db.add(intento)
    await db.commit()
    
    service = PuntosIntegrationService(db)
    
    # Act
    resultado = await service.procesar_evaluacion_completada(
        intento_id=intento.intento_id,
        estudiante_id=estudiante_id,
    )
    
    # Assert
    assert resultado["puntos_ganados"] == 0
    assert resultado["otorga_puntos"] is False
    assert "no otorga puntos" in resultado["razon"].lower()


@pytest.mark.asyncio
async def test_integracion_completa_ciclo_vida(
    db: AsyncSession,
    evaluacion_con_puntos: Evaluacion,
    estudiante_id: UUID,
    insignias_base: list
):
    """Test E2E: Ciclo completo desde inicio hasta otorgamiento de puntos"""
    
    # 1. Crear intento
    intento = IntentoEvaluacion(
        evaluacion_id=evaluacion_con_puntos.id,
        estado=EstadoIntento.INICIADO),
        puntuacion_maxima=100,
    )
    
    db.add(intento)
    await db.commit()
    
    # 2. Cambiar a EN_PROGRESO y responder preguntas
    intento.estado = EstadoIntento.EN_PROGRESO,
    intento.preguntas_respondidas = 5,
    intento.puntuacion_obtenida = 90,
    intento.porcentaje = 90.0,
    intento.tiempo_total_segundos = 1500
    await db.commit()
    
    # 3. Finalizar intento
    intento.estado = EstadoIntento.FINALIZADO,
    intento.fecha_cierre= datetime.now(timezone.utc)
    intento.aprobado = True
    await db.commit()
    
    # 4. Procesar puntos (simula lo que hace IntentoService.finalizar_intento)
    service = PuntosIntegrationService(db)
    resultado = await service.procesar_evaluacion_completada(
        intento_id=intento.intento_id,
        estudiante_id=estudiante_id,
    )
    
    # 5. Verificaciones finales
    assert resultado["success"] is True
    assert resultado["puntos_ganados"] > 0
    assert len(resultado["nuevas_insignias"]) > 0
    assert "nivel_actual" in resultado
    
    # Verificar intento actualizado
    await db.refresh(intento)
    assert intento.puntos_ganados > 0
    assert intento.multiplicador_aplicado > 0
    
    # Verificar puntos en usuario
    usuario_puntos = await db.execute(
        "SELECT puntos_acumulados FROM usuario_puntos WHERE usuario_id = :user_id",
        {"user_id": estudiante_id}
    )
    puntos = usuario_puntos.scalar()
    assert puntos == resultado["puntos_ganados"]
    
    # Verificar historial
    historial = await db.execute(
        "SELECT COUNT(*) FROM historial_puntos WHERE usuario_id = :user_id",
        {"user_id": estudiante_id}
    )
    count = historial.scalar()
    assert count > 0


# ==================== TESTS DE ERROR HANDLING ====================

@pytest.mark.asyncio
async def test_error_intento_no_encontrado(db: AsyncSession, estudiante_id: UUID):
    """Test: Error cuando el intento no existe"""
    
    service = PuntosIntegrationService(db)
    
    with pytest.raises(ValueError, match="no encontrado"):
        await service.procesar_evaluacion_completada(
            intento_id=uuid4(),  # ID que no existe,
            estudiante_id=estudiante_id,
        )


@pytest.mark.asyncio
async def test_error_intento_no_completado(
    db: AsyncSession,
    evaluacion_con_puntos: Evaluacion,
    estudiante_id: UUID
):
    """Test: Error cuando el intento no está completado"""
    
    # Arrange - Intento EN_PROGRESO
    intento = IntentoEvaluacion(
        evaluacion_id=evaluacion_con_puntos.id,
        estado=EstadoIntento.EN_PROGRESO  # ← No finalizado,
    )
    
    db.add(intento)
    await db.commit()
    
    service = PuntosIntegrationService(db)
    
    # Act & Assert
    with pytest.raises(ValueError, match="no está completado"):
        await service.procesar_evaluacion_completada(
            intento_id=intento.intento_id,
            estudiante_id=estudiante_id,
        )


# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
