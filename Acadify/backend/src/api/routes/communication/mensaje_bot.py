# api/v1/endpoints/communication.py
from typing import List, Any, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime 

# Importar dependencias de base de datos
from src.api.deps import get_db

import src.crud.communication.mensaje_bot as crud_mensaje_bot

from src.enums.communication.mensaje_bots_enum import ContextoMensaje

from src.schemas.communication.mensaje_bot import (
    MensajeBot,
    MensajeBotCreate,
    MensajeBotUpdate,
)

# Crear router principal
router = APIRouter()

MENSAJE_BOT_NOT_FOUND = "Mensaje del Bot no encontrado"

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
            detail=MENSAJE_BOT_NOT_FOUND
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
    return mensaje_bot.search_by_content(db, search_term=search_term)

@router.get("/mensaje-bots/conversacion/historial", response_model=List[MensajeBot])
def read_conversation_history(
    *,
    db: Session = Depends(get_db),
    usuario_id: UUID = Query(..., description="ID del usuario"),
    chat_grupo_id: UUID = Query(..., description="ID del chat grupo"),
    limit: int = Query(100, ge=1, le=500)
) -> Any:
    """
    Obtener historial de conversación de un usuario en un chat específico.
    """
    return crud_mensaje_bot.get_conversation_history(
        db,
        usuario_id=usuario_id,
        chat_grupo_id=chat_grupo_id,
        limit=limit
    )

@router.get("/mensaje-bots/sin-respuesta", response_model=List[MensajeBot])
def read_unanswered_mensaje_bots(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener mensajes bot sin respuesta.
    """
    return crud_mensaje_bot.get_unanswered_messages(db)

@router.get("/mensaje-bots/recientes/", response_model=List[MensajeBot])
def read_recent_mensaje_bots(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200)
) -> Any:
    """
    Obtener mensajes bot más recientes.
    """
    return crud_mensaje_bot.get_recent_messages(db, limit=limit)

@router.get("/mensaje-bots/estadisticas/contexto", response_model=Dict[str, int])
def read_mensaje_bot_count_by_contexto(
    db: Session = Depends(get_db)
) -> Any:
    """
    Contar mensajes bot por contexto.
    """
    return mensaje_bot.count_messages_by_context(db)

@router.get("/mensaje-bots/estadisticas/usuarios-activos", response_model=Dict[str, int])
def read_active_users_mensaje_bot(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
) -> Any:
    """
    Obtener usuarios más activos en mensajes bot.
    """
    return mensaje_bot.count_messages_by_user(db, limit=limit)

@router.put("/mensaje-bots/{mensaje_bot_id}", response_model=MensajeBot)
def update_mensaje_bot(
    *,
    db: Session = Depends(get_db),
    mensaje_bot_id: UUID,
    mensaje_bot_in: MensajeBotUpdate
) -> Any:
    """
    Actualizar mensaje bot.
    """
    mensaje_bot = crud_mensaje_bot.get(db=db, mensaje_bot_id=mensaje_bot_id)
    if not mensaje_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MENSAJE_BOT_NOT_FOUND
        )
    
    mensaje_bot = crud_mensaje_bot.update(db=db, db_obj=mensaje_bot, obj_in=mensaje_bot_in)
    return mensaje_bot

@router.patch("/mensaje-bots/{mensaje_bot_id}/respuesta", response_model=MensajeBot)
def update_mensaje_bot_response(
    *,
    db: Session = Depends(get_db),
    mensaje_bot_id: UUID,
    new_response: str = Query(..., description="Nueva respuesta")
) -> Any:
    """
    Actualizar solo la respuesta de un mensaje bot.
    """
    mensaje_bot = crud_mensaje_bot.update_response(
        db=db,
        mensaje_bot_id=mensaje_bot_id,
        new_response=new_response
    )
    if not mensaje_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MENSAJE_BOT_NOT_FOUND
        )
    return mensaje_bot

@router.delete("/mensaje-bots/{mensaje_bot_id}", response_model=MensajeBot)
def delete_mensaje_bot(
    *,
    db: Session = Depends(get_db),
    mensaje_bot_id: UUID
) -> Any:
    """
    Eliminar mensaje bot.
    """
    mensaje_bot = crud_mensaje_bot.remove(db=db, mensaje_bot_id=mensaje_bot_id)
    if not mensaje_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MENSAJE_BOT_NOT_FOUND
        )
    return mensaje_bot

@router.delete("/mensaje-bots/antiguos/limpiar", response_model=Dict[str, Any])
def delete_old_mensaje_bots(
    *,
    db: Session = Depends(get_db),
    older_than: datetime = Query(..., description="Eliminar mensajes más antiguos que esta fecha")
) -> Any:
    """
    Eliminar mensajes bot más antiguos que una fecha específica.
    """
    deleted_count = crud_mensaje_bot.remove_old_messages(db=db, older_than=older_than)
    return {
        "message": "Mensajes bot antiguos eliminados exitosamente",
        "registros_eliminados": deleted_count,
        "fecha_corte": older_than.isoformat()
    }