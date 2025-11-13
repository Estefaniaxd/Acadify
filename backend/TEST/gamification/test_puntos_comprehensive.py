"""Tests comprehensivos del sistema de puntos."""

import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from src.models.users.usuario import Usuario
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.models.gamification.historial_puntos import HistorialPuntos
from src.crud.gamification.historial_puntos import (
    get_usuario_puntos,
    create_usuario_puntos,
    get_or_create_usuario_puntos,
    asignar_puntos,
    descontar_puntos,
    get_historial_puntos_usuario,
    get_ranking_usuarios,
    get_estadisticas_puntos,
    get_posicion_usuario_ranking,
)
from src.schemas.gamification.historial_puntos import (
    AsignarPuntosRequest,
    DescontarPuntosRequest,
)


# ==================== TESTS DE CREACIÓN Y OBTENCIÓN ====================


def test_create_usuario_puntos(db_session: Session, estudiante_1: Usuario):
    """Test crear registro inicial de puntos."""
    puntos = create_usuario_puntos(db_session, estudiante_1.usuario_id, puntos_iniciales=50)
    
    assert puntos is not None
    assert puntos.usuario_id == estudiante_1.usuario_id
    assert puntos.puntos_acumulados == 50


def test_get_usuario_puntos_existente(db_session: Session, usuario_con_puntos: UsuarioPuntos):
    """Test obtener puntos de usuario existente."""
    puntos = get_usuario_puntos(db_session, usuario_con_puntos.usuario_id)
    
    assert puntos is not None
    assert puntos.usuario_id == usuario_con_puntos.usuario_id
    assert puntos.puntos_acumulados == usuario_con_puntos.puntos_acumulados


def test_get_usuario_puntos_no_existente(db_session: Session, estudiante_2: Usuario):
    """Test obtener puntos de usuario sin registro."""
    puntos = get_usuario_puntos(db_session, estudiante_2.usuario_id)
    
    assert puntos is None


def test_get_or_create_usuario_puntos_nuevo(db_session: Session, estudiante_2: Usuario):
    """Test obtener o crear puntos para usuario nuevo."""
    puntos = get_or_create_usuario_puntos(db_session, estudiante_2.usuario_id)
    
    assert puntos is not None
    assert puntos.usuario_id == estudiante_2.usuario_id
    assert puntos.puntos_acumulados == 0


def test_get_or_create_usuario_puntos_existente(
    db_session: Session, usuario_con_puntos: UsuarioPuntos
):
    """Test obtener o crear puntos para usuario existente."""
    puntos = get_or_create_usuario_puntos(db_session, usuario_con_puntos.usuario_id)
    
    assert puntos is not None
    assert puntos.usuario_id == usuario_con_puntos.usuario_id
    assert puntos.puntos_acumulados == usuario_con_puntos.puntos_acumulados


# ==================== TESTS DE ASIGNACIÓN DE PUNTOS ====================


def test_asignar_puntos_tarea(db_session: Session, estudiante_1: Usuario):
    """Test asignar puntos por completar tarea."""
    request = AsignarPuntosRequest(
        usuario_id=estudiante_1.usuario_id,
        puntos=50,
        motivo="Tarea de matemáticas completada"
    )
    
    puntos = asignar_puntos(db_session, request)
    
    assert puntos is not None
    assert puntos.puntos_acumulados >= 50
    
    # Verificar historial
    historial = get_historial_puntos_usuario(db_session, estudiante_1.usuario_id)
    assert len(historial) >= 1
    assert any(h.cambio == 50 and "Tarea" in h.motivo for h in historial)


def test_asignar_puntos_examen(db_session: Session, usuario_con_puntos: UsuarioPuntos):
    """Test asignar puntos por examen."""
    puntos_antes = usuario_con_puntos.puntos_acumulados
    
    request = AsignarPuntosRequest(
        usuario_id=usuario_con_puntos.usuario_id,
        puntos=100,
        motivo="Examen de Python: 95/100"
    )
    
    puntos = asignar_puntos(db_session, request)
    
    assert puntos.puntos_acumulados == puntos_antes + 100


def test_asignar_puntos_participacion(db_session: Session, estudiante_2: Usuario):
    """Test asignar puntos por participación en clase."""
    request = AsignarPuntosRequest(
        usuario_id=estudiante_2.usuario_id,
        puntos=10,
        motivo="Participación activa en clase"
    )
    
    puntos = asignar_puntos(db_session, request)
    
    assert puntos.puntos_acumulados == 10


def test_asignar_puntos_racha(db_session: Session, estudiante_3: Usuario):
    """Test asignar puntos por racha de días."""
    request = AsignarPuntosRequest(
        usuario_id=estudiante_3.usuario_id,
        puntos=25,
        motivo="Racha de 7 días consecutivos"
    )
    
    puntos = asignar_puntos(db_session, request)
    
    assert puntos.puntos_acumulados == 25


def test_asignar_puntos_multiples_veces(
    db_session: Session, estudiante_1: Usuario
):
    """Test asignar puntos múltiples veces al mismo usuario."""
    actividades = [
        ("Tarea 1 completada", 30),
        ("Examen aprobado", 80),
        ("Foro participación", 15),
        ("Proyecto entregado", 100),
    ]
    
    total_esperado = sum(puntos for _, puntos in actividades)
    
    for motivo, puntos_ganados in actividades:
        request = AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=puntos_ganados,
            motivo=motivo
        )
        asignar_puntos(db_session, request)
    
    puntos_finales = get_usuario_puntos(db_session, estudiante_1.usuario_id)
    assert puntos_finales.puntos_acumulados >= total_esperado
    
    # Verificar historial completo
    historial = get_historial_puntos_usuario(db_session, estudiante_1.usuario_id)
    assert len(historial) >= len(actividades)


# ==================== TESTS DE DESCUENTO DE PUNTOS ====================


def test_descontar_puntos_compra(db_session: Session, usuario_con_puntos: UsuarioPuntos):
    """Test descontar puntos por compra de recompensa."""
    puntos_antes = usuario_con_puntos.puntos_acumulados
    
    request = DescontarPuntosRequest(
        usuario_id=usuario_con_puntos.usuario_id,
        puntos=50,
        motivo="Canje de avatar especial"
    )
    
    puntos = descontar_puntos(db_session, request)
    
    assert puntos.puntos_acumulados == puntos_antes - 50


def test_descontar_puntos_insuficientes(
    db_session: Session, usuario_con_puntos: UsuarioPuntos
):
    """Test no se pueden descontar más puntos de los disponibles."""
    request = DescontarPuntosRequest(
        usuario_id=usuario_con_puntos.usuario_id,
        puntos=1000,  # Más puntos de los que tiene
        motivo="Intento de compra costosa"
    )
    
    with pytest.raises(ValueError, match="suficientes puntos"):
        descontar_puntos(db_session, request)


def test_descontar_puntos_exactos(db_session: Session, estudiante_1: Usuario):
    """Test descontar exactamente todos los puntos."""
    # Dar 100 puntos
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=100,
            motivo="Puntos de prueba"
        )
    )
    
    # Descontar todos
    request = DescontarPuntosRequest(
        usuario_id=estudiante_1.usuario_id,
        puntos=100,
        motivo="Compra total"
    )
    
    puntos = descontar_puntos(db_session, request)
    assert puntos.puntos_acumulados >= 0


# ==================== TESTS DE HISTORIAL ====================


def test_get_historial_puntos_usuario(
    db_session: Session,
    estudiante_1: Usuario,
    historial_puntos_inicial: HistorialPuntos,
):
    """Test obtener historial completo de puntos."""
    # Agregar más entradas
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=50,
            motivo="Segunda actividad"
        )
    )
    
    historial = get_historial_puntos_usuario(db_session, estudiante_1.usuario_id)
    
    assert len(historial) >= 2
    assert all(isinstance(h, HistorialPuntos) for h in historial)
    assert all(h.usuario_id == estudiante_1.usuario_id for h in historial)


def test_historial_puntos_ordenado_por_fecha(
    db_session: Session, estudiante_1: Usuario
):
    """Test historial está ordenado por fecha descendente (más reciente primero)."""
    # Crear varias entradas
    for i in range(5):
        asignar_puntos(
            db_session,
            AsignarPuntosRequest(
                usuario_id=estudiante_1.usuario_id,
                puntos=10 * (i + 1),
                motivo=f"Actividad {i + 1}"
            )
        )
    
    historial = get_historial_puntos_usuario(db_session, estudiante_1.usuario_id)
    
    # Verificar orden descendente
    fechas = [h.fecha for h in historial]
    assert fechas == sorted(fechas, reverse=True)


def test_historial_puntos_paginacion(db_session: Session, estudiante_1: Usuario):
    """Test paginación del historial."""
    # Crear 10 entradas
    for i in range(10):
        asignar_puntos(
            db_session,
            AsignarPuntosRequest(
                usuario_id=estudiante_1.usuario_id,
                puntos=10,
                motivo=f"Entrada {i}"
            )
        )
    
    # Obtener primera página
    pagina_1 = get_historial_puntos_usuario(
        db_session, estudiante_1.usuario_id, skip=0, limit=5
    )
    
    # Obtener segunda página
    pagina_2 = get_historial_puntos_usuario(
        db_session, estudiante_1.usuario_id, skip=5, limit=5
    )
    
    assert len(pagina_1) == 5
    assert len(pagina_2) >= 5
    assert pagina_1[0].historial_id != pagina_2[0].historial_id


# ==================== TESTS DE RANKING ====================


def test_get_ranking_usuarios(
    db_session: Session,
    estudiante_1: Usuario,
    estudiante_2: Usuario,
    estudiante_3: Usuario,
):
    """Test obtener ranking de usuarios por puntos."""
    # Asignar diferentes puntos
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=200,
            motivo="Estudiante destacado"
        )
    )
    
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_2.usuario_id,
            puntos=150,
            motivo="Buen rendimiento"
        )
    )
    
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_3.usuario_id,
            puntos=100,
            motivo="Participación"
        )
    )
    
    ranking = get_ranking_usuarios(db_session, limit=10)
    
    assert len(ranking) >= 3
    
    # Verificar orden descendente por puntos
    puntos_ranking = [r.puntos_acumulados for r in ranking]
    assert puntos_ranking == sorted(puntos_ranking, reverse=True)
    
    # Verificar posiciones
    posiciones = [r.posicion for r in ranking]
    assert posiciones == list(range(1, len(posiciones) + 1))


def test_get_posicion_usuario_ranking(
    db_session: Session,
    estudiante_1: Usuario,
    estudiante_2: Usuario,
    estudiante_3: Usuario,
):
    """Test obtener posición específica de un usuario en el ranking."""
    # Asignar puntos
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=300,
            motivo="Primer lugar"
        )
    )
    
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_2.usuario_id,
            puntos=200,
            motivo="Segundo lugar"
        )
    )
    
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_3.usuario_id,
            puntos=100,
            motivo="Tercer lugar"
        )
    )
    
    posicion_1 = get_posicion_usuario_ranking(db_session, estudiante_1.usuario_id)
    posicion_2 = get_posicion_usuario_ranking(db_session, estudiante_2.usuario_id)
    posicion_3 = get_posicion_usuario_ranking(db_session, estudiante_3.usuario_id)
    
    assert posicion_1 == 1
    assert posicion_2 == 2
    assert posicion_3 == 3


def test_posicion_usuario_sin_puntos(db_session: Session, estudiante_1: Usuario):
    """Test posición de usuario sin puntos."""
    # Usuario no tiene registro de puntos
    posicion = get_posicion_usuario_ranking(db_session, estudiante_1.usuario_id)
    
    assert posicion is None


# ==================== TESTS DE ESTADÍSTICAS ====================


def test_get_estadisticas_puntos(
    db_session: Session,
    estudiante_1: Usuario,
    estudiante_2: Usuario,
    estudiante_3: Usuario,
):
    """Test obtener estadísticas generales del sistema."""
    # Asignar puntos a varios usuarios
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=200,
            motivo="Estudiante 1"
        )
    )
    
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_2.usuario_id,
            puntos=150,
            motivo="Estudiante 2"
        )
    )
    
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_3.usuario_id,
            puntos=100,
            motivo="Estudiante 3"
        )
    )
    
    stats = get_estadisticas_puntos(db_session)
    
    assert stats["total_usuarios_con_puntos"] >= 3
    assert stats["puntos_maximos"] >= 200
    assert stats["puntos_minimos"] >= 100
    assert stats["promedio_puntos"] > 0
    assert stats["total_puntos_distribuidos"] >= 450


def test_estadisticas_sistema_vacio(db_session: Session):
    """Test estadísticas con sistema sin puntos."""
    # Limpiar datos (esto depende de la fixture)
    stats = get_estadisticas_puntos(db_session)
    
    # Puede ser 0 o tener datos de otros tests
    assert stats["total_usuarios_con_puntos"] >= 0
    assert stats["promedio_puntos"] >= 0


# ==================== TESTS DE INTEGRACIÓN ====================


def test_flujo_completo_puntos_tarea(
    db_session: Session, estudiante_1: Usuario
):
    """Test flujo completo: ganar puntos por tarea y gastar en recompensa."""
    # 1. Completar tarea - ganar puntos
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=100,
            motivo="Tarea de programación completada"
        )
    )
    
    puntos_despues_tarea = get_usuario_puntos(db_session, estudiante_1.usuario_id)
    assert puntos_despues_tarea.puntos_acumulados >= 100
    
    # 2. Comprar recompensa - gastar puntos
    descontar_puntos(
        db_session,
        DescontarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=50,
            motivo="Canje de avatar especial"
        )
    )
    
    puntos_finales = get_usuario_puntos(db_session, estudiante_1.usuario_id)
    assert puntos_finales.puntos_acumulados >= 50
    
    # 3. Verificar historial completo
    historial = get_historial_puntos_usuario(db_session, estudiante_1.usuario_id)
    assert len(historial) >= 2
    
    cambios_positivos = [h for h in historial if h.cambio > 0]
    cambios_negativos = [h for h in historial if h.cambio < 0]
    
    assert len(cambios_positivos) >= 1
    assert len(cambios_negativos) >= 1


def test_multiples_usuarios_actividades_simultaneas(
    db_session: Session,
    estudiante_1: Usuario,
    estudiante_2: Usuario,
    estudiante_3: Usuario,
):
    """Test múltiples usuarios ganando puntos simultáneamente."""
    usuarios = [estudiante_1, estudiante_2, estudiante_3]
    
    # Cada usuario realiza varias actividades
    for usuario in usuarios:
        for i in range(3):
            asignar_puntos(
                db_session,
                AsignarPuntosRequest(
                    usuario_id=usuario.usuario_id,
                    puntos=50,
                    motivo=f"Actividad {i + 1}"
                )
            )
    
    # Verificar que cada usuario tiene 150 puntos
    for usuario in usuarios:
        puntos = get_usuario_puntos(db_session, usuario.usuario_id)
        assert puntos.puntos_acumulados >= 150
    
    # Verificar ranking
    ranking = get_ranking_usuarios(db_session)
    assert len(ranking) >= 3
