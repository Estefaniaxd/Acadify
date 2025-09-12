import uuid
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc

from src.models.gamification.insignia import Insignia
from src.models.gamification.usuario_insignia import UsuarioInsignia
from src.models.users.usuario import Usuario
from src.schemas.gamificacion.insignias import (
    InsigniaCreate,
    InsigniaUpdate,
    UsuarioInsigniaCreate,
    OtorgarInsigniaRequest
)


def get_insignia(db: Session, insignia_id: uuid.UUID) -> Optional[Insignia]:
    """Obtener una insignia por su ID."""
    return db.query(Insignia).filter(
        Insignia.insignia_id == insignia_id
    ).first()


def get_insignias(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    activas_solo: bool = False
) -> List[Insignia]:
    """Obtener lista de insignias."""
    query = db.query(Insignia)
    
    return query.order_by(Insignia.nombre).offset(skip).limit(limit).all()


def create_insignia(db: Session, insignia: InsigniaCreate) -> Insignia:
    """Crear una nueva insignia."""
    db_insignia = Insignia(
        nombre=insignia.nombre,
        descripcion=insignia.descripcion,
        imagen_url=insignia.imagen_url,
        tipo=insignia.tipo,
        es_unica=insignia.es_unica
    )
    db.add(db_insignia)
    db.commit()
    db.refresh(db_insignia)
    return db_insignia


def update_insignia(
    db: Session, 
    insignia_id: uuid.UUID, 
    insignia_update: InsigniaUpdate
) -> Optional[Insignia]:
    """Actualizar una insignia existente."""
    db_insignia = get_insignia(db, insignia_id)
    if not db_insignia:
        return None
    
    update_data = insignia_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_insignia, field, value)
    
    db.commit()
    db.refresh(db_insignia)
    return db_insignia


def delete_insignia(db: Session, insignia_id: uuid.UUID) -> bool:
    """Eliminar una insignia."""
    db_insignia = get_insignia(db, insignia_id)
    if not db_insignia:
        return False
    
    db.delete(db_insignia)
    db.commit()
    return True


def get_usuario_insignia(
    db: Session, 
    usuario_id: uuid.UUID, 
    insignia_id: uuid.UUID
) -> Optional[UsuarioInsignia]:
    """Verificar si un usuario tiene una insignia específica."""
    return db.query(UsuarioInsignia).filter(
        UsuarioInsignia.usuario_id == usuario_id,
        UsuarioInsignia.insignia_id == insignia_id
    ).first()


def get_insignias_usuario(
    db: Session,
    usuario_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> List[UsuarioInsignia]:
    """Obtener todas las insignias de un usuario."""
    return db.query(UsuarioInsignia).options(
        joinedload(UsuarioInsignia.insignia)
    ).filter(
        UsuarioInsignia.usuario_id == usuario_id
    ).order_by(desc(UsuarioInsignia.fecha_otorgada)).offset(skip).limit(limit).all()


def otorgar_insignia(db: Session, request: OtorgarInsigniaRequest) -> UsuarioInsignia:
    """Otorgar una insignia a un usuario."""
    # Verificar que la insignia existe
    insignia = get_insignia(db, request.insignia_id)
    if not insignia:
        raise ValueError("La insignia no existe")
    
    # Verificar si el usuario ya tiene la insignia
    if insignia.es_unica:
        existing = get_usuario_insignia(db, request.usuario_id, request.insignia_id)
        if existing:
            raise ValueError("El usuario ya tiene esta insignia única")
    
    # Crear la asignación
    db_usuario_insignia = UsuarioInsignia(
        usuario_id=request.usuario_id,
        insignia_id=request.insignia_id,
        otorgada_por=request.otorgada_por
    )
    
    db.add(db_usuario_insignia)
    db.commit()
    db.refresh(db_usuario_insignia)
    
    return db_usuario_insignia


def revocar_insignia(
    db: Session, 
    usuario_id: uuid.UUID, 
    insignia_id: uuid.UUID
) -> bool:
    """Revocar una insignia de un usuario."""
    usuario_insignia = get_usuario_insignia(db, usuario_id, insignia_id)
    if not usuario_insignia:
        return False
    
    db.delete(usuario_insignia)
    db.commit()
    return True


def get_insignias_con_estadisticas(db: Session) -> List[dict]:
    """Obtener insignias con estadísticas de uso."""
    query = db.query(
        Insignia,
        func.count(UsuarioInsignia.usuario_id).label('total_usuarios')
    ).outerjoin(
        UsuarioInsignia, Insignia.insignia_id == UsuarioInsignia.insignia_id
    ).group_by(
        Insignia.insignia_id
    ).order_by(desc('total_usuarios'))
    
    # Obtener total de usuarios para calcular porcentajes
    total_usuarios = db.query(func.count(Usuario.usuario_id)).scalar()
    
    results = []
    for insignia, total_usuarios_con_insignia in query.all():
        porcentaje = (total_usuarios_con_insignia / total_usuarios * 100) if total_usuarios > 0 else 0
        results.append({
            'insignia': insignia,
            'total_usuarios_con_insignia': total_usuarios_con_insignia,
            'porcentaje_usuarios': round(porcentaje, 2)
        })
    
    return results


def get_usuarios_con_insignia(
    db: Session,
    insignia_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> List[UsuarioInsignia]:
    """Obtener usuarios que tienen una insignia específica."""
    return db.query(UsuarioInsignia).options(
        joinedload(UsuarioInsignia.usuario)
    ).filter(
        UsuarioInsignia.insignia_id == insignia_id
    ).order_by(desc(UsuarioInsignia.fecha_otorgada)).offset(skip).limit(limit).all()


def count_insignias_usuario(db: Session, usuario_id: uuid.UUID) -> int:
    """Contar el total de insignias de un usuario."""
    return db.query(UsuarioInsignia).filter(
        UsuarioInsignia.usuario_id == usuario_id
    ).count()