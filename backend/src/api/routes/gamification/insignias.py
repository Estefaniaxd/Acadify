from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import src.crud.gamification.insignia as crud_insignias
from src.schemas.gamification.insignia import (
    InsigniaResponse, InsigniaCreate, InsigniaUpdate,
    UsuarioInsigniasResponse
)
from src.api.deps import get_db
from src.api.dependencies import get_current_user
from src.models.users.usuario import Usuario

router = APIRouter()


# Obtener insignias del usuario autenticado
@router.get(
    "/me",
    response_model=UsuarioInsigniasResponse,
    summary="Obtener mis insignias",
    tags=["Insignias"],
)
def get_my_insignias(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Obtiene todas las insignias obtenidas por el usuario autenticado.
    """
    insignias = crud_insignias.get_insignias_usuario(
        db, current_user.usuario_id, skip=skip, limit=limit
    )
    total_insignias = crud_insignias.count_insignias_usuario(
        db, current_user.usuario_id
    )
    return {
        "usuario_id": current_user.usuario_id,
        "total_insignias": total_insignias,
        "insignias": insignias,
    }


# CRUD Insignias
@router.get(
    "/",
    response_model=list[InsigniaResponse],
    summary="Listar todas las insignias",
    tags=["Insignias"],
)
def list_insignias(db: Session = Depends(get_db)):
    return crud_insignias.get_insignias(db)


@router.post(
    "/",
    response_model=InsigniaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una insignia",
    tags=["Insignias"],
)
def create_insignia(
    insignia: InsigniaCreate, db: Session = Depends(get_db)
):
    return crud_insignias.create_insignia(db, insignia)


@router.put(
    "/{insignia_id}",
    response_model=InsigniaResponse,
    summary="Actualizar una insignia",
    tags=["Insignias"],
)
def update_insignia(
    insignia_id: str,
    insignia_update: InsigniaUpdate,
    db: Session = Depends(get_db),
):
    insignia = crud_insignias.update_insignia(db, insignia_id, insignia_update)
    if not insignia:
        raise HTTPException(status_code=404, detail="Insignia no encontrada")
    return insignia


@router.delete(
    "/{insignia_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una insignia",
    tags=["Insignias"],
)
def delete_insignia(insignia_id: str, db: Session = Depends(get_db)):
    ok = crud_insignias.delete_insignia(db, insignia_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Insignia no encontrada")
    return None
