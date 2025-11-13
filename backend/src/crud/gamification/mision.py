"""CRUD operations para el sistema de misiones."""
import uuid
from datetime import datetime, timedelta

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session, joinedload

from src.enums.gamification.mision_enums import (
    EstadoMision,
    FrecuenciaMision,
)
from src.models.gamification.mision import Mision
from src.models.gamification.mision_usuario import MisionUsuario
from src.schemas.gamification.mision import (
    MisionCreate,
    MisionUpdate,
    MisionUsuarioCreate,
    MisionUsuarioUpdate,
)


# ==================== CRUD Misiones ====================
def get_mision(db: Session, mision_id: uuid.UUID) -> Mision | None:
    """Obtener una misión por su ID."""
    return db.query(Mision).filter(Mision.mision_id == mision_id).first()


def get_misiones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    activas_solo: bool = True,
    frecuencia: FrecuenciaMision | None = None,
) -> list[Mision]:
    """Obtener lista de misiones."""
    query = db.query(Mision)

    if activas_solo:
        query = query.filter(Mision.es_activa == True)  # noqa: E712

    if frecuencia:
        query = query.filter(Mision.frecuencia == frecuencia)

    return (
        query.order_by(Mision.orden_visualizacion, Mision.nombre)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_mision(db: Session, mision: MisionCreate) -> Mision:
    """Crear una nueva misión."""
    db_mision = Mision(
        nombre=mision.nombre,
        descripcion=mision.descripcion,
        icono=mision.icono,
        tipo=mision.tipo,
        frecuencia=mision.frecuencia,
        dificultad=mision.dificultad,
        objetivo=mision.objetivo,
        unidad=mision.unidad,
        puntos_recompensa=mision.puntos_recompensa,
        experiencia_recompensa=mision.experiencia_recompensa,
        recompensas_extra=mision.recompensas_extra,
        es_activa=mision.es_activa,
        requisitos=mision.requisitos,
        orden_visualizacion=mision.orden_visualizacion,
    )
    db.add(db_mision)
    db.commit()
    db.refresh(db_mision)
    return db_mision


def update_mision(
    db: Session, mision_id: uuid.UUID, mision_update: MisionUpdate
) -> Mision | None:
    """Actualizar una misión existente."""
    db_mision = get_mision(db, mision_id)
    if not db_mision:
        return None

    update_data = mision_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_mision, field, value)

    db.commit()
    db.refresh(db_mision)
    return db_mision


def delete_mision(db: Session, mision_id: uuid.UUID) -> bool:
    """Eliminar una misión (soft delete)."""
    db_mision = get_mision(db, mision_id)
    if not db_mision:
        return False

    db_mision.es_activa = False
    db.commit()
    return True


# ==================== CRUD MisionesUsuario ====================
def get_mision_usuario(
    db: Session, mision_usuario_id: uuid.UUID
) -> MisionUsuario | None:
    """Obtener una misión de usuario por su ID."""
    return (
        db.query(MisionUsuario)
        .options(joinedload(MisionUsuario.mision))
        .filter(MisionUsuario.mision_usuario_id == mision_usuario_id)
        .first()
    )


def get_misiones_usuario(
    db: Session,
    usuario_id: uuid.UUID,
    estado: EstadoMision | None = None,
    frecuencia: FrecuenciaMision | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[MisionUsuario]:
    """Obtener misiones de un usuario."""
    query = (
        db.query(MisionUsuario)
        .options(joinedload(MisionUsuario.mision))
        .filter(MisionUsuario.usuario_id == usuario_id)
    )

    if estado:
        query = query.filter(MisionUsuario.estado == estado)

    if frecuencia:
        query = query.join(Mision).filter(Mision.frecuencia == frecuencia)

    return (
        query.order_by(desc(MisionUsuario.fecha_asignacion))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_misiones_disponibles(
    db: Session, usuario_id: uuid.UUID, frecuencia: FrecuenciaMision | None = None
) -> list[MisionUsuario]:
    """Obtener misiones disponibles para el usuario."""
    query = (
        db.query(MisionUsuario)
        .options(joinedload(MisionUsuario.mision))
        .filter(
            MisionUsuario.usuario_id == usuario_id,
            or_(
                MisionUsuario.estado == EstadoMision.DISPONIBLE,
                MisionUsuario.estado == EstadoMision.EN_PROGRESO,
            ),
            or_(
                MisionUsuario.fecha_expiracion == None,  # noqa: E711
                MisionUsuario.fecha_expiracion > datetime.utcnow(),
            ),
        )
    )

    if frecuencia:
        query = query.join(Mision).filter(Mision.frecuencia == frecuencia)

    return query.all()


def asignar_mision(
    db: Session, mision_usuario: MisionUsuarioCreate
) -> MisionUsuario:
    """Asignar una misión a un usuario."""
    db_mision_usuario = MisionUsuario(
        usuario_id=mision_usuario.usuario_id,
        mision_id=mision_usuario.mision_id,
        estado=mision_usuario.estado,
        progreso_actual=mision_usuario.progreso_actual,
        fecha_expiracion=mision_usuario.fecha_expiracion,
    )
    db.add(db_mision_usuario)
    db.commit()
    db.refresh(db_mision_usuario)
    return db_mision_usuario


def actualizar_progreso_mision(
    db: Session,
    mision_usuario_id: uuid.UUID,
    incremento: int,
    metadata: dict | None = None,
) -> MisionUsuario | None:
    """Actualizar el progreso de una misión."""
    db_mision_usuario = get_mision_usuario(db, mision_usuario_id)
    if not db_mision_usuario:
        return None

    # Actualizar progreso
    db_mision_usuario.progreso_actual += incremento

    # Marcar como en progreso si está disponible
    if db_mision_usuario.estado == EstadoMision.DISPONIBLE:
        db_mision_usuario.estado = EstadoMision.EN_PROGRESO
        db_mision_usuario.fecha_inicio = datetime.utcnow()

    # Verificar si se completó
    if db_mision_usuario.progreso_actual >= db_mision_usuario.mision.objetivo:
        db_mision_usuario.progreso_actual = db_mision_usuario.mision.objetivo
        db_mision_usuario.estado = EstadoMision.COMPLETADA
        db_mision_usuario.fecha_completada = datetime.utcnow()

    # Actualizar metadata
    if metadata:
        current_metadata = db_mision_usuario.metadata_progreso or {}
        current_metadata.update(metadata)
        db_mision_usuario.metadata_progreso = current_metadata

    db.commit()
    db.refresh(db_mision_usuario)
    return db_mision_usuario


def reclamar_recompensa(
    db: Session, mision_usuario_id: uuid.UUID
) -> MisionUsuario | None:
    """Reclamar la recompensa de una misión completada."""
    db_mision_usuario = get_mision_usuario(db, mision_usuario_id)
    if not db_mision_usuario:
        return None

    if db_mision_usuario.estado != EstadoMision.COMPLETADA:
        return None

    db_mision_usuario.estado = EstadoMision.RECLAMADA
    db_mision_usuario.fecha_reclamada = datetime.utcnow()

    db.commit()
    db.refresh(db_mision_usuario)
    return db_mision_usuario


def verificar_y_expirar_misiones(db: Session, usuario_id: uuid.UUID) -> int:
    """Verificar y marcar como expiradas las misiones que ya pasaron su fecha."""
    ahora = datetime.utcnow()
    misiones_a_expirar = (
        db.query(MisionUsuario)
        .filter(
            MisionUsuario.usuario_id == usuario_id,
            MisionUsuario.estado.in_(
                [EstadoMision.DISPONIBLE, EstadoMision.EN_PROGRESO]
            ),
            MisionUsuario.fecha_expiracion != None,  # noqa: E711
            MisionUsuario.fecha_expiracion < ahora,
        )
        .all()
    )

    count = 0
    for mision in misiones_a_expirar:
        mision.estado = EstadoMision.EXPIRADA
        count += 1

    if count > 0:
        db.commit()

    return count


def asignar_misiones_diarias(db: Session, usuario_id: uuid.UUID) -> list[MisionUsuario]:
    """Asignar misiones diarias activas al usuario."""
    # Obtener misiones diarias activas
    misiones_diarias = get_misiones(
        db, activas_solo=True, frecuencia=FrecuenciaMision.DIARIA, limit=100
    )

    # Verificar cuáles ya tiene asignadas para hoy
    hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    manana = hoy + timedelta(days=1)

    misiones_existentes = (
        db.query(MisionUsuario.mision_id)
        .filter(
            MisionUsuario.usuario_id == usuario_id,
            MisionUsuario.fecha_asignacion >= hoy,
            MisionUsuario.fecha_asignacion < manana,
        )
        .all()
    )
    misiones_existentes_ids = {m[0] for m in misiones_existentes}

    # Asignar las que faltan
    nuevas_misiones = []
    for mision in misiones_diarias:
        if mision.mision_id not in misiones_existentes_ids:
            nueva_asignacion = MisionUsuarioCreate(
                usuario_id=usuario_id,
                mision_id=mision.mision_id,
                fecha_expiracion=manana,
            )
            db_mision_usuario = asignar_mision(db, nueva_asignacion)
            nuevas_misiones.append(db_mision_usuario)

    return nuevas_misiones


def obtener_estadisticas_misiones(
    db: Session, usuario_id: uuid.UUID
) -> dict:
    """Obtener estadísticas de misiones del usuario."""
    # Total completadas
    total_completadas = (
        db.query(func.count(MisionUsuario.mision_usuario_id))
        .filter(
            MisionUsuario.usuario_id == usuario_id,
            MisionUsuario.estado.in_([EstadoMision.COMPLETADA, EstadoMision.RECLAMADA]),
        )
        .scalar()
    )

    # Total en progreso
    total_en_progreso = (
        db.query(func.count(MisionUsuario.mision_usuario_id))
        .filter(
            MisionUsuario.usuario_id == usuario_id,
            MisionUsuario.estado == EstadoMision.EN_PROGRESO,
        )
        .scalar()
    )

    # Puntos ganados por misiones
    puntos_ganados = (
        db.query(func.coalesce(func.sum(Mision.puntos_recompensa), 0))
        .join(MisionUsuario)
        .filter(
            MisionUsuario.usuario_id == usuario_id,
            MisionUsuario.estado == EstadoMision.RECLAMADA,
        )
        .scalar()
    )

    # Misiones por tipo
    misiones_por_tipo = dict(
        db.query(Mision.tipo, func.count(MisionUsuario.mision_usuario_id))
        .join(MisionUsuario)
        .filter(
            MisionUsuario.usuario_id == usuario_id,
            MisionUsuario.estado.in_([EstadoMision.COMPLETADA, EstadoMision.RECLAMADA]),
        )
        .group_by(Mision.tipo)
        .all()
    )

    # Misiones por dificultad
    misiones_por_dificultad = dict(
        db.query(Mision.dificultad, func.count(MisionUsuario.mision_usuario_id))
        .join(MisionUsuario)
        .filter(
            MisionUsuario.usuario_id == usuario_id,
            MisionUsuario.estado.in_([EstadoMision.COMPLETADA, EstadoMision.RECLAMADA]),
        )
        .group_by(Mision.dificultad)
        .all()
    )

    return {
        "total_completadas": total_completadas or 0,
        "total_en_progreso": total_en_progreso or 0,
        "racha_actual": 0,  # TODO: Calcular racha
        "racha_maxima": 0,  # TODO: Calcular racha máxima
        "puntos_ganados_misiones": int(puntos_ganados or 0),
        "misiones_por_tipo": {k.value: v for k, v in misiones_por_tipo.items()},
        "misiones_por_dificultad": {
            k.value: v for k, v in misiones_por_dificultad.items()
        },
    }
