# routers/classes/entregar_tarea.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.schemas.classes.entregar_tarea import (
    EntregarTareaCreate,
    EntregarTareaUpdate,
    EntregarTarea,
)
import src.crud.classes.entregar_tarea as crud_entrega_tarea

router = APIRouter()


@router.post("/", response_model=EntregarTarea)
def create_entrega(entrega_in: EntregarTareaCreate, db: Session = Depends(get_db)):
    """Crear una nueva entrega"""
    return entrega_tarea.create(db, obj_in=entrega_in)


@router.get("/{entrega_id}", response_model=EntregarTarea)
def get_entrega(entrega_id: UUID, db: Session = Depends(get_db)):
    """Obtener una entrega por ID"""
    entrega = entrega_tarea.get(db, entrega_id=entrega_id)
    if not entrega:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
    return entrega


@router.get("/", response_model=List[EntregarTarea])
def get_entregas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener todas las entregas con paginación"""
    return entrega_tarea.get_multi(db, skip=skip, limit=limit)


@router.get("/tarea/{tarea_id}", response_model=List[EntregarTarea])
def get_entregas_by_tarea(tarea_id: UUID, db: Session = Depends(get_db)):
    """Obtener entregas por tarea"""
    return entrega_tarea.get_by_tarea(db, tarea_id=tarea_id)


@router.get("/estudiante/{estudiante_id}", response_model=List[EntregarTarea])
def get_entregas_by_estudiante(estudiante_id: UUID, db: Session = Depends(get_db)):
    """Obtener entregas por estudiante"""
    return entrega_tarea.get_by_estudiante(db, estudiante_id=estudiante_id)


@router.get(
    "/tarea/{tarea_id}/estudiante/{estudiante_id}", response_model=EntregarTarea
)
def get_entrega_by_tarea_and_estudiante(
    tarea_id: UUID, estudiante_id: UUID, db: Session = Depends(get_db)
):
    """Obtener la entrega de un estudiante específico para una tarea"""
    entrega = entrega_tarea.get_by_tarea_and_estudiante(
        db, tarea_id=tarea_id, estudiante_id=estudiante_id
    )
    if not entrega:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
    return entrega


@router.put("/{entrega_id}", response_model=EntregarTarea)
def update_entrega(
    entrega_id: UUID, entrega_in: EntregarTareaUpdate, db: Session = Depends(get_db)
):
    """Actualizar una entrega"""
    db_obj = entrega_tarea.get(db, entrega_id=entrega_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
    return entrega_tarea.update(db, db_obj=db_obj, obj_in=entrega_in)


@router.delete("/{entrega_id}", response_model=EntregarTarea)
def delete_entrega(entrega_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una entrega"""
    obj = entrega_tarea.remove(db, entrega_id=entrega_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
    return obj
