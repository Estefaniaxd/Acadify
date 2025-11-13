import uuid

from sqlalchemy.orm import Session, joinedload

from ...models.gamification.tema import Tema
from ...models.gamification.tema_personalizado import TemaPersonalizado
from ...models.gamification.tema_predefinido import TemaPredefinido
from ...schemas.gamification.tema import (
    AsignarTemaPersonalizadoRequest,
    TemaCreate,
    TemaUpdate,
)


def get_tema(db: Session, tema_id: uuid.UUID) -> Tema | None:
    """Obtener un tema por su ID."""
    return db.query(Tema).filter(Tema.tema_id == tema_id).first()


def get_temas(db: Session, skip: int = 0, limit: int = 100) -> list[Tema]:
    """Obtener lista de todos los temas."""
    return db.query(Tema).order_by(Tema.nombre).offset(skip).limit(limit).all()


def create_tema(db: Session, tema: TemaCreate) -> Tema:
    """Crear un nuevo tema."""
    db_tema = Tema(nombre=tema.nombre, emoji=tema.emoji)
    db.add(db_tema)
    db.commit()
    db.refresh(db_tema)
    return db_tema


def update_tema(
    db: Session, tema_id: uuid.UUID, tema_update: TemaUpdate
) -> Tema | None:
    """Actualizar un tema existente."""
    db_tema = get_tema(db, tema_id)
    if not db_tema:
        return None

    update_data = tema_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tema, field, value)

    db.commit()
    db.refresh(db_tema)
    return db_tema


def delete_tema(db: Session, tema_id: uuid.UUID) -> bool:
    """Eliminar un tema."""
    db_tema = get_tema(db, tema_id)
    if not db_tema:
        return False

    db.delete(db_tema)
    db.commit()
    return True


def get_temas_predefinidos(db: Session) -> list[Tema]:
    """Obtener todos los temas predefinidos."""
    return (
        db.query(Tema)
        .join(TemaPredefinido, Tema.tema_id == TemaPredefinido.tema_id)
        .order_by(Tema.nombre)
        .all()
    )


def create_tema_predefinido(db: Session, tema_id: uuid.UUID) -> TemaPredefinido:
    """Marcar un tema como predefinido."""
    # Verificar que el tema existe
    tema = get_tema(db, tema_id)
    if not tema:
        msg = "El tema no existe"
        raise ValueError(msg)

    # Verificar que no esté ya marcado como predefinido
    existing = (
        db.query(TemaPredefinido).filter(TemaPredefinido.tema_id == tema_id).first()
    )

    if existing:
        msg = "El tema ya está marcado como predefinido"
        raise ValueError(msg)

    db_tema_predefinido = TemaPredefinido(tema_id=tema_id)
    db.add(db_tema_predefinido)
    db.commit()
    db.refresh(db_tema_predefinido)
    return db_tema_predefinido


def remove_tema_predefinido(db: Session, tema_id: uuid.UUID) -> bool:
    """Quitar marca de predefinido de un tema."""
    tema_predefinido = (
        db.query(TemaPredefinido).filter(TemaPredefinido.tema_id == tema_id).first()
    )

    if not tema_predefinido:
        return False

    db.delete(tema_predefinido)
    db.commit()
    return True


def get_temas_personalizados_usuario(
    db: Session, usuario_id: uuid.UUID
) -> list[TemaPersonalizado]:
    """Obtener temas personalizados de un usuario."""
    return (
        db.query(TemaPersonalizado)
        .options(joinedload(TemaPersonalizado.tema))
        .filter(TemaPersonalizado.usuario_id == usuario_id)
        .all()
    )


def get_temas_usuario(db: Session, usuario_id: uuid.UUID) -> dict:
    """Obtener todos los temas disponibles para un usuario (predefinidos + personalizados)."""
    # Temas predefinidos (disponibles para todos)
    temas_predefinidos = get_temas_predefinidos(db)

    # Temas personalizados del usuario
    temas_personalizados_rel = get_temas_personalizados_usuario(db, usuario_id)
    temas_personalizados = [rel.tema for rel in temas_personalizados_rel]

    return {
        "temas_predefinidos": temas_predefinidos,
        "temas_personalizados": temas_personalizados,
        "total_temas": len(temas_predefinidos) + len(temas_personalizados),
    }


def asignar_tema_personalizado(
    db: Session, request: AsignarTemaPersonalizadoRequest
) -> TemaPersonalizado:
    """Asignar un tema personalizado a un usuario."""
    # Verificar que el tema existe
    tema = get_tema(db, request.tema_id)
    if not tema:
        msg = "El tema no existe"
        raise ValueError(msg)

    # Verificar que no esté ya asignado al usuario
    existing = (
        db.query(TemaPersonalizado)
        .filter(
            TemaPersonalizado.usuario_id == request.usuario_id,
            TemaPersonalizado.tema_id == request.tema_id,
        )
        .first()
    )

    if existing:
        msg = "El usuario ya tiene este tema personalizado"
        raise ValueError(msg)

    # Verificar que no sea un tema predefinido
    es_predefinido = (
        db.query(TemaPredefinido)
        .filter(TemaPredefinido.tema_id == request.tema_id)
        .first()
    )

    if es_predefinido:
        msg = "No se puede asignar un tema predefinido como personalizado"
        raise ValueError(msg)

    db_tema_personalizado = TemaPersonalizado(
        usuario_id=request.usuario_id, tema_id=request.tema_id
    )

    db.add(db_tema_personalizado)
    db.commit()
    db.refresh(db_tema_personalizado)
    return db_tema_personalizado


def revocar_tema_personalizado(
    db: Session, usuario_id: uuid.UUID, tema_id: uuid.UUID
) -> bool:
    """Revocar un tema personalizado de un usuario."""
    tema_personalizado = (
        db.query(TemaPersonalizado)
        .filter(
            TemaPersonalizado.usuario_id == usuario_id,
            TemaPersonalizado.tema_id == tema_id,
        )
        .first()
    )

    if not tema_personalizado:
        return False

    db.delete(tema_personalizado)
    db.commit()
    return True


def is_tema_predefinido(db: Session, tema_id: uuid.UUID) -> bool:
    """Verificar si un tema es predefinido."""
    return (
        db.query(TemaPredefinido).filter(TemaPredefinido.tema_id == tema_id).first()
        is not None
    )


def count_usuarios_con_tema(db: Session, tema_id: uuid.UUID) -> int:
    """Contar cuántos usuarios tienen un tema específico (solo temas personalizados)."""
    return (
        db.query(TemaPersonalizado).filter(TemaPersonalizado.tema_id == tema_id).count()
    )
