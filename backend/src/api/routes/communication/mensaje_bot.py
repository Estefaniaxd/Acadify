# api/v1/endpoints/communication.py
from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

# Importar dependencias de base de datos
from src.db.session import get_db

from src.crud.communication.mensaje_bot import CRUDMensajeBot

from src.enums.communication.mensaje_bots_enum import ContextoMensaje


from src.schemas.communication.mensaje_bot import (
    MensajeBot,
    MensajeBotCreate,
)

from src.enums.communication.mensaje_bots_enum import ContextoMensaje

crud_mensaje_bot = CRUDMensajeBot()

# Crear router principal
router = APIRouter()

# ============================================================================
# ENDPOINTS PARA MENSAJE BOT
# ============================================================================

@router.post("/mensaje-bots/", response_model=MensajeBot, status_code=status.HTTP_201_CREATED)
def create_mensaje_bot(
    *,
    db: Session = Depends(get_db),
    mensaje_bot_in: MensajeBotCreate
) -> Any:
    """
    Crear nuevo mensaje de bot.
    """
    mensaje_bot = crud_mensaje_bot.create(db=db, obj_in=mensaje_bot_in)
    return mensaje_bot

@router.get("/mensaje-bots/", response_model=List[MensajeBot])
def read_mensaje_bots(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Obtener lista de mensajes bot con paginación.
    """
    mensaje_bots = crud_mensaje_bot.get_multi(db, skip=skip, limit=limit)
    return mensaje_bots

@router.get("/mensaje-bots/{mensaje_bot_id}", response_model=MensajeBot)
def read_mensaje_bot(
    *,
    db: Session = Depends(get_db),
    mensaje_bot_id: UUID
) -> Any:
    """
    Obtener mensaje bot por ID.
    """
    mensaje_bot = crud_mensaje_bot.get(db=db, mensaje_bot_id=mensaje_bot_id)
    if not mensaje_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje bot no encontrado"
        )
    return mensaje_bot

@router.get("/mensaje-bots/usuario/{usuario_id}", response_model=List[MensajeBot])
def read_mensaje_bots_by_usuario(
    *,
    db: Session = Depends(get_db),
    usuario_id: UUID
) -> Any:
    """
    Obtener mensajes bot por usuario.
    """
    return crud_mensaje_bot.get_by_usuario(db, usuario_id=usuario_id)

@router.get("/mensaje-bots/chat-grupo/{chat_grupo_id}", response_model=List[MensajeBot])
def read_mensaje_bots_by_chat_grupo(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID
) -> Any:
    """
    Obtener mensajes bot por chat grupo.
    """
    return crud_mensaje_bot.get_by_chat_grupo(db, chat_grupo_id=chat_grupo_id)

@router.get("/mensaje-bots/material/{material_id}", response_model=List[MensajeBot])
def read_mensaje_bots_by_material(
    *,
    db: Session = Depends(get_db),
    material_id: UUID
) -> Any:
    """
    Obtener mensajes bot relacionados con material educativo.
    """
    return crud_mensaje_bot.get_by_material_educativo(db, material_id=material_id)

@router.get("/mensaje-bots/contexto/{contexto}", response_model=List[MensajeBot])
def read_mensaje_bots_by_contexto(
    *,
    db: Session = Depends(get_db),
    contexto: ContextoMensaje
) -> Any:
    """
    Obtener mensajes bot por contexto.
    """
    return crud_mensaje_bot.get_by_contexto(db, contexto=contexto)

@router.get("/mensaje-bots/buscar/{search_term}", response_model=List[MensajeBot])
def search_mensaje_bots(
    *,
    db: Session = Depends(get_db),
    search_term: str
) -> Any:
    """
    Buscar mensajes bot por contenido o respuesta.
    """
    return crud_mensaje_bot.search_by_content(db, search_term=search_term)

@router.get("/mensaje-bots/conversacion/historial", response_model=List[MensajeBot])
def read_conversation_history(
    *,
    db: Session = Depends(Session.get_db),
    usuario_id: UUID = Query(..., description="ID del usuario"),
    chat_grupo_id: UUID = Query(..., description="ID del chat grupo"),
    limit: int = Query(100, ge=1, le=500)
) -> Any:
    """
    Obtener historial de conversación de un usuario en un chat específico.
    """
    historial = Session.crud_mensaje_bot.get_conversation_history(
        db=db,
        usuario_id=usuario_id,
        chat_grupo_id=chat_grupo_id,
        limit=limit
    )
    return historial