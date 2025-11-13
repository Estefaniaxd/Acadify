"""Rutas API para el sistema de misiones."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.api.deps import get_db
from src.crud.gamification import mision as crud_misiones
from src.enums.gamification.mision_enums import EstadoMision, FrecuenciaMision
from src.models.users.usuario import Usuario
from src.schemas.gamification.mision import (
    ActualizarProgresoRequest,
    EstadisticasMisionesResponse,
    MisionCreate,
    MisionesDisponiblesResponse,
    MisionResponse,
    MisionUpdate,
    MisionUsuarioConDetalle,
    ReclamarRecompensaRequest,
)

router = APIRouter()


# ==================== Endpoints para Usuarios ====================
@router.get(
    "/disponibles",
    response_model=MisionesDisponiblesResponse,
    summary="Obtener misiones disponibles",
    tags=["Misiones - Usuario"],
)
def get_misiones_disponibles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene todas las misiones disponibles agrupadas por frecuencia."""
    # Expirar misiones vencidas primero
    crud_misiones.verificar_y_expirar_misiones(db, current_user.usuario_id)

    # Asignar misiones diarias si es necesario
    crud_misiones.asignar_misiones_diarias(db, current_user.usuario_id)

    # Obtener misiones por frecuencia
    diarias = crud_misiones.get_misiones_disponibles(
        db, current_user.usuario_id, FrecuenciaMision.DIARIA
    )
    semanales = crud_misiones.get_misiones_disponibles(
        db, current_user.usuario_id, FrecuenciaMision.SEMANAL
    )
    mensuales = crud_misiones.get_misiones_disponibles(
        db, current_user.usuario_id, FrecuenciaMision.MENSUAL
    )
    unicas = crud_misiones.get_misiones_disponibles(
        db, current_user.usuario_id, FrecuenciaMision.UNICA
    )

    # Contar completadas hoy
    from datetime import datetime, timedelta

    hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    completadas_hoy = (
        db.query(crud_misiones.MisionUsuario)
        .filter(
            crud_misiones.MisionUsuario.usuario_id == current_user.usuario_id,
            crud_misiones.MisionUsuario.fecha_completada >= hoy,
        )
        .count()
    )

    return {
        "diarias": diarias,
        "semanales": semanales,
        "mensuales": mensuales,
        "unicas": unicas,
        "total_disponibles": len(diarias) + len(semanales) + len(mensuales) + len(unicas),
        "total_completadas_hoy": completadas_hoy,
    }


@router.get(
    "/mis-misiones",
    response_model=list[MisionUsuarioConDetalle],
    summary="Obtener mis misiones",
    tags=["Misiones - Usuario"],
)
def get_mis_misiones(
    estado: EstadoMision | None = None,
    frecuencia: FrecuenciaMision | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene todas las misiones del usuario con filtros opcionales."""
    return crud_misiones.get_misiones_usuario(
        db, current_user.usuario_id, estado, frecuencia, skip, limit
    )


@router.patch(
    "/{mision_usuario_id}/progreso",
    response_model=MisionUsuarioConDetalle,
    summary="Actualizar progreso de misión",
    tags=["Misiones - Usuario"],
)
def actualizar_progreso(
    mision_usuario_id: str,
    request: ActualizarProgresoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza el progreso de una misión del usuario."""
    from uuid import UUID

    mision = crud_misiones.get_mision_usuario(db, UUID(mision_usuario_id))
    if not mision or mision.usuario_id != current_user.usuario_id:
        raise HTTPException(status_code=404, detail="Misión no encontrada")

    if mision.estado not in [EstadoMision.DISPONIBLE, EstadoMision.EN_PROGRESO]:
        raise HTTPException(
            status_code=400, detail="No se puede actualizar el progreso de esta misión"
        )

    updated = crud_misiones.actualizar_progreso_mision(
        db, UUID(mision_usuario_id), request.incremento, request.metadata
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Error al actualizar progreso")

    return updated


@router.post(
    "/{mision_usuario_id}/reclamar",
    response_model=MisionUsuarioConDetalle,
    summary="Reclamar recompensa de misión",
    tags=["Misiones - Usuario"],
)
def reclamar_recompensa(
    mision_usuario_id: str,
    request: ReclamarRecompensaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Reclama la recompensa de una misión completada."""
    from uuid import UUID

    mision = crud_misiones.get_mision_usuario(db, UUID(mision_usuario_id))
    if not mision or mision.usuario_id != current_user.usuario_id:
        raise HTTPException(status_code=404, detail="Misión no encontrada")

    if mision.estado != EstadoMision.COMPLETADA:
        raise HTTPException(
            status_code=400, detail="La misión no está completada"
        )

    # Reclamar recompensa
    updated = crud_misiones.reclamar_recompensa(db, UUID(mision_usuario_id))

    if not updated:
        raise HTTPException(status_code=400, detail="Error al reclamar recompensa")

    # TODO: Otorgar puntos y recompensas al usuario
    # Aquí deberías integrar con el sistema de puntos existente

    return updated


@router.get(
    "/estadisticas",
    response_model=EstadisticasMisionesResponse,
    summary="Obtener estadísticas de misiones",
    tags=["Misiones - Usuario"],
)
def get_estadisticas_misiones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene estadísticas de misiones del usuario."""
    stats = crud_misiones.obtener_estadisticas_misiones(db, current_user.usuario_id)
    return stats


# ==================== Endpoints Administrativos ====================
@router.get(
    "/admin/todas",
    response_model=list[MisionResponse],
    summary="Listar todas las misiones (Admin)",
    tags=["Misiones - Admin"],
)
def list_all_misiones(
    activas_solo: bool = True,
    frecuencia: FrecuenciaMision | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # TODO: Agregar dependencia de admin
):
    """Lista todas las misiones del sistema."""
    return crud_misiones.get_misiones(db, skip, limit, activas_solo, frecuencia)


@router.post(
    "/admin",
    response_model=MisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear misión (Admin)",
    tags=["Misiones - Admin"],
)
def create_mision(
    mision: MisionCreate,
    db: Session = Depends(get_db),
    # TODO: Agregar dependencia de admin
):
    """Crea una nueva misión."""
    return crud_misiones.create_mision(db, mision)


@router.put(
    "/admin/{mision_id}",
    response_model=MisionResponse,
    summary="Actualizar misión (Admin)",
    tags=["Misiones - Admin"],
)
def update_mision(
    mision_id: str,
    mision_update: MisionUpdate,
    db: Session = Depends(get_db),
    # TODO: Agregar dependencia de admin
):
    """Actualiza una misión existente."""
    from uuid import UUID

    updated = crud_misiones.update_mision(db, UUID(mision_id), mision_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Misión no encontrada")
    return updated


@router.delete(
    "/admin/{mision_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar misión (Admin)",
    tags=["Misiones - Admin"],
)
def delete_mision(
    mision_id: str,
    db: Session = Depends(get_db),
    # TODO: Agregar dependencia de admin
):
    """Elimina (desactiva) una misión."""
    from uuid import UUID

    success = crud_misiones.delete_mision(db, UUID(mision_id))
    if not success:
        raise HTTPException(status_code=404, detail="Misión no encontrada")
