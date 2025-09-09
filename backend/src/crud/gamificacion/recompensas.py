import uuid
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc

from src.models.gamification.recompensa import Recompensa
from src.models.gamification.usuario_recompensa import UsuarioRecompensa
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.schemas.gamificacion.recompensas import (
    RecompensaCreate,
    RecompensaUpdate,
    CanjearRecompensaRequest
)


def get_recompensa(db: Session, recompensa_id: uuid.UUID) -> Optional[Recompensa]:
    """Obtener una recompensa por su ID."""
    return db.query(Recompensa).filter(
        Recompensa.recompensa_id == recompensa_id
    ).first()


def get_recompensas(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Recompensa]:
    """Obtener lista de recompensas."""
    return db.query(Recompensa).order_by(
        Recompensa.costo_puntos
    ).offset(skip).limit(limit).all()


def create_recompensa(db: Session, recompensa: RecompensaCreate) -> Recompensa:
    """Crear una nueva recompensa."""
    db_recompensa = Recompensa(
        nombre=recompensa.nombre,
        descripcion=recompensa.descripcion,
        costo_puntos=recompensa.costo_puntos,
        tipo=recompensa.tipo
    )
    db.add(db_recompensa)
    db.commit()
    db.refresh(db_recompensa)
    return db_recompensa


def update_recompensa(
    db: Session,
    recompensa_id: uuid.UUID,
    recompensa_update: RecompensaUpdate
) -> Optional[Recompensa]:
    """Actualizar una recompensa existente."""
    db_recompensa = get_recompensa(db, recompensa_id)
    if not db_recompensa:
        return None
    
    update_data = recompensa_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_recompensa, field, value)
    
    db.commit()
    db.refresh(db_recompensa)
    return db_recompensa


def delete_recompensa(db: Session, recompensa_id: uuid.UUID) -> bool:
    """Eliminar una recompensa."""
    db_recompensa = get_recompensa(db, recompensa_id)
    if not db_recompensa:
        return False
    
    db.delete(db_recompensa)
    db.commit()
    return True


def get_recompensas_disponibles_usuario(
    db: Session,
    usuario_id: uuid.UUID
) -> List[dict]:
    """Obtener recompensas disponibles para un usuario con su estado de disponibilidad."""
    # Obtener puntos del usuario
    usuario_puntos = db.query(UsuarioPuntos).filter(
        UsuarioPuntos.usuario_id == usuario_id
    ).first()
    
    puntos_usuario = usuario_puntos.puntos_acumulados if usuario_puntos else 0
    
    # Obtener todas las recompensas
    recompensas = get_recompensas(db)
    
    resultado = []
    for recompensa in recompensas:
        puede_canjear = puntos_usuario >= recompensa.costo_puntos
        puntos_faltantes = max(0, recompensa.costo_puntos - puntos_usuario)
        
        resultado.append({
            'recompensa': recompensa,
            'puede_canjear': puede_canjear,
            'puntos_faltantes': puntos_faltantes
        })
    
    return resultado


def canjear_recompensa(db: Session, request: CanjearRecompensaRequest) -> UsuarioRecompensa:
    """Canjear una recompensa por puntos."""
    # Verificar que la recompensa existe
    recompensa = get_recompensa(db, request.recompensa_id)
    if not recompensa:
        raise ValueError("La recompensa no existe")
    
    # Verificar que el usuario tiene suficientes puntos
    usuario_puntos = db.query(UsuarioPuntos).filter(
        UsuarioPuntos.usuario_id == request.usuario_id
    ).first()
    
    if not usuario_puntos or usuario_puntos.puntos_acumulados < recompensa.costo_puntos:
        raise ValueError("Puntos insuficientes para canjear esta recompensa")
    
    # Descontar puntos
    usuario_puntos.puntos_acumulados -= recompensa.costo_puntos
    
    # Crear registro de canje
    db_usuario_recompensa = UsuarioRecompensa(
        usuario_id=request.usuario_id,
        recompensa_id=request.recompensa_id
    )
    
    db.add(db_usuario_recompensa)
    db.commit()
    db.refresh(db_usuario_recompensa)
    
    return db_usuario_recompensa


def get_canjes_usuario(
    db: Session,
    usuario_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> List[UsuarioRecompensa]:
    """Obtener historial de canjes de un usuario."""
    return db.query(UsuarioRecompensa).options(
        joinedload(UsuarioRecompensa.recompensa)
    ).filter(
        UsuarioRecompensa.usuario_id == usuario_id
    ).order_by(desc(UsuarioRecompensa.fecha_canje)).offset(skip).limit(limit).all()


def get_estadisticas_canjes_usuario(db: Session, usuario_id: uuid.UUID) -> dict:
    """Obtener estadísticas de canjes de un usuario."""
    canjes = db.query(UsuarioRecompensa).options(
        joinedload(UsuarioRecompensa.recompensa)
    ).filter(
        UsuarioRecompensa.usuario_id == usuario_id
    ).all()
    
    total_canjes = len(canjes)
    puntos_gastados = sum(canje.recompensa.costo_puntos for canje in canjes)
    
    return {
        'total_canjes': total_canjes,
        'puntos_gastados_total': puntos_gastados,
        'canjes': canjes
    }


def get_recompensas_con_estadisticas(db: Session) -> List[dict]:
    """Obtener recompensas con estadísticas de canjes."""
    query = db.query(
        Recompensa,
        func.count(UsuarioRecompensa.usuario_recompensa_id).label('total_canjes'),
        func.sum(Recompensa.costo_puntos).label('puntos_gastados')
    ).outerjoin(
        UsuarioRecompensa, Recompensa.recompensa_id == UsuarioRecompensa.recompensa_id
    ).group_by(
        Recompensa.recompensa_id
    ).order_by(desc('total_canjes'))
    
    results = []
    for recompensa, total_canjes, puntos_gastados in query.all():
        results.append({
            'recompensa': recompensa,
            'total_canjes': total_canjes or 0,
            'puntos_gastados_total': puntos_gastados or 0
        })
    
    return results