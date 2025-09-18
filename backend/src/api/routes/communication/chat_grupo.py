# api/v1/endpoints/communication.py
from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

# Importar dependencias de base de datos
from src.db.session import get_db

from src.crud.communication.chat_grupo import CRUDChatGrupo

from src.schemas.communication.chat_grupo import (
    ChatGrupo,
    ChatGrupoCreate,
    ChatGrupoUpdate,
)

from src.enums.communication.chat_grupo_enums import EstadoChatGrupo

# Importar enums
from src.enums.communication.chat_grupo_enums import EstadoChatGrupo

crud_chat_grupo = CRUDChatGrupo()

# Crear router principal
router = APIRouter()

CHAT_GRUPO_NOT_FOUND = "Chat de grupo no encontrado"

# ============================================================================
# ENDPOINTS PARA CHAT GRUPO
# ============================================================================


@router.post("/chat-grupos/", response_model=ChatGrupo, status_code=status.HTTP_201_CREATED)
def create_chat_grupo(
    *,
    db: Session = Depends(get_db),
    chat_grupo_in: ChatGrupoCreate
) -> Any:
    """
    Crear nuevo chat de grupo.
    """
    # Verificar si ya existe un chat para el grupo
    if chat_grupo_in.grupo_id:
        existing = crud_chat_grupo.get_by_grupo(db, grupo_id=chat_grupo_in.grupo_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un chat para este grupo"
            )
    
    chat_grupo = crud_chat_grupo.create(db=db, obj_in=chat_grupo_in)
    return chat_grupo

@router.get("/chat-grupos/", response_model=List[ChatGrupo])
def read_chat_grupos(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Obtener lista de chats de grupo con paginación.
    """
    chat_grupos = crud_chat_grupo.get_multi(db, skip=skip, limit=limit)
    return chat_grupos

@router.get("/chat-grupos/{chat_grupo_id}", response_model=ChatGrupo)
def read_chat_grupo(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID
) -> Any:
    """
    Obtener chat de grupo por ID.
    """
    chat_grupo = crud_chat_grupo.get(db=db, chat_grupo_id=chat_grupo_id)
    if not chat_grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_GRUPO_NOT_FOUND
        )
    return chat_grupo

@router.get("/chat-grupos/grupo/{grupo_id}", response_model=ChatGrupo)
def read_chat_grupo_by_grupo(
    *,
    db: Session = Depends(get_db),
    grupo_id: UUID
) -> Any:
    """
    Obtener chat por ID de grupo.
    """
    chat_grupo = crud_chat_grupo.get_by_grupo(db=db, grupo_id=grupo_id)
    if not chat_grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat de grupo no encontrado para este grupo"
        )
    return chat_grupo

@router.get("/chat-grupos/estado/{estado}", response_model=List[ChatGrupo])
def read_chat_grupos_by_estado(
    *,
    db: Session = Depends(get_db),
    estado: EstadoChatGrupo
) -> Any:
    """
    Obtener chats por estado.
    """
    return crud_chat_grupo.get_by_estado(db, estado=estado)

@router.get("/chat-grupos/activos/", response_model=List[ChatGrupo])
def read_active_chat_grupos(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener chats activos.
    """
    return crud_chat_grupo.get_active_chats(db)

@router.get("/chat-grupos/archivados/", response_model=List[ChatGrupo])
def read_archived_chat_grupos(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener chats archivados.
    """
    return crud_chat_grupo.get_archived_chats(db)

@router.get("/chat-grupos/archivos/permitidos", response_model=List[ChatGrupo])
def read_chat_grupos_with_files(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener chats que permiten archivos.
    """
    return crud_chat_grupo.get_chats_with_files_allowed(db)

@router.get("/chat-grupos/recientes/", response_model=List[ChatGrupo])
def read_recent_chat_grupos(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100)
) -> Any:
    """
    Obtener chats más recientes.
    """
    return crud_chat_grupo.get_recent_chats(db, limit=limit)

@router.put("/chat-grupos/{chat_grupo_id}", response_model=ChatGrupo)
def update_chat_grupo(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID,
    chat_grupo_in: ChatGrupoUpdate
) -> Any:
    """
    Actualizar chat de grupo.
    """
    chat_grupo = crud_chat_grupo.get(db=db, chat_grupo_id=chat_grupo_id)
    if not chat_grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_GRUPO_NOT_FOUND
        )
    
    chat_grupo = crud_chat_grupo.update(db=db, db_obj=chat_grupo, obj_in=chat_grupo_in)
    return chat_grupo

@router.patch("/chat-grupos/{chat_grupo_id}/archivar", response_model=ChatGrupo)
def archive_chat_grupo(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID
) -> Any:
    """
    Archivar chat de grupo.
    """
    chat_grupo = crud_chat_grupo.archive_chat(db=db, chat_grupo_id=chat_grupo_id)
    if not chat_grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_GRUPO_NOT_FOUND
        )
    return chat_grupo

@router.patch("/chat-grupos/{chat_grupo_id}/activar", response_model=ChatGrupo)
def activate_chat_grupo(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID
) -> Any:
    """
    Activar chat de grupo.
    """
    chat_grupo = crud_chat_grupo.activate_chat(db=db, chat_grupo_id=chat_grupo_id)
    if not chat_grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_GRUPO_NOT_FOUND
        )
    return chat_grupo

@router.patch("/chat-grupos/{chat_grupo_id}/almacenamiento", response_model=ChatGrupo)
def update_chat_storage(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID,
    new_capacity: int = Query(..., ge=0)
) -> Any:
    """
    Actualizar capacidad de almacenamiento del chat.
    """
    chat_grupo = crud_chat_grupo.update_storage_capacity(
        db=db, 
        chat_grupo_id=chat_grupo_id,
        new_capacity=new_capacity
    )
    if not chat_grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_GRUPO_NOT_FOUND
        )
    return chat_grupo

@router.patch("/chat-grupos/{chat_grupo_id}/toggle-archivos", response_model=ChatGrupo)
def toggle_file_permissions(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID
) -> Any:
    """
    Alternar permisos de archivos en el chat.
    """
    chat_grupo = crud_chat_grupo.toggle_file_permissions(db=db, chat_grupo_id=chat_grupo_id)
    if not chat_grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_GRUPO_NOT_FOUND
        )
    return chat_grupo

@router.delete("/chat-grupos/{chat_grupo_id}", response_model=ChatGrupo)
def delete_chat_grupo(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID
) -> Any:
    """
    Eliminar chat de grupo.
    """
    chat_grupo = crud_chat_grupo.remove(db=db, chat_grupo_id=chat_grupo_id)
    if not chat_grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_GRUPO_NOT_FOUND
        )
    return chat_grupo