from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.crud.gamificacion import temas as crud_temas
from backend.src.schemas.gamification import tema as schemas_temas
from src.db.session import get_db
from src.api.dependencies import get_current_user
from src.models.users.usuario import Usuario

router = APIRouter()

@router.get(
    "/me",
    response_model=schemas_temas.TemasUsuarioResponse,
    summary="Obtener mis temas disponibles",
    tags=["Temas"]
)
def get_my_themes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene los temas predefinidos y personalizados que tiene el usuario.
    """
    return crud_temas.get_temas_usuario(db, current_user.usuario_id)


# CRUD Temas
@router.get(
    "/",
    response_model=list[schemas_temas.TemaResponse],
    summary="Listar todos los temas",
    tags=["Temas"]
)
def list_temas(db: Session = Depends(get_db)):
    return crud_temas.get_temas(db)


@router.post(
    "/",
    response_model=schemas_temas.TemaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un tema",
    tags=["Temas"]
)
def create_tema(tema: schemas_temas.TemaCreate, db: Session = Depends(get_db)):
    return crud_temas.create_tema(db, tema)


@router.put(
    "/{tema_id}",
    response_model=schemas_temas.TemaResponse,
    summary="Actualizar un tema",
    tags=["Temas"]
)
def update_tema(tema_id: str, tema_update: schemas_temas.TemaUpdate, db: Session = Depends(get_db)):
    tema = crud_temas.update_tema(db, tema_id, tema_update)
    if not tema:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    return tema


@router.delete(
    "/{tema_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un tema",
    tags=["Temas"]
)
def delete_tema(tema_id: str, db: Session = Depends(get_db)):
    ok = crud_temas.delete_tema(db, tema_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    return None