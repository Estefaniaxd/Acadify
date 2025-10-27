# api/v1/endpoints/communication.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

# Importar dependencias de base de datos
from src.api.deps import get_db

import src.crud.communication.faq_bot as crud_faq_bot

from src.schemas.communication.faq_bot import (
    FAQBotCreate,
    FAQBotUpdate,
    FAQBot,
)

from src.enums.communication.chat_grupo_enums import EstadoChatGrupo


# Crear router principal
router = APIRouter()

FAQ_NOT_FOUND= "Faq no encontrada"

# ============================================================================
# ENDPOINTS PARA FAQBOT
# ============================================================================


@router.post("/faq-bots/", response_model=FAQBot, status_code=status.HTTP_201_CREATED)
def create_faq_bot(
    *,
    db: Session = Depends(get_db),
    faq_bot_in: FAQBotCreate
) -> Any:
    """
    Crear nueva FAQ.
    """
    faq_bot = faq_bot.create(db=db, obj_in=faq_bot_in)
    return faq_bot

@router.get("/faq-bots/", response_model=List[FAQBot])
def read_faq_bots(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Obtener lista de FAQs con paginación.
    """
    faq_bots = faq_bot.get_multi(db, skip=skip, limit=limit)
    return faq_bots

@router.get("/faq-bots/{faq_id}", response_model=FAQBot)
def read_faq_bot(
    *,
    db: Session = Depends(get_db),
    faq_id: UUID
) -> Any:
    """
    Obtener FAQ por ID.
    """
    faq_bot = faq_bot.get(db=db, faq_id=faq_id)
    if not faq_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=FAQ_NOT_FOUND
        )
    return faq_bot

@router.get("/faq-bots/categoria/{categoria}", response_model=List[FAQBot])
def read_faq_bots_by_categoria(
    *,
    db: Session = Depends(get_db),
    categoria: str
) -> Any:
    """
    Obtener FAQs por categoría.
    """
    return faq_bot.get_by_categoria(db, categoria=categoria)

@router.get("/faq-bots/categorias/todas", response_model=List[str])
def read_all_categorias(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener todas las categorías únicas.
    """
    return faq_bot.get_all_categorias(db)

@router.get("/faq-bots/buscar/pregunta/{search_term}", response_model=List[FAQBot])
def search_faq_bots_by_pregunta(
    *,
    db: Session = Depends(get_db),
    search_term: str
) -> Any:
    """
    Buscar FAQs por pregunta.
    """
    return faq_bot.search_by_pregunta(db, search_term=search_term)

@router.get("/faq-bots/buscar/respuesta/{search_term}", response_model=List[FAQBot])
def search_faq_bots_by_respuesta(
    *,
    db: Session = Depends(get_db),
    search_term: str
) -> Any:
    """
    Buscar FAQs por respuesta.
    """
    return faq_bot.search_by_respuesta(db, search_term=search_term)

@router.get("/faq-bots/buscar/contenido/{search_term}", response_model=List[FAQBot])
def search_faq_bots_in_content(
    *,
    db: Session = Depends(get_db),
    search_term: str
) -> Any:
    """
    Buscar FAQs en pregunta o respuesta.
    """
    return faq_bot.search_in_content(db, search_term=search_term)

@router.get("/faq-bots/recientes/", response_model=List[FAQBot])
def read_recent_faq_updates(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100)
) -> Any:
    """
    Obtener FAQs actualizadas recientemente.
    """
    return faq_bot.get_recent_updates(db, limit=limit)

@router.get("/faq-bots/agrupadas/categoria", response_model=Dict[str, List[FAQBot]])
def read_faqs_grouped_by_categoria(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener FAQs agrupadas por categoría.
    """
    return faq_bot.get_faqs_grouped_by_categoria(db)

@router.get("/faq-bots/estadisticas/categoria", response_model=Dict[str, int])
def read_faq_count_by_categoria(
    db: Session = Depends(get_db)
) -> Any:
    """
    Contar FAQs por categoría.
    """
    return faq_bot.count_by_categoria(db)

@router.put("/faq-bots/{faq_id}", response_model=FAQBot)
def update_faq_bot(
    *,
    db: Session = Depends(get_db),
    faq_id: UUID,
    faq_bot_in: FAQBotUpdate
) -> Any:
    """
    Actualizar FAQ.
    """
    faq_bot = faq_bot.get(db=db, faq_id=faq_id)
    if not faq_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=FAQ_NOT_FOUND
        )
    
    faq_bot = faq_bot.update(db=db, db_obj=faq_bot, obj_in=faq_bot_in)
    return faq_bot

@router.patch("/faq-bots/categoria/actualizar", response_model=Dict[str, Any])
def bulk_update_categoria(
    *,
    db: Session = Depends(get_db),
    old_categoria: str = Query(..., description="Categoría actual"),
    new_categoria: str = Query(..., description="Nueva categoría")
) -> Any:
    """
    Actualizar categoría en lote.
    """
    updated_count = faq_bot.bulk_update_categoria(
        db=db,
        old_categoria=old_categoria,
        new_categoria=new_categoria
    )
    return {
        "message": "Categoría actualizada exitosamente",
        "registros_actualizados": updated_count,
        "old_categoria": old_categoria,
        "new_categoria": new_categoria
    }

@router.post("/faq-bots/{faq_id}/duplicar", response_model=FAQBot)
def duplicate_faq(
    *,
    db: Session = Depends(get_db),
    faq_id: UUID,
    new_categoria: Optional[str] = Query(None, description="Nueva categoría para la copia")
) -> Any:
    """
    Duplicar FAQ existente.
    """
    new_faq = faq_bot.duplicate_faq(
        db=db,
        faq_id=faq_id,
        new_categoria=new_categoria
    )
    if not new_faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ original no encontrada"
        )
    return new_faq

@router.delete("/faq-bots/{faq_id}", response_model=FAQBot)
def delete_faq_bot(
    *,
    db: Session = Depends(get_db),
    faq_id: UUID
) -> Any:
    """
    Eliminar FAQ.
    """
    faq_bot = faq_bot.remove(db=db, faq_id=faq_id)
    if not faq_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=FAQ_NOT_FOUND
        )
    return faq_bot