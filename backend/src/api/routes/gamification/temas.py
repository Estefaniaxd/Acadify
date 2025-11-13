from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.api.deps import get_db
import src.crud.gamification.tema as crud_temas
from src.models.users.usuario import Usuario
from src.schemas.gamification.tema import (
    TemaCreate,
    TemaResponse,
    TemasUsuarioResponse,
    TemaUpdate,
)


router = APIRouter()


@router.get(
    "/me",
    response_model=TemasUsuarioResponse,
    summary="Obtener mis temas disponibles",
    tags=["Temas"],
)
def get_my_themes(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    """Obtiene los temas predefinidos y personalizados que tiene el usuario."""
    return crud_temas.get_temas_usuario(db, current_user.usuario_id)


# CRUD Temas
@router.get(
    "/",
    response_model=list[TemaResponse],
    summary="Listar todos los temas",
    tags=["Temas"],
)
def list_temas(db: Session = Depends(get_db)):
    return crud_temas.get_temas(db)


@router.post(
    "/",
    response_model=TemaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un tema",
    tags=["Temas"],
)
def create_tema(tema: TemaCreate, db: Session = Depends(get_db)):
    return crud_temas.create_tema(db, tema)


@router.put(
    "/{tema_id}",
    response_model=TemaResponse,
    summary="Actualizar un tema",
    tags=["Temas"],
)
def update_tema(tema_id: str, tema_update: TemaUpdate, db: Session = Depends(get_db)):
    tema = crud_temas.update_tema(db, tema_id, tema_update)
    if not tema:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    return tema


@router.delete(
    "/{tema_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un tema",
    tags=["Temas"],
)
def delete_tema(tema_id: str, db: Session = Depends(get_db)) -> None:
    ok = crud_temas.delete_tema(db, tema_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
