# api/v1/endpoints/communication.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

# Importar dependencias de base de datos
from src.api.deps import get_db

# Importar CRUDs
import src.crud.communication.chat_bot as crud_chat_bot
import src.crud.communication.mensaje as crud_mensaje

# Importar schemas
from src.schemas.communication.chat_bot import (
    ChatBotRead,
    ChatBotCreate,
    ChatBotUpdate,
)

from src.enums.communication.mensaje_enums import TipoMensaje

# Crear router principal
router = APIRouter()

CHAT_BOT_NOT_FOUND = "Chat Bot no encontrado"

# ============================================================================
# ENDPOINTS PARA CHATBOT
# ============================================================================

@router.post("/chatbots/", response_model=ChatBotRead, status_code=status.HTTP_201_CREATED)
def create_chatbot(
    *,
    db: Session = Depends(get_db),
    chatbot_in: ChatBotCreate
) -> Any:
    """
    Crear nuevo chatbot.
    """
    # Verificar si ya existe un chatbot con el mismo nombre
    existing = chat_bot.get_by_nombre(db, nombre=chatbot_in.nombre)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un chatbot con el nombre '{chatbot_in.nombre}'"
        )
    
    chatbot = chat_bot.create(db=db, obj_in=chatbot_in)
    return chatbot

@router.get("/chatbots/", response_model=List[ChatBotRead])
def read_chatbots(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Obtener lista de chatbots con paginación.
    """
    chatbots = chat_bot.get_multi(db, skip=skip, limit=limit)
    return chatbots

@router.get("/chatbots/{chat_bot_id}", response_model=ChatBotRead)
def read_chatbot(
    *,
    db: Session = Depends(get_db),
    chat_bot_id: UUID
) -> Any:
    """
    Obtener chatbot por ID.
    """
    chatbot = chat_bot.get(db=db, chat_bot_id=chat_bot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_BOT_NOT_FOUND
        )
    return chatbot

@router.get("/chatbots/nombre/{nombre}", response_model=ChatBotRead)
def read_chatbot_by_name(
    *,
    db: Session = Depends(get_db),
    nombre: str
) -> Any:
    """
    Obtener chatbot por nombre.
    """
    chatbot = chat_bot.get_by_nombre(db=db, nombre=nombre)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chatbot con nombre '{nombre}' no encontrado"
        )
    return chatbot

@router.get("/chatbots/estado/activos", response_model=List[ChatBotRead])
def read_active_chatbots(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener todos los chatbots activos.
    """
    return chat_bot.get_active_bots(db)

@router.get("/chatbots/estado/inactivos", response_model=List[ChatBotRead])
def read_inactive_chatbots(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener todos los chatbots inactivos.
    """
    return chat_bot.get_inactive_bots(db)

@router.get("/chatbots/buscar/{search_term}", response_model=List[ChatBotRead])
def search_chatbots(
    *,
    db: Session = Depends(get_db),
    search_term: str
) -> Any:
    """
    Buscar chatbots por nombre o descripción.
    """
    return chat_bot.search_by_name_or_description(db, search_term=search_term)

@router.get("/chatbots/fecha/rango", response_model=List[ChatBotRead])
def read_chatbots_by_date_range(
    *,
    db: Session = Depends(get_db),
    start_date: date = Query(..., description="Fecha de inicio"),
    end_date: date = Query(..., description="Fecha de fin")
) -> Any:
    """
    Obtener chatbots registrados en un rango de fechas.
    """
    return chat_bot.get_by_date_range(db, start_date=start_date, end_date=end_date)

@router.put("/chatbots/{chat_bot_id}", response_model=ChatBotRead)
def update_chatbot(
    *,
    db: Session = Depends(get_db),
    chat_bot_id: UUID,
    chatbot_in: ChatBotUpdate
) -> Any:
    """
    Actualizar chatbot.
    """
    chatbot = chat_bot.get(db=db, chat_bot_id=chat_bot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_BOT_NOT_FOUND
        )
    
    chatbot = chat_bot.update(db=db, db_obj=chatbot, obj_in=chatbot_in)
    return chatbot

@router.patch("/chatbots/{chat_bot_id}/activar", response_model=ChatBotRead)
def activate_chatbot(
    *,
    db: Session = Depends(get_db),
    chat_bot_id: UUID
) -> Any:
    """
    Activar chatbot.
    """
    chatbot = chat_bot.activate(db=db, chat_bot_id=chat_bot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_BOT_NOT_FOUND
        )
    return chatbot

@router.patch("/chatbots/{chat_bot_id}/desactivar", response_model=ChatBotRead)
def deactivate_chatbot(
    *,
    db: Session = Depends(get_db),
    chat_bot_id: UUID
) -> Any:
    """
    Desactivar chatbot.
    """
    chatbot = chat_bot.deactivate(db=db, chat_bot_id=chat_bot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_BOT_NOT_FOUND
        )
    return chatbot

@router.delete("/chatbots/{chat_bot_id}", response_model=ChatBotRead)
def delete_chatbot(
    *,
    db: Session = Depends(get_db),
    chat_bot_id: UUID
) -> Any:
    """
    Eliminar chatbot.
    """
    chatbot = chat_bot.remove(db=db, chat_bot_id=chat_bot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_BOT_NOT_FOUND
        )
    return chatbot