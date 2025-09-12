from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.crud.gamificacion import puntos as crud_puntos
from src.schemas.gamification import puntos as schemas_puntos
from src.db.session import get_db
from src.api.dependencies import get_current_user
from src.models.users.usuario import Usuario

router = APIRouter()

# Obtener puntos del usuario autenticado
@router.get(
    "/me",
    response_model=schemas_puntos.UsuarioPuntosResponse,
    summary="Obtener mis puntos acumulados",
    tags=["Puntos"]
)
def get_my_points(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    puntos = crud_puntos.get_usuario_puntos(db, current_user.usuario_id)
    if not puntos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puntos no encontrados para el usuario"
        )
    return puntos

# CRUD Puntos (solo para pruebas/admin, normalmente no se expone crear/eliminar puntos directos)
@router.post(
    "/",
    response_model=schemas_puntos.UsuarioPuntosResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear registro de puntos para usuario",
    tags=["Puntos"]
)
def create_usuario_puntos(usuario_id: str, db: Session = Depends(get_db)):
    return crud_puntos.create_usuario_puntos(db, usuario_id)

@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar registro de puntos de usuario",
    tags=["Puntos"]
)
def delete_usuario_puntos(usuario_id: str, db: Session = Depends(get_db)):
    puntos = crud_puntos.get_usuario_puntos(db, usuario_id)
    if not puntos:
        raise HTTPException(status_code=404, detail="UsuarioPuntos no encontrado")
    db.delete(puntos)
    db.commit()
    return None

# Asignar y descontar puntos
@router.post(
    "/asignar",
    response_model=schemas_puntos.UsuarioPuntosResponse,
    summary="Asignar puntos a un usuario",
    tags=["Puntos"]
)
def asignar_puntos(request: schemas_puntos.AsignarPuntosRequest, db: Session = Depends(get_db)):
    return crud_puntos.asignar_puntos(db, request)

# Historial y ranking
@router.get(
    "/historial",
    response_model=List[schemas_puntos.HistorialPuntosResponse],
    summary="Obtener mi historial de puntos",
    tags=["Puntos"]
)
def get_my_point_history(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    return crud_puntos.get_historial_puntos_usuario(db, current_user.usuario_id, skip=skip, limit=limit)

@router.get(
    "/ranking",
    response_model=List[schemas_puntos.RankingUsuarioResponse],
    summary="Obtener el ranking de usuarios",
    tags=["Puntos"]
)
def get_user_ranking(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    return crud_puntos.get_ranking_usuarios(db, skip=skip, limit=limit)