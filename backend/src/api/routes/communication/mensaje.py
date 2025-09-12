from typing import List, Any, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status 
from sqlalchemy.orm import Session
from datetime import datetime

# Importar dependencias de base de datos

from src.db.session import get_db

from src.crud.communication.mensaje import CRUDMensaje

from src.enums.communication.mensaje_enums import TipoMensaje

from src.schemas.communication.mensaje import {
    Mensaje
}



@router.post("/mensajes/", response_model=Mensaje, status_code=status.HTTP_201_CREATED)
def create_mensaje(
    *,
    db: Session = Depends(get_db),
    mensaje_in: MensajeCreate
) -> Any:
    """
    Crear nuevo mensaje.
    """
    mensaje = crud_mensaje.create(db=db, obj_in=mensaje_in)
    return mensaje

@router.get("/mensajes/", response_model=List[Mensaje])
def read_mensajes(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Obtener lista de mensajes con paginación.
    """
    mensajes = crud_mensaje.get_multi(db, skip=skip, limit=limit)
    return mensajes

@router.get("/mensajes/{mensaje_id}", response_model=Mensaje)
def read_mensaje(
    *,
    db: Session = Depends(get_db),
    mensaje_id: UUID
) -> Any:
    """
    Obtener mensaje por ID.
    """
    mensaje = crud_mensaje.get(db=db, mensaje_id=mensaje_id)
    if not mensaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado"
        )
    return mensaje

@router.get("/mensajes/chat-grupo/{chat_grupo_id}", response_model=List[Mensaje])
def read_mensajes_by_chat_grupo(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Obtener mensajes por chat grupo con paginación.
    """
    return crud_mensaje.get_by_chat_grupo(
        db,
        chat_grupo_id=chat_grupo_id,
        skip=skip,
        limit=limit
    )

@router.get("/mensajes/emisor/{emisor_id}", response_model=List[Mensaje])
def read_mensajes_by_emisor(
    *,
    db: Session = Depends(get_db),
    emisor_id: UUID
) -> Any:
    """
    Obtener mensajes por emisor.
    """
    return crud_mensaje.get_by_emisor(db, emisor_id=emisor_id)

@router.get("/mensajes/tipo/{tipo}", response_model=List[Mensaje])
def read_mensajes_by_tipo(
    *,
    db: Session = Depends(get_db),
    tipo: TipoMensaje
) -> Any:
    """
    Obtener mensajes por tipo.
    """
    return crud_mensaje.get_by_tipo(db, tipo=tipo)

@router.get("/mensajes/fecha/rango", response_model=List[Mensaje])
def read_mensajes_by_date_range(
    *,
    db: Session = Depends(get_db),
    start_date: datetime = Query(..., description="Fecha de inicio"),
    end_date: datetime = Query(..., description="Fecha de fin")
) -> Any:
    """
    Obtener mensajes en un rango de fechas.
    """
    return crud_mensaje.get_by_date_range(db, start_date=start_date, end_date=end_date)

@router.get("/mensajes/chat-grupo/{chat_grupo_id}/recientes", response_model=List[Mensaje])
def read_recent_messages_in_chat(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID,
    limit: int = Query(50, ge=1, le=200)
) -> Any:
    """
    Obtener mensajes más recientes de un chat específico.
    """
    return crud_mensaje.get_recent_messages_in_chat(db, chat_grupo_id=chat_grupo_id, limit=limit)

@router.get("/mensajes/buscar/{search_term}", response_model=List[Mensaje])
def search_mensajes(
    *,
    db: Session = Depends(get_db),
    search_term: str
) -> Any:
    """
    Buscar mensajes por contenido.
    """
    return crud_mensaje.search_by_content(db, search_term=search_term)

@router.get("/mensajes/usuario-chat/", response_model=List[Mensaje])
def read_messages_by_user_in_chat(
    *,
    db: Session = Depends(get_db),
    emisor_id: UUID = Query(..., description="ID del emisor"),
    chat_grupo_id: UUID = Query(..., description="ID del chat grupo")
) -> Any:
    """
    Obtener mensajes de un usuario específico en un chat específico.
    """
    return crud_mensaje.get_messages_by_user_in_chat(
        db,
        emisor_id=emisor_id,
        chat_grupo_id=chat_grupo_id
    )

@router.get("/mensajes/tipo-chat/", response_model=List[Mensaje])
def read_messages_by_type_in_chat(
    *,
    db: Session = Depends(get_db),
    tipo: TipoMensaje = Query(..., description="Tipo de mensaje"),
    chat_grupo_id: UUID = Query(..., description="ID del chat grupo")
) -> Any:
    """
    Obtener mensajes por tipo en un chat específico.
    """
    return crud_mensaje.get_messages_by_type_in_chat(
        db,
        tipo=tipo,
        chat_grupo_id=chat_grupo_id
    )

@router.get("/mensajes/chat-grupo/{chat_grupo_id}/estadisticas", response_model=Dict[str, Any])
def read_chat_statistics(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID
) -> Any:
    """
    Obtener estadísticas de un chat específico.
    """
    return crud_mensaje.get_chat_statistics(db, chat_grupo_id=chat_grupo_id)

@router.get("/mensajes/estadisticas/tipo", response_model=Dict[str, int])
def read_mensaje_count_by_tipo(
    db: Session = Depends(get_db)
) -> Any:
    """
    Contar mensajes por tipo globalmente.
    """
    return crud_mensaje.count_messages_by_type(db)

@router.get("/mensajes/chats/mas-activos", response_model=List[Dict[str, Any]])
def read_most_active_chats(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
) -> Any:
    """
    Obtener los chats más activos.
    """
    return crud_mensaje.get_most_active_chats(db, limit=limit)

@router.get("/mensajes/anonimos/", response_model=List[Mensaje])
def read_anonymous_messages(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener mensajes sin emisor (anónimos).
    """
    return crud_mensaje.get_anonymous_messages(db)

@router.put("/mensajes/{mensaje_id}", response_model=Mensaje)
def update_mensaje(
    *,
    db: Session = Depends(get_db),
    mensaje_id: UUID,
    mensaje_in: MensajeUpdate
) -> Any:
    """
    Actualizar mensaje.
    """
    mensaje = crud_mensaje.get(db=db, mensaje_id=mensaje_id)
    if not mensaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado"
        )
    
    mensaje = crud_mensaje.update(db=db, db_obj=mensaje, obj_in=mensaje_in)
    return mensaje

@router.patch("/mensajes/{mensaje_id}/contenido", response_model=Mensaje)
def update_mensaje_content(
    *,
    db: Session = Depends(get_db),
    mensaje_id: UUID,
    new_content: str = Query(..., description="Nuevo contenido")
) -> Any:
    """
    Actualizar solo el contenido de un mensaje.
    """
    mensaje = crud_mensaje.update_content(
        db=db,
        mensaje_id=mensaje_id,
        new_content=new_content
    )
    if not mensaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado"
        )
    return mensaje

@router.delete("/mensajes/{mensaje_id}", response_model=Mensaje)
def delete_mensaje(
    *,
    db: Session = Depends(get_db),
    mensaje_id: UUID
) -> Any:
    """
    Eliminar mensaje.
    """
    mensaje = crud_mensaje.remove(db=db, mensaje_id=mensaje_id)
    if not mensaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado"
        )
    return mensaje

@router.delete("/mensajes/chat-grupo/{chat_grupo_id}/todos", response_model=Dict[str, Any])
def delete_all_messages_from_chat(
    *,
    db: Session = Depends(get_db),
    chat_grupo_id: UUID
) -> Any:
    """
    Eliminar todos los mensajes de un chat.
    """
    deleted_count = crud_mensaje.remove_messages_from_chat(db=db, chat_grupo_id=chat_grupo_id)
    return {
        "message": "Mensajes del chat eliminados exitosamente",
        "registros_eliminados": deleted_count,
        "chat_grupo_id": str(chat_grupo_id)
    }

@router.delete("/mensajes/antiguos/limpiar", response_model=Dict[str, Any])
def delete_old_mensajes(
    *,
    db: Session = Depends(get_db),
    older_than: datetime = Query(..., description="Eliminar mensajes más antiguos que esta fecha")
) -> Any:
    """
    Eliminar mensajes más antiguos que una fecha específica.
    """
    deleted_count = crud_mensaje.remove_old_messages(db=db, older_than=older_than)
    return {
        "message": "Mensajes antiguos eliminados exitosamente",
        "registros_eliminados": deleted_count,
        "fecha_corte": older_than.isoformat()
    }

@router.delete("/mensajes/usuario/{emisor_id}/todos", response_model=Dict[str, Any])
def delete_all_messages_by_user(
    *,
    db: Session = Depends(get_db),
    emisor_id: UUID
) -> Any:
    """
    Eliminar todos los mensajes de un usuario específico.
    """
    deleted_count = crud_mensaje.remove_messages_by_user(db=db, emisor_id=emisor_id)
    return {
        "message": "Mensajes del usuario eliminados exitosamente",
        "registros_eliminados": deleted_count,
        "emisor_id": str(emisor_id)
    }