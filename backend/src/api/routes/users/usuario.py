from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from sqlalchemy.orm import Session
import uuid

from src.schemas.users.usuario import Usuario, UsuarioUpdate
from src.crud.auth.user_crud import UserCRUD
from src.api.deps import get_db
from src.api.dependencies import (
    get_current_user,
    get_user_crud,
    require_admin_or_coordinator,
)

router = APIRouter()


USUARIO_NO_ENCONTRADO = "Usuario no encontrado"


@router.get(
    "/",
    response_model=List[Usuario],
    summary="Listar usuarios",
    description="Retorna una lista de todos los usuarios.",
)
async def get_all_usuarios(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_coordinator()),
    user_crud: UserCRUD = Depends(get_user_crud),
):
    usuarios, _ = user_crud.get_users_paginated(db)
    return usuarios


@router.get(
    "/{usuario_id}",
    response_model=Usuario,
    summary="Obtener un usuario por ID",
    description="Retorna los detalles de un usuario específico.",
)
async def get_usuario(
    usuario_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    user_crud: UserCRUD = Depends(get_user_crud),
):
    usuario = user_crud.get_by_id(db, user_id=str(usuario_id))
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USUARIO_NO_ENCONTRADO
        )
    return usuario


@router.put(
    "/{usuario_id}",
    response_model=Usuario,
    summary="Actualizar un usuario",
    description="Actualiza los datos de un usuario por su ID.",
)
async def update_usuario(
    usuario_id: uuid.UUID,
    usuario_in: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    user_crud: UserCRUD = Depends(get_user_crud),
):
    usuario = user_crud.get_by_id(db, user_id=str(usuario_id))
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USUARIO_NO_ENCONTRADO
        )
    return user_crud.update_user(db, user_id=str(usuario_id), user_update=usuario_in)


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un usuario",
    description="Elimina un usuario por su ID.",
)
async def delete_usuario(
    usuario_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    user_crud: UserCRUD = Depends(get_user_crud),
):
    usuario = user_crud.get_by_id(db, user_id=str(usuario_id))
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USUARIO_NO_ENCONTRADO
        )
    user_crud.delete_user(db, user_id=str(usuario_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
