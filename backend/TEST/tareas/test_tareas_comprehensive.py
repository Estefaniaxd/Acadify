"""Tests comprehensivos del sistema de tareas.

Prueba todas las funcionalidades del sistema de tareas:
- Creación y gestión de tareas
- Entregas de estudiantes
- Calificación manual y con IA
- Retroalimentación personalizada con IA
- Sistema de puntos y gamificación
- Rúbricas de evaluación
- Entregas tardías y múltiples intentos
"""

import pytest
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4

from sqlalchemy.orm import Session

# Imports de modelos
from src.models.academic.tarea import Tarea, EntregaTarea, Rubrica, EstadoTarea, TipoTarea, PrioridadTarea
from src.models.academic.grupo import Grupo
from src.models.academic.curso import Curso
from src.models.users.usuario import Usuario

# Imports de servicios
from src.services.academic.tarea_service import TareaService
from src.services.academic.tarea_enriched_service import TareaEnriquecidaService


# ==================== FIXTURES ====================


@pytest.fixture
def docente_test(db_session: Session):
    """Crear docente de prueba."""
    docente = Usuario(
        usuario_id=str(uuid4()),
        correo_institucional=f"docente_{uuid4().hex[:8]}@test.com",
        username=f"docente_{uuid4().hex[:8]}",
        numero_documento="12345678",
        tipo_documento="CC",
        rol="docente",
        password_hash="hashed_password",
    )
    db_session.add(docente)
    db_session.commit()
    db_session.refresh(docente)
    return docente


@pytest.fixture
def estudiante_test(db_session: Session):
    """Crear estudiante de prueba."""
    estudiante = Usuario(
        usuario_id=str(uuid4()),
        correo_institucional=f"estudiante_{uuid4().hex[:8]}@test.com",
        username=f"estudiante_{uuid4().hex[:8]}",
        numero_documento="87654321",
        tipo_documento="CC",
        rol="estudiante",
        password_hash="hashed_password",
    )
    db_session.add(estudiante)
    db_session.commit()
    db_session.refresh(estudiante)
    return estudiante


@pytest.fixture
def curso_test(db_session: Session):
    """Crear curso de prueba."""
    curso = Curso(
        curso_id=str(uuid4()),
        nombre="Programación Python",
        codigo_curso=f"PROG{uuid4().hex[:6].upper()}",
        descripcion="Curso de Python",
        creditos=3,
        estado="activo",
    )
    db_session.add(curso)
    db_session.commit()
    db_session.refresh(curso)
    return curso


@pytest.fixture
def programa_test(db_session: Session):
    """Crear programa de prueba."""
    from src.models.academic.programa import Programa
    programa = Programa(
        programa_id=str(uuid4()),
        nombre="Ingeniería de Software",
        codigo=f"INGSW{uuid4().hex[:6].upper()}",
        descripcion="Programa de ingeniería",
    )
    db_session.add(programa)
    db_session.commit()
    db_session.refresh(programa)
    return programa


@pytest.fixture
def grupo_test(db_session: Session, programa_test):
    """Crear grupo de prueba."""
    grupo = Grupo(
        grupo_id=str(uuid4()),
        programa_id=programa_test.programa_id,
        nombre="Grupo A",
        codigo_grupo=f"GA{uuid4().hex[:6].upper()}",
        estado="activo",
    )
    db_session.add(grupo)
    db_session.commit()
    db_session.refresh(grupo)
    return grupo


@pytest.fixture
def tarea_test(db_session: Session, grupo_test, docente_test):
    """Crear tarea de prueba."""
    tarea = Tarea(
        tarea_id=str(uuid4()),
        grupo_id=grupo_test.grupo_id,
        docente_id=docente_test.usuario_id,
        titulo="Tarea de prueba: Algoritmos",
        descripcion="Implementar algoritmos de ordenamiento",
        tipo=TipoTarea.EJERCICIOS.value,
        prioridad=PrioridadTarea.MEDIA,
        fecha_limite=datetime.now(UTC) + timedelta(days=7),
        puntuacion_maxima=100.0,
        habilitar_retroalimentacion_ia=True,
        permite_entrega_tardia=True,
        intentos_maximos=3,
        estado=EstadoTarea.ASIGNADA.value,
    )
    db_session.add(tarea)
    db_session.commit()
    db_session.refresh(tarea)
    return tarea


@pytest.fixture
def rubrica_test(db_session: Session, docente_test):
    """Crear rúbrica de prueba."""
    rubrica = Rubrica(
        rubrica_id=str(uuid4()),
        nombre="Rúbrica Algoritmos",
        descripcion="Evaluación de implementación de algoritmos",
        criterios=[
            {
                "nombre": "Correctitud",
                "descripcion": "El algoritmo funciona correctamente",
                "puntos": 40.0,
                "niveles": [
                    {"nivel": "Excelente", "puntos": 40, "descripcion": "100% correcto"},
                    {"nivel": "Bueno", "puntos": 30, "descripcion": "75-99% correcto"},
                    {"nivel": "Regular", "puntos": 20, "descripcion": "50-74% correcto"},
                    {"nivel": "Insuficiente", "puntos": 0, "descripcion": "Menos de 50%"},
                ],
            },
            {
                "nombre": "Eficiencia",
                "descripcion": "Complejidad algorítmica",
                "puntos": 30.0,
            },
            {
                "nombre": "Claridad del código",
                "descripcion": "Legibilidad y documentación",
                "puntos": 30.0,
            },
        ],
        puntuacion_total=100.0,
        es_publica=True,
        creado_por=docente_test.usuario_id,
    )
    db_session.add(rubrica)
    db_session.commit()
    db_session.refresh(rubrica)
    return rubrica


# ==================== TESTS DE CREACIÓN DE TAREAS ====================


def test_crear_tarea_basica(db_session: Session, grupo_test, docente_test):
    """Test: Crear una tarea básica."""
    tarea = Tarea(
        tarea_id=str(uuid4()),
        grupo_id=grupo_test.grupo_id,
        docente_id=docente_test.usuario_id,
        titulo="Tarea de prueba",
        descripcion="Descripción de la tarea",
        fecha_limite=datetime.now(UTC) + timedelta(days=7),
        puntuacion_maxima=100.0,
        tipo=TipoTarea.ENSAYO.value,
        estado=EstadoTarea.ASIGNADA.value,
    )
    db_session.add(tarea)
    db_session.commit()
    
    assert tarea.tarea_id is not None
    assert tarea.titulo == "Tarea de prueba"
    assert tarea.tipo == TipoTarea.ENSAYO.value
    assert tarea.estado == EstadoTarea.ASIGNADA.value


def test_tarea_con_rubrica(db_session: Session, tarea_test, rubrica_test):
    """Test: Asociar rúbrica a una tarea."""
    tarea_test.rubrica_id = rubrica_test.rubrica_id
    db_session.commit()
    db_session.refresh(tarea_test)
    
    assert tarea_test.rubrica_id == rubrica_test.rubrica_id
    assert tarea_test.rubrica_obj is not None
    assert tarea_test.rubrica_obj.nombre == "Rúbrica Algoritmos"


def test_tarea_configuracion_ia(db_session: Session, tarea_test):
    """Test: Configurar IA en tarea."""
    assert tarea_test.habilitar_retroalimentacion_ia is True
    
    tarea_test.prompt_ia_personalizado = "Evalúa el código según las mejores prácticas de Python"
    db_session.commit()
    
    assert tarea_test.prompt_ia_personalizado is not None


def test_tarea_multiples_intentos(db_session: Session, tarea_test):
    """Test: Configurar múltiples intentos."""
    assert tarea_test.intentos_maximos == 3
    assert tarea_test.permite_entrega_tardia is True


# ==================== TESTS DE ENTREGAS ====================


def test_crear_entrega_basica(db_session: Session, tarea_test, estudiante_test):
    """Test: Estudiante crea una entrega."""
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        titulo_entrega="Mi solución de algoritmos",
        contenido_texto="def bubble_sort(arr): ...",
        fecha_entrega=datetime.now(UTC),
        estado="entregada",
        numero_intento=1,
    )
    db_session.add(entrega)
    db_session.commit()
    db_session.refresh(entrega)
    
    assert entrega.entrega_id is not None
    assert entrega.estado == "entregada"
    assert entrega.numero_intento == 1


def test_entrega_tardia_penalizacion(db_session: Session, tarea_test, estudiante_test):
    """Test: Detectar entrega tardía y aplicar penalización."""
    tarea_test.fecha_limite = datetime.now(UTC) - timedelta(days=1)
    tarea_test.penalizacion_tardia = 10.0  # 10% de penalización
    db_session.commit()
    
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        contenido_texto="Código tardío",
        fecha_entrega=datetime.now(UTC),
        fecha_limite_original=tarea_test.fecha_limite,
        es_entrega_tardia=True,
        estado="entregada",
    )
    db_session.add(entrega)
    db_session.commit()
    
    assert entrega.es_entrega_tardia is True


def test_multiples_intentos_estudiante(db_session: Session, tarea_test, estudiante_test):
    """Test: Estudiante realiza múltiples intentos."""
    for intento in range(1, 4):
        entrega = EntregaTarea(
            entrega_id=str(uuid4()),
            tarea_id=tarea_test.tarea_id,
            estudiante_id=estudiante_test.usuario_id,
            contenido_texto=f"Intento {intento}",
            fecha_entrega=datetime.now(UTC),
            numero_intento=intento,
            estado="entregada" if intento < 3 else "calificada",
            es_final=(intento == 3),
        )
        db_session.add(entrega)
    
    db_session.commit()
    
    entregas = db_session.query(EntregaTarea).filter(
        EntregaTarea.tarea_id == tarea_test.tarea_id,
        EntregaTarea.estudiante_id == estudiante_test.usuario_id
    ).all()
    
    assert len(entregas) == 3
    assert entregas[-1].es_final is True


# ==================== TESTS DE CALIFICACIÓN ====================


def test_calificar_entrega_manual(db_session: Session, tarea_test, estudiante_test, docente_test):
    """Test: Docente califica entrega manualmente."""
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        contenido_texto="Código bien implementado",
        fecha_entrega=datetime.now(UTC),
        estado="entregada",
    )
    db_session.add(entrega)
    db_session.commit()
    
    # Calificar
    entrega.calificar_manualmente(
        calificacion=85.0,
        comentarios="Excelente trabajo, muy bien implementado",
        calificado_por=docente_test.usuario_id,
    )
    db_session.commit()
    db_session.refresh(entrega)
    
    assert entrega.calificacion == 85.0
    assert entrega.estado == "calificada"
    assert entrega.comentarios_docente is not None
    assert entrega.fecha_calificacion is not None


def test_calificacion_con_rubrica(db_session: Session, tarea_test, rubrica_test, estudiante_test, docente_test):
    """Test: Calificar usando rúbrica."""
    tarea_test.rubrica_id = rubrica_test.rubrica_id
    db_session.commit()
    
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        contenido_texto="Código con rúbrica",
        fecha_entrega=datetime.now(UTC),
        estado="entregada",
    )
    db_session.add(entrega)
    db_session.commit()
    
    rubrica_calificacion = {
        "Correctitud": {"nivel": "Excelente", "puntos": 40},
        "Eficiencia": {"nivel": "Bueno", "puntos": 25},
        "Claridad del código": {"nivel": "Excelente", "puntos": 30},
    }
    
    entrega.calificar_manualmente(
        calificacion=95.0,
        comentarios="Muy buen trabajo",
        rubrica=rubrica_calificacion,
        calificado_por=docente_test.usuario_id,
    )
    db_session.commit()
    
    assert entrega.rubrica_calificacion is not None
    assert entrega.calificacion == 95.0


# ==================== TESTS DE IA ====================


@pytest.mark.asyncio
async def test_ia_calificacion_preliminar(db_session: Session, tarea_test, estudiante_test):
    """Test: IA genera calificación preliminar."""
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        contenido_texto="Implementación de bubble sort correcta",
        fecha_entrega=datetime.now(UTC),
        estado="entregada",
    )
    db_session.add(entrega)
    db_session.commit()
    
    # Simular calificación de IA
    calificacion_ia = 87.5
    retroalimentacion_ia = {
        "calificacion": 87.5,
        "aspectos_positivos": [
            "Implementación correcta del algoritmo",
            "Buen uso de variables descriptivas"
        ],
        "aspectos_mejorar": [
            "Podría optimizarse la complejidad",
            "Falta documentación en algunas funciones"
        ],
        "sugerencias": [
            "Considera usar algoritmos más eficientes como quicksort",
            "Agrega docstrings a las funciones"
        ],
    }
    
    entrega.aplicar_calificacion_ia(calificacion_ia, retroalimentacion_ia)
    db_session.commit()
    db_session.refresh(entrega)
    
    assert entrega.calificacion_preliminar_ia == 87.5
    assert entrega.retroalimentacion_ia is not None
    assert len(entrega.retroalimentacion_ia["aspectos_positivos"]) == 2


@pytest.mark.asyncio
async def test_ia_retroalimentacion_personalizada(db_session: Session, tarea_test, estudiante_test):
    """Test: IA genera retroalimentación personalizada."""
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        contenido_texto="Código con errores menores",
        fecha_entrega=datetime.now(UTC),
        estado="entregada",
    )
    db_session.add(entrega)
    db_session.commit()
    
    retroalimentacion = {
        "calificacion": 72.0,
        "analisis_detallado": {
            "correctitud": "Funciona pero tiene errores en casos extremos",
            "estilo": "Buen estilo de código, cumple PEP8",
            "eficiencia": "Complejidad O(n²) - podría mejorarse",
        },
        "recomendaciones": [
            "Prueba tu código con casos límite (arrays vacíos, un elemento)",
            "Investiga algoritmos O(n log n) como merge sort",
        ],
    }
    
    entrega.aplicar_calificacion_ia(72.0, retroalimentacion)
    db_session.commit()
    
    assert entrega.tiene_retroalimentacion_ia is True
    assert entrega.tiene_calificacion_preliminar is True


@pytest.mark.asyncio
async def test_comparacion_calificacion_ia_vs_docente(db_session: Session, tarea_test, estudiante_test, docente_test):
    """Test: Comparar calificación de IA vs docente."""
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        contenido_texto="Código complejo",
        fecha_entrega=datetime.now(UTC),
        estado="entregada",
    )
    db_session.add(entrega)
    db_session.commit()
    
    # IA califica primero
    entrega.aplicar_calificacion_ia(82.0, {"analisis": "Buena implementación"})
    db_session.commit()
    
    # Docente califica después
    entrega.calificar_manualmente(
        calificacion=85.0,
        comentarios="La IA fue un poco conservadora, merece 85",
        calificado_por=docente_test.usuario_id,
    )
    db_session.commit()
    db_session.refresh(entrega)
    
    diferencia = entrega.diferencia_calificacion_ia
    assert diferencia == 3.0  # 85 - 82
    assert entrega.calificacion > entrega.calificacion_preliminar_ia


# ==================== TESTS DE GAMIFICACIÓN ====================


def test_otorgar_puntos_gamificacion(db_session: Session, tarea_test, estudiante_test):
    """Test: Otorgar puntos de gamificación por entrega."""
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        contenido_texto="Entrega excelente",
        fecha_entrega=datetime.now(UTC),
        estado="calificada",
        calificacion=95.0,
    )
    db_session.add(entrega)
    db_session.commit()
    
    # Otorgar puntos
    puntos_base = 100
    puntos_bonificacion = 50  # Por excelencia (95+)
    entrega.otorgar_puntos(puntos_base + puntos_bonificacion)
    db_session.commit()
    
    assert entrega.puntos_otorgados == 150


def test_puntos_por_entrega_temprana(db_session: Session, tarea_test, estudiante_test):
    """Test: Bonificación por entrega temprana."""
    dias_anticipacion = 5
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        contenido_texto="Entrega anticipada",
        fecha_entrega=datetime.now(UTC),
        fecha_limite_original=datetime.now(UTC) + timedelta(days=dias_anticipacion),
        estado="calificada",
        calificacion=85.0,
    )
    db_session.add(entrega)
    db_session.commit()
    
    # Calcular bonificación por anticipación (10 puntos por día)
    puntos_anticipacion = dias_anticipacion * 10
    entrega.otorgar_puntos(100 + puntos_anticipacion)
    db_session.commit()
    
    assert entrega.puntos_otorgados == 150  # 100 base + 50 bonificación


# ==================== TESTS DE PROPIEDADES CALCULADAS ====================


def test_tarea_propiedades_calculadas(db_session: Session, tarea_test, estudiante_test):
    """Test: Propiedades calculadas de la tarea."""
    # Crear entregas
    for i in range(5):
        calificacion = 70.0 + (i * 5)  # 70, 75, 80, 85, 90
        entrega = EntregaTarea(
            entrega_id=str(uuid4()),
            tarea_id=tarea_test.tarea_id,
            estudiante_id=str(uuid4()),
            contenido_texto=f"Entrega {i}",
            fecha_entrega=datetime.now(UTC),
            estado="calificada",
            calificacion=calificacion,
        )
        db_session.add(entrega)
    
    # Una entrega pendiente
    entrega_pendiente = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        contenido_texto="Pendiente",
        fecha_entrega=datetime.now(UTC),
        estado="entregada",
    )
    db_session.add(entrega_pendiente)
    db_session.commit()
    db_session.refresh(tarea_test)
    
    assert tarea_test.total_entregas == 6
    assert tarea_test.entregas_pendientes == 1
    assert 70.0 <= tarea_test.promedio_calificaciones <= 90.0


def test_entrega_propiedades_calculadas(db_session: Session, tarea_test, estudiante_test):
    """Test: Propiedades calculadas de la entrega."""
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        contenido_texto="Entrega para test",
        fecha_entrega=datetime.now(UTC) - timedelta(days=3),
        estado="calificada",
        calificacion=80.0,
        numero_intento=2,
    )
    db_session.add(entrega)
    db_session.commit()
    db_session.refresh(entrega)
    
    assert entrega.dias_desde_entrega >= 3
    assert entrega.porcentaje_calificacion == 80.0
    assert entrega.esta_calificada is True
    assert entrega.pendiente_revision is False


def test_entrega_intentos_restantes(db_session: Session, tarea_test, estudiante_test):
    """Test: Calcular intentos restantes."""
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        contenido_texto="Primer intento",
        fecha_entrega=datetime.now(UTC),
        numero_intento=1,
        estado="calificada",
        calificacion=60.0,
    )
    db_session.add(entrega)
    db_session.commit()
    db_session.refresh(entrega)
    
    assert entrega.intentos_restantes == 2  # 3 max - 1 usado = 2
    assert entrega.puede_reintentar is True


# ==================== TESTS DE INTEGRACIÓN ====================


@pytest.mark.integration
async def test_flujo_completo_tarea_con_ia(
    db_session: Session,
    tarea_test,
    estudiante_test,
    docente_test
):
    """Test de integración: Flujo completo de tarea con IA."""
    # 1. Estudiante entrega tarea
    entrega = EntregaTarea(
        entrega_id=str(uuid4()),
        tarea_id=tarea_test.tarea_id,
        estudiante_id=estudiante_test.usuario_id,
        titulo_entrega="Implementación de algoritmos",
        contenido_texto="""
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
        """,
        fecha_entrega=datetime.now(UTC),
        estado="entregada",
        numero_intento=1,
    )
    db_session.add(entrega)
    db_session.commit()
    
    # 2. IA analiza y genera calificación preliminar
    retroalimentacion_ia = {
        "calificacion": 85.0,
        "aspectos_positivos": [
            "Implementación correcta",
            "Código limpio y legible",
        ],
        "aspectos_mejorar": [
            "Complejidad O(n²) - considerar algoritmos más eficientes",
        ],
        "sugerencias": [
            "Investiga merge sort o quick sort para mejor rendimiento",
        ],
    }
    entrega.aplicar_calificacion_ia(85.0, retroalimentacion_ia)
    db_session.commit()
    
    assert entrega.tiene_calificacion_preliminar is True
    
    # 3. Docente revisa y ajusta calificación
    entrega.calificar_manualmente(
        calificacion=88.0,
        comentarios="Muy buen trabajo, la IA fue precisa",
        calificado_por=docente_test.usuario_id,
    )
    db_session.commit()
    
    # 4. Otorgar puntos de gamificación
    puntos = 120  # 100 base + 20 bonificación
    entrega.otorgar_puntos(puntos)
    db_session.commit()
    db_session.refresh(entrega)
    
    # Verificaciones finales
    assert entrega.esta_calificada is True
    assert entrega.calificacion == 88.0
    assert entrega.puntos_otorgados == 120
    assert entrega.diferencia_calificacion_ia == 3.0  # 88 - 85


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
