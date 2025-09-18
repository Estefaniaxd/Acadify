# api/v1/endpoints/communication.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

# Importar dependencias de base de datos
from src.db.session import get_db

# Importar CRUDs
from src.crud.communication.chat_bot import CRUDChatBot
from src.crud.communication.mensaje import CRUDMensaje

# Importar schemas
from src.schemas.communication.chat_bot import (
    ChatBot,
    ChatBotCreate,
    ChatBotUpdate,
)

from src.enums.communication.mensaje_enums import TipoMensaje

# Crear instancias de los CRUDs
crud_chatbot = CRUDChatBot()

# Crear router principal
router = APIRouter()

CHAT_BOT_NOT_FOUND = "Chat Bot no encontrado"

# ============================================================================
# ENDPOINTS PARA CHATBOT
# ============================================================================

@router.post("/chatbots/", response_model=ChatBot, status_code=status.HTTP_201_CREATED)
def create_chatbot(
    *,
    db: Session = Depends(get_db),
    chatbot_in: ChatBotCreate
) -> Any:
    """
    Crear nuevo chatbot.
    """
    # Verificar si ya existe un chatbot con el mismo nombre
    existing = crud_chatbot.get_by_nombre(db, nombre=chatbot_in.nombre)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un chatbot con el nombre '{chatbot_in.nombre}'"
        )
    
    chatbot = crud_chatbot.create(db=db, obj_in=chatbot_in)
    return chatbot

@router.get("/chatbots/", response_model=List[ChatBot])
def read_chatbots(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Obtener lista de chatbots con paginación.
    """
    chatbots = crud_chatbot.get_multi(db, skip=skip, limit=limit)
    return chatbots

@router.get("/chatbots/{chat_bot_id}", response_model=ChatBot)
def read_chatbot(
    *,
    db: Session = Depends(get_db),
    chat_bot_id: UUID
) -> Any:
    """
    Obtener chatbot por ID.
    """
    chatbot = crud_chatbot.get(db=db, chat_bot_id=chat_bot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_BOT_NOT_FOUND
        )
    return chatbot

@router.get("/chatbots/nombre/{nombre}", response_model=ChatBot)
def read_chatbot_by_name(
    *,
    db: Session = Depends(get_db),
    nombre: str
) -> Any:
    """
    Obtener chatbot por nombre.
    """
    chatbot = crud_chatbot.get_by_nombre(db=db, nombre=nombre)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chatbot con nombre '{nombre}' no encontrado"
        )
    return chatbot

@router.get("/chatbots/estado/activos", response_model=List[ChatBot])
def read_active_chatbots(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener todos los chatbots activos.
    """
    return crud_chatbot.get_active_bots(db)

@router.get("/chatbots/estado/inactivos", response_model=List[ChatBot])
def read_inactive_chatbots(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener todos los chatbots inactivos.
    """
    return crud_chatbot.get_inactive_bots(db)

@router.get("/chatbots/buscar/{search_term}", response_model=List[ChatBot])
def search_chatbots(
    *,
    db: Session = Depends(get_db),
    search_term: str
) -> Any:
    """
    Buscar chatbots por nombre o descripción.
    """
    return crud_chatbot.search_by_name_or_description(db, search_term=search_term)

@router.get("/chatbots/fecha/rango", response_model=List[ChatBot])
def read_chatbots_by_date_range(
    *,
    db: Session = Depends(get_db),
    start_date: date = Query(..., description="Fecha de inicio"),
    end_date: date = Query(..., description="Fecha de fin")
) -> Any:
    """
    Obtener chatbots registrados en un rango de fechas.
    """
    return crud_chatbot.get_by_date_range(db, start_date=start_date, end_date=end_date)

@router.put("/chatbots/{chat_bot_id}", response_model=ChatBot)
def update_chatbot(
    *,
    db: Session = Depends(get_db),
    chat_bot_id: UUID,
    chatbot_in: ChatBotUpdate
) -> Any:
    """
    Actualizar chatbot.
    """
    chatbot = crud_chatbot.get(db=db, chat_bot_id=chat_bot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_BOT_NOT_FOUND
        )
    
    chatbot = crud_chatbot.update(db=db, db_obj=chatbot, obj_in=chatbot_in)
    return chatbot

@router.patch("/chatbots/{chat_bot_id}/activar", response_model=ChatBot)
def activate_chatbot(
    *,
    db: Session = Depends(get_db),
    chat_bot_id: UUID
) -> Any:
    """
    Activar chatbot.
    """
    chatbot = crud_chatbot.activate(db=db, chat_bot_id=chat_bot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_BOT_NOT_FOUND
        )
    return chatbot

@router.patch("/chatbots/{chat_bot_id}/desactivar", response_model=ChatBot)
def deactivate_chatbot(
    *,
    db: Session = Depends(get_db),
    chat_bot_id: UUID
) -> Any:
    """
    Desactivar chatbot.
    """
    chatbot = crud_chatbot.deactivate(db=db, chat_bot_id=chat_bot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_BOT_NOT_FOUND
        )
    return chatbot

@router.delete("/chatbots/{chat_bot_id}", response_model=ChatBot)
def delete_chatbot(
    *,
    db: Session = Depends(get_db),
    chat_bot_id: UUID
) -> Any:
    """
    Eliminar chatbot.
    """
    chatbot = crud_chatbot.remove(db=db, chat_bot_id=chat_bot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_BOT_NOT_FOUND
        )
    return chatbot