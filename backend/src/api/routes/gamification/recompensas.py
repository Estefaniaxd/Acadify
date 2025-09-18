from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.crud.gamification import recompensas as crud_recompensas
from backend.src.schemas.gamification import recompensa as schemas_recompensas
from src.db.session import get_db
from src.api.dependencies import get_current_user
from src.models.users.usuario import Usuario

router = APIRouter()


# CRUD Recompensas
@router.get(
    "/",
    response_model=List[schemas_recompensas.RecompensaResponse],
    summary="Listar todas las recompensas",
    tags=["Recompensas"],
)
def list_recompensas(db: Session = Depends(get_db)):
    return crud_recompensas.get_recompensas(db)


@router.post(
    "/",
    response_model=schemas_recompensas.RecompensaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una recompensa",
    tags=["Recompensas"],
)
def create_recompensa(
    recompensa: schemas_recompensas.RecompensaCreate, db: Session = Depends(get_db)
):
    return crud_recompensas.create_recompensa(db, recompensa)


@router.put(
    "/{recompensa_id}",
    response_model=schemas_recompensas.RecompensaResponse,
    summary="Actualizar una recompensa",
    tags=["Recompensas"],
)
def update_recompensa(
    recompensa_id: str,
    recompensa_update: schemas_recompensas.RecompensaUpdate,
    db: Session = Depends(get_db),
):
    recompensa = crud_recompensas.update_recompensa(
        db, recompensa_id, recompensa_update
    )
    if not recompensa:
        raise HTTPException(status_code=404, detail="Recompensa no encontrada")
    return recompensa


@router.delete(
    "/{recompensa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una recompensa",
    tags=["Recompensas"],
)
def delete_recompensa(recompensa_id: str, db: Session = Depends(get_db)):
    ok = crud_recompensas.delete_recompensa(db, recompensa_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Recompensa no encontrada")
    return None


# Endpoints de tienda y canje
@router.get(
    "/tienda/recompensas",
    response_model=List[schemas_recompensas.RecompensasDisponiblesResponse],
    summary="Ver recompensas disponibles en la tienda",
    tags=["Recompensas"],
)
def get_available_rewards(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    return crud_recompensas.get_recompensas_disponibles_usuario(
        db, current_user.usuario_id
    )


@router.post(
    "/tienda/recompensas/canjear",
    response_model=schemas_recompensas.UsuarioRecompensaResponse,
    summary="Canjear una recompensa por puntos",
    tags=["Recompensas"],
)
def redeem_reward(
    request: schemas_recompensas.CanjearRecompensaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if request.usuario_id != current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para canjear recompensas de otro usuario",
        )
    try:
        canje = crud_recompensas.canjear_recompensa(db, request)
        return canje
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/tienda/historial",
    response_model=schemas_recompensas.HistorialCanjesUsuarioResponse,
    summary="Ver mi historial de canjes",
    tags=["Recompensas"],
)
def get_my_redeem_history(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    canjes_data = crud_recompensas.get_estadisticas_canjes_usuario(
        db, current_user.usuario_id
    )
    return {
        "usuario_id": current_user.usuario_id,
        "total_canjes": canjes_data["total_canjes"],
        "puntos_gastados_total": canjes_data["puntos_gastados_total"],
        "canjes": canjes_data["canjes"],
    }
