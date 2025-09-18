# routers/classes/entregar_tarea.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.classes.entregar_tarea import (
    EntregarTareaCreate,
    EntregarTareaUpdate,
    EntregarTareaRead,
)
from src.crud.classes.entregar_tarea import CRUDEntregarTarea

router = APIRouter()
crud_entregar_tarea = CRUDEntregarTarea()


@router.post("/", response_model=EntregarTareaRead)
def create_entrega(entrega_in: EntregarTareaCreate, db: Session = Depends(get_db)):
    """Crear una nueva entrega"""
    return crud_entregar_tarea.create(db, obj_in=entrega_in)


@router.get("/{entrega_id}", response_model=EntregarTareaRead)
def get_entrega(entrega_id: UUID, db: Session = Depends(get_db)):
    """Obtener una entrega por ID"""
    entrega = crud_entregar_tarea.get(db, entrega_id=entrega_id)
    if not entrega:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
    return entrega


@router.get("/", response_model=List[EntregarTareaRead])
def get_entregas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener todas las entregas con paginación"""
    return crud_entregar_tarea.get_multi(db, skip=skip, limit=limit)


@router.get("/tarea/{tarea_id}", response_model=List[EntregarTareaRead])
def get_entregas_by_tarea(tarea_id: UUID, db: Session = Depends(get_db)):
    """Obtener entregas por tarea"""
    return crud_entregar_tarea.get_by_tarea(db, tarea_id=tarea_id)


@router.get("/estudiante/{estudiante_id}", response_model=List[EntregarTareaRead])
def get_entregas_by_estudiante(estudiante_id: UUID, db: Session = Depends(get_db)):
    """Obtener entregas por estudiante"""
    return crud_entregar_tarea.get_by_estudiante(db, estudiante_id=estudiante_id)


@router.get(
    "/tarea/{tarea_id}/estudiante/{estudiante_id}", response_model=EntregarTareaRead
)
def get_entrega_by_tarea_and_estudiante(
    tarea_id: UUID, estudiante_id: UUID, db: Session = Depends(get_db)
):
    """Obtener la entrega de un estudiante específico para una tarea"""
    entrega = crud_entregar_tarea.get_by_tarea_and_estudiante(
        db, tarea_id=tarea_id, estudiante_id=estudiante_id
    )
    if not entrega:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
    return entrega


@router.put("/{entrega_id}", response_model=EntregarTareaRead)
def update_entrega(
    entrega_id: UUID, entrega_in: EntregarTareaUpdate, db: Session = Depends(get_db)
):
    """Actualizar una entrega"""
    db_obj = crud_entregar_tarea.get(db, entrega_id=entrega_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
    return crud_entregar_tarea.update(db, db_obj=db_obj, obj_in=entrega_in)


@router.delete("/{entrega_id}", response_model=EntregarTareaRead)
def delete_entrega(entrega_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una entrega"""
    obj = crud_entregar_tarea.remove(db, entrega_id=entrega_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
    return obj
