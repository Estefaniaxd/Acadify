"""Tests comprehensivos del sistema de recompensas."""

import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from src.models.users.usuario import Usuario
from src.models.gamification.recompensa import Recompensa
from src.models.gamification.usuario_recompensa import UsuarioRecompensa
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.crud.gamification.recompensas import (
    get_recompensa,
    get_recompensas,
    create_recompensa,
    update_recompensa,
    delete_recompensa,
    get_recompensas_disponibles_usuario,
    canjear_recompensa,
    get_canjes_usuario,
    get_estadisticas_canjes_usuario,
    get_recompensas_con_estadisticas,
)
from src.crud.gamification.historial_puntos import asignar_puntos
from src.schemas.gamification.recompensa import (
    RecompensaCreate,
    RecompensaUpdate,
    CanjearRecompensaRequest,
)
from src.schemas.gamification.historial_puntos import AsignarPuntosRequest
from src.enums.gamification.recompensa_enums import TipoRecompensa


# ==================== TESTS DE CRUD BÁSICO ====================


def test_create_recompensa(db_session: Session):
    """Test crear nueva recompensa."""
    recompensa_data = RecompensaCreate(
        nombre="Foto de Portada Especial",
        descripcion="Foto de portada personalizada para el perfil",
        costo_puntos=75,
        tipo=TipoRecompensa.foto_portada
    )
    
    recompensa = create_recompensa(db_session, recompensa_data)
    
    assert recompensa is not None
    assert recompensa.nombre == "Foto de Portada Especial"
    assert recompensa.costo_puntos == 75
    assert recompensa.tipo == TipoRecompensa.foto_portada


def test_get_recompensa_existente(db_session: Session, recompensa_basica: Recompensa):
    """Test obtener recompensa por ID."""
    recompensa = get_recompensa(db_session, recompensa_basica.recompensa_id)
    
    assert recompensa is not None
    assert recompensa.recompensa_id == recompensa_basica.recompensa_id
    assert recompensa.nombre == recompensa_basica.nombre


def test_get_recompensa_no_existente(db_session: Session):
    """Test obtener recompensa que no existe."""
    recompensa = get_recompensa(db_session, uuid4())
    
    assert recompensa is None


def test_get_recompensas_lista(
    db_session: Session,
    recompensa_basica: Recompensa,
    recompensa_premium: Recompensa,
    recompensa_titulo: Recompensa,
):
    """Test obtener lista de todas las recompensas."""
    recompensas = get_recompensas(db_session, limit=10)
    
    assert len(recompensas) >= 3
    
    # Verificar que están ordenadas por costo
    costos = [r.costo_puntos for r in recompensas]
    assert costos == sorted(costos)


def test_update_recompensa(db_session: Session, recompensa_basica: Recompensa):
    """Test actualizar recompensa existente."""
    update_data = RecompensaUpdate(
        nombre="Avatar Especial Actualizado",
        costo_puntos=60
    )
    
    recompensa = update_recompensa(
        db_session,
        recompensa_basica.recompensa_id,
        update_data
    )
    
    assert recompensa is not None
    assert recompensa.nombre == "Avatar Especial Actualizado"
    assert recompensa.costo_puntos == 60
    assert recompensa.descripcion == recompensa_basica.descripcion  # No cambió


def test_update_recompensa_no_existente(db_session: Session):
    """Test actualizar recompensa que no existe."""
    update_data = RecompensaUpdate(nombre="Inexistente")
    
    recompensa = update_recompensa(db_session, uuid4(), update_data)
    
    assert recompensa is None


def test_delete_recompensa(db_session: Session, recompensa_titulo: Recompensa):
    """Test eliminar recompensa."""
    deleted = delete_recompensa(db_session, recompensa_titulo.recompensa_id)
    
    assert deleted is True
    
    # Verificar que ya no existe
    recompensa = get_recompensa(db_session, recompensa_titulo.recompensa_id)
    assert recompensa is None


def test_delete_recompensa_no_existente(db_session: Session):
    """Test eliminar recompensa que no existe."""
    deleted = delete_recompensa(db_session, uuid4())
    
    assert deleted is False


# ==================== TESTS DE DISPONIBILIDAD ====================


def test_get_recompensas_disponibles_sin_puntos(
    db_session: Session,
    estudiante_1: Usuario,
    recompensa_basica: Recompensa,
    recompensa_premium: Recompensa,
):
    """Test ver recompensas cuando usuario no tiene puntos."""
    disponibles = get_recompensas_disponibles_usuario(
        db_session,
        estudiante_1.usuario_id
    )
    
    assert len(disponibles) >= 2
    
    # Ninguna debería estar disponible
    for item in disponibles:
        assert item["puede_canjear"] is False
        assert item["puntos_faltantes"] > 0


def test_get_recompensas_disponibles_con_puntos(
    db_session: Session,
    usuario_con_puntos: UsuarioPuntos,
    recompensa_basica: Recompensa,
    recompensa_premium: Recompensa,
):
    """Test ver recompensas con puntos suficientes para algunas."""
    disponibles = get_recompensas_disponibles_usuario(
        db_session,
        usuario_con_puntos.usuario_id
    )
    
    # Usuario tiene 100 puntos
    # recompensa_basica cuesta 50 - debería poder canjear
    # recompensa_premium cuesta 200 - no puede canjear
    
    basica_item = next(
        (item for item in disponibles if item["recompensa"].recompensa_id == recompensa_basica.recompensa_id),
        None
    )
    premium_item = next(
        (item for item in disponibles if item["recompensa"].recompensa_id == recompensa_premium.recompensa_id),
        None
    )
    
    assert basica_item is not None
    assert basica_item["puede_canjear"] is True
    assert basica_item["puntos_faltantes"] == 0
    
    assert premium_item is not None
    assert premium_item["puede_canjear"] is False
    assert premium_item["puntos_faltantes"] == 100  # 200 - 100


def test_recompensas_disponibles_calculo_correcto(
    db_session: Session,
    estudiante_1: Usuario,
    recompensa_basica: Recompensa,
):
    """Test cálculo correcto de puntos faltantes."""
    # Dar exactamente 30 puntos (recompensa cuesta 50)
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=30,
            motivo="Puntos de prueba"
        )
    )
    
    disponibles = get_recompensas_disponibles_usuario(
        db_session,
        estudiante_1.usuario_id
    )
    
    basica_item = next(
        (item for item in disponibles if item["recompensa"].recompensa_id == recompensa_basica.recompensa_id),
        None
    )
    
    assert basica_item is not None
    assert basica_item["puede_canjear"] is False
    assert basica_item["puntos_faltantes"] == 20  # 50 - 30


# ==================== TESTS DE CANJE ====================


def test_canjear_recompensa_exitoso(
    db_session: Session,
    usuario_con_puntos: UsuarioPuntos,
    recompensa_basica: Recompensa,
):
    """Test canjear recompensa con puntos suficientes."""
    puntos_antes = usuario_con_puntos.puntos_acumulados
    
    request = CanjearRecompensaRequest(
        usuario_id=usuario_con_puntos.usuario_id,
        recompensa_id=recompensa_basica.recompensa_id
    )
    
    canje = canjear_recompensa(db_session, request)
    
    assert canje is not None
    assert canje.usuario_id == usuario_con_puntos.usuario_id
    assert canje.recompensa_id == recompensa_basica.recompensa_id
    assert canje.fecha_canje is not None
    
    # Verificar descuento de puntos
    db_session.refresh(usuario_con_puntos)
    assert usuario_con_puntos.puntos_acumulados == puntos_antes - recompensa_basica.costo_puntos


def test_canjear_recompensa_puntos_insuficientes(
    db_session: Session,
    usuario_con_puntos: UsuarioPuntos,
    recompensa_premium: Recompensa,
):
    """Test no se puede canjear recompensa sin puntos suficientes."""
    request = CanjearRecompensaRequest(
        usuario_id=usuario_con_puntos.usuario_id,
        recompensa_id=recompensa_premium.recompensa_id  # Cuesta 200, usuario tiene 100
    )
    
    with pytest.raises(ValueError, match="Puntos insuficientes"):
        canjear_recompensa(db_session, request)


def test_canjear_recompensa_no_existente(
    db_session: Session,
    usuario_con_puntos: UsuarioPuntos,
):
    """Test no se puede canjear recompensa que no existe."""
    request = CanjearRecompensaRequest(
        usuario_id=usuario_con_puntos.usuario_id,
        recompensa_id=uuid4()
    )
    
    with pytest.raises(ValueError, match="no existe"):
        canjear_recompensa(db_session, request)


def test_canjear_recompensa_usuario_sin_puntos(
    db_session: Session,
    estudiante_2: Usuario,
    recompensa_basica: Recompensa,
):
    """Test usuario sin registro de puntos no puede canjear."""
    request = CanjearRecompensaRequest(
        usuario_id=estudiante_2.usuario_id,
        recompensa_id=recompensa_basica.recompensa_id
    )
    
    with pytest.raises(ValueError, match="insuficientes"):
        canjear_recompensa(db_session, request)


def test_canjear_multiples_recompensas(
    db_session: Session,
    estudiante_1: Usuario,
    recompensa_basica: Recompensa,
    recompensa_titulo: Recompensa,
):
    """Test canjear varias recompensas seguidas."""
    # Dar suficientes puntos
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=300,
            motivo="Puntos para múltiples canjes"
        )
    )
    
    # Canjear primera recompensa
    canje_1 = canjear_recompensa(
        db_session,
        CanjearRecompensaRequest(
            usuario_id=estudiante_1.usuario_id,
            recompensa_id=recompensa_basica.recompensa_id
        )
    )
    
    # Canjear segunda recompensa
    canje_2 = canjear_recompensa(
        db_session,
        CanjearRecompensaRequest(
            usuario_id=estudiante_1.usuario_id,
            recompensa_id=recompensa_titulo.recompensa_id
        )
    )
    
    assert canje_1 is not None
    assert canje_2 is not None
    
    # Verificar canjes en historial
    canjes = get_canjes_usuario(db_session, estudiante_1.usuario_id)
    assert len(canjes) >= 2


# ==================== TESTS DE HISTORIAL DE CANJES ====================


def test_get_canjes_usuario_vacio(db_session: Session, estudiante_1: Usuario):
    """Test obtener canjes de usuario sin canjes."""
    canjes = get_canjes_usuario(db_session, estudiante_1.usuario_id)
    
    assert len(canjes) == 0


def test_get_canjes_usuario_con_canjes(
    db_session: Session,
    usuario_con_puntos: UsuarioPuntos,
    recompensa_basica: Recompensa,
):
    """Test obtener historial de canjes."""
    # Realizar canje
    canjear_recompensa(
        db_session,
        CanjearRecompensaRequest(
            usuario_id=usuario_con_puntos.usuario_id,
            recompensa_id=recompensa_basica.recompensa_id
        )
    )
    
    canjes = get_canjes_usuario(db_session, usuario_con_puntos.usuario_id)
    
    assert len(canjes) >= 1
    assert canjes[0].recompensa is not None
    assert canjes[0].recompensa.recompensa_id == recompensa_basica.recompensa_id


def test_canjes_ordenados_por_fecha(
    db_session: Session,
    estudiante_1: Usuario,
    recompensa_basica: Recompensa,
    recompensa_titulo: Recompensa,
):
    """Test canjes están ordenados por fecha descendente."""
    # Dar puntos
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=300,
            motivo="Puntos para canjes"
        )
    )
    
    # Realizar varios canjes
    for recompensa in [recompensa_basica, recompensa_titulo]:
        canjear_recompensa(
            db_session,
            CanjearRecompensaRequest(
                usuario_id=estudiante_1.usuario_id,
                recompensa_id=recompensa.recompensa_id
            )
        )
    
    canjes = get_canjes_usuario(db_session, estudiante_1.usuario_id)
    
    fechas = [c.fecha_canje for c in canjes]
    assert fechas == sorted(fechas, reverse=True)


# ==================== TESTS DE ESTADÍSTICAS ====================


def test_get_estadisticas_canjes_usuario_sin_canjes(
    db_session: Session,
    estudiante_1: Usuario,
):
    """Test estadísticas de usuario sin canjes."""
    stats = get_estadisticas_canjes_usuario(db_session, estudiante_1.usuario_id)
    
    assert stats["total_canjes"] == 0
    assert stats["puntos_gastados_total"] == 0
    assert len(stats["canjes"]) == 0


def test_get_estadisticas_canjes_usuario_con_canjes(
    db_session: Session,
    estudiante_1: Usuario,
    recompensa_basica: Recompensa,
    recompensa_titulo: Recompensa,
):
    """Test estadísticas de usuario con canjes."""
    # Dar puntos
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=300,
            motivo="Puntos para canjes"
        )
    )
    
    # Realizar canjes
    canjear_recompensa(
        db_session,
        CanjearRecompensaRequest(
            usuario_id=estudiante_1.usuario_id,
            recompensa_id=recompensa_basica.recompensa_id
        )
    )
    
    canjear_recompensa(
        db_session,
        CanjearRecompensaRequest(
            usuario_id=estudiante_1.usuario_id,
            recompensa_id=recompensa_titulo.recompensa_id
        )
    )
    
    stats = get_estadisticas_canjes_usuario(db_session, estudiante_1.usuario_id)
    
    assert stats["total_canjes"] >= 2
    assert stats["puntos_gastados_total"] == (
        recompensa_basica.costo_puntos + recompensa_titulo.costo_puntos
    )


def test_get_recompensas_con_estadisticas(
    db_session: Session,
    estudiante_1: Usuario,
    estudiante_2: Usuario,
    recompensa_basica: Recompensa,
    recompensa_premium: Recompensa,
):
    """Test estadísticas globales de recompensas."""
    # Dar puntos a ambos usuarios
    for estudiante in [estudiante_1, estudiante_2]:
        asignar_puntos(
            db_session,
            AsignarPuntosRequest(
                usuario_id=estudiante.usuario_id,
                puntos=100,
                motivo="Puntos de prueba"
            )
        )
    
    # Ambos canjean la recompensa básica
    for estudiante in [estudiante_1, estudiante_2]:
        canjear_recompensa(
            db_session,
            CanjearRecompensaRequest(
                usuario_id=estudiante.usuario_id,
                recompensa_id=recompensa_basica.recompensa_id
            )
        )
    
    stats = get_recompensas_con_estadisticas(db_session)
    
    # Encontrar stats de recompensa_basica
    basica_stats = next(
        (s for s in stats if s["recompensa"].recompensa_id == recompensa_basica.recompensa_id),
        None
    )
    
    assert basica_stats is not None
    assert basica_stats["total_canjes"] >= 2
    assert basica_stats["puntos_gastados_total"] >= recompensa_basica.costo_puntos * 2
    
    # Recompensa premium no debería tener canjes
    premium_stats = next(
        (s for s in stats if s["recompensa"].recompensa_id == recompensa_premium.recompensa_id),
        None
    )
    
    if premium_stats:
        assert premium_stats["total_canjes"] == 0


# ==================== TESTS DE INTEGRACIÓN ====================


def test_flujo_completo_ganar_y_canjear_recompensa(
    db_session: Session,
    estudiante_1: Usuario,
    recompensa_basica: Recompensa,
):
    """Test flujo completo: ganar puntos y canjear recompensa."""
    # 1. Ganar puntos por actividades
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=100,
            motivo="Completar tarea"
        )
    )
    
    # 2. Ver recompensas disponibles
    disponibles = get_recompensas_disponibles_usuario(
        db_session,
        estudiante_1.usuario_id
    )
    
    basica_disponible = next(
        (item for item in disponibles if item["recompensa"].recompensa_id == recompensa_basica.recompensa_id),
        None
    )
    
    assert basica_disponible["puede_canjear"] is True
    
    # 3. Canjear recompensa
    canje = canjear_recompensa(
        db_session,
        CanjearRecompensaRequest(
            usuario_id=estudiante_1.usuario_id,
            recompensa_id=recompensa_basica.recompensa_id
        )
    )
    
    assert canje is not None
    
    # 4. Verificar historial
    canjes = get_canjes_usuario(db_session, estudiante_1.usuario_id)
    assert len(canjes) >= 1
    
    # 5. Verificar estadísticas
    stats = get_estadisticas_canjes_usuario(db_session, estudiante_1.usuario_id)
    assert stats["total_canjes"] >= 1
    assert stats["puntos_gastados_total"] >= recompensa_basica.costo_puntos


def test_multiples_usuarios_canjeando_misma_recompensa(
    db_session: Session,
    estudiante_1: Usuario,
    estudiante_2: Usuario,
    estudiante_3: Usuario,
    recompensa_basica: Recompensa,
):
    """Test varios usuarios canjeando la misma recompensa."""
    usuarios = [estudiante_1, estudiante_2, estudiante_3]
    
    # Dar puntos a todos
    for usuario in usuarios:
        asignar_puntos(
            db_session,
            AsignarPuntosRequest(
                usuario_id=usuario.usuario_id,
                puntos=100,
                motivo="Puntos iniciales"
            )
        )
    
    # Todos canjean la misma recompensa
    for usuario in usuarios:
        canje = canjear_recompensa(
            db_session,
            CanjearRecompensaRequest(
                usuario_id=usuario.usuario_id,
                recompensa_id=recompensa_basica.recompensa_id
            )
        )
        assert canje is not None
    
    # Verificar estadísticas globales
    stats = get_recompensas_con_estadisticas(db_session)
    basica_stats = next(
        (s for s in stats if s["recompensa"].recompensa_id == recompensa_basica.recompensa_id),
        None
    )
    
    assert basica_stats["total_canjes"] >= 3
