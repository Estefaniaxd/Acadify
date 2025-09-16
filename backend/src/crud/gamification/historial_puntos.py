import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text

from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.models.gamification.historial_puntos import HistorialPuntos
from src.models.users.usuario import Usuario
from src.schemas.gamification.historial_puntos import (
    AsignarPuntosRequest,
    DescontarPuntosRequest,
)


def get_usuario_puntos(db: Session, usuario_id: uuid.UUID) -> Optional[UsuarioPuntos]:
    """Obtener los puntos de un usuario específico."""
    return (
        db.query(UsuarioPuntos).filter(UsuarioPuntos.usuario_id == usuario_id).first()
    )


def create_usuario_puntos(
    db: Session, usuario_id: uuid.UUID, puntos_iniciales: int = 0
) -> UsuarioPuntos:
    """Crear registro inicial de puntos para un usuario."""
    db_puntos = UsuarioPuntos(usuario_id=usuario_id, puntos_acumulados=puntos_iniciales)
    db.add(db_puntos)
    db.commit()
    db.refresh(db_puntos)
    return db_puntos


def get_or_create_usuario_puntos(db: Session, usuario_id: uuid.UUID) -> UsuarioPuntos:
    """Obtener puntos de usuario o crear registro si no existe."""
    puntos = get_usuario_puntos(db, usuario_id)
    if not puntos:
        puntos = create_usuario_puntos(db, usuario_id)
    return puntos


def asignar_puntos(db: Session, request: AsignarPuntosRequest) -> UsuarioPuntos:
    """Asignar puntos a un usuario y crear historial."""
    # Obtener o crear registro de puntos
    usuario_puntos = get_or_create_usuario_puntos(db, request.usuario_id)

    # Actualizar puntos
    usuario_puntos.puntos_acumulados += request.puntos

    # Crear entrada en historial
    historial = HistorialPuntos(
        usuario_id=request.usuario_id, cambio=request.puntos, motivo=request.motivo
    )

    db.add(historial)
    db.commit()
    db.refresh(usuario_puntos)

    return usuario_puntos


def descontar_puntos(db: Session, request: DescontarPuntosRequest) -> UsuarioPuntos:
    """Descontar puntos a un usuario y crear historial."""
    # Obtener puntos actuales
    usuario_puntos = get_or_create_usuario_puntos(db, request.usuario_id)

    # Verificar que tenga suficientes puntos
    if usuario_puntos.puntos_acumulados < request.puntos:
        raise ValueError("El usuario no tiene suficientes puntos")

    # Descontar puntos
    usuario_puntos.puntos_acumulados -= request.puntos

    # Crear entrada en historial (cambio negativo)
    historial = HistorialPuntos(
        usuario_id=request.usuario_id, cambio=-request.puntos, motivo=request.motivo
    )

    db.add(historial)
    db.commit()
    db.refresh(usuario_puntos)

    return usuario_puntos


def get_historial_puntos_usuario(
    db: Session, usuario_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[HistorialPuntos]:
    """Obtener historial de puntos de un usuario."""
    return (
        db.query(HistorialPuntos)
        .filter(HistorialPuntos.usuario_id == usuario_id)
        .order_by(desc(HistorialPuntos.fecha))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_ranking_usuarios(db: Session, skip: int = 0, limit: int = 50) -> List[dict]:
    """Obtener ranking de usuarios por puntos."""
    query = (
        db.query(
            UsuarioPuntos.usuario_id,
            UsuarioPuntos.puntos_acumulados,
            Usuario.nombres,
            Usuario.apellidos,
            func.row_number()
            .over(order_by=desc(UsuarioPuntos.puntos_acumulados))
            .label("posicion"),
        )
        .join(Usuario, UsuarioPuntos.usuario_id == Usuario.usuario_id)
        .filter(UsuarioPuntos.puntos_acumulados > 0)
        .order_by(desc(UsuarioPuntos.puntos_acumulados))
        .offset(skip)
        .limit(limit)
    )

    return query.all()


def get_estadisticas_puntos(db: Session) -> dict:
    """Obtener estadísticas generales del sistema de puntos."""
    stats = (
        db.query(
            func.count(UsuarioPuntos.usuario_id).label("total_usuarios"),
            func.avg(UsuarioPuntos.puntos_acumulados).label("promedio_puntos"),
            func.max(UsuarioPuntos.puntos_acumulados).label("puntos_maximos"),
            func.min(UsuarioPuntos.puntos_acumulados).label("puntos_minimos"),
            func.sum(UsuarioPuntos.puntos_acumulados).label("total_puntos"),
        )
        .filter(UsuarioPuntos.puntos_acumulados > 0)
        .first()
    )

    return {
        "total_usuarios_con_puntos": stats.total_usuarios or 0,
        "promedio_puntos": float(stats.promedio_puntos or 0),
        "puntos_maximos": stats.puntos_maximos or 0,
        "puntos_minimos": stats.puntos_minimos or 0,
        "total_puntos_distribuidos": stats.total_puntos or 0,
    }


def get_posicion_usuario_ranking(db: Session, usuario_id: uuid.UUID) -> Optional[int]:
    """Obtener la posición de un usuario en el ranking."""
    usuario_puntos = get_usuario_puntos(db, usuario_id)
    if not usuario_puntos:
        return None

    posicion = (
        db.query(func.count(UsuarioPuntos.usuario_id).label("posicion"))
        .filter(UsuarioPuntos.puntos_acumulados > usuario_puntos.puntos_acumulados)
        .scalar()
    )

    return posicion + 1 if posicion is not None else 1
