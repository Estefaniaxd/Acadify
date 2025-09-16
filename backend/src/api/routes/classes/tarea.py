# routers/classes/tarea.py
from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.classes.tarea import TareaCreate, TareaUpdate, TareaRead
from src.crud.classes.tarea import CRUDTarea

router = APIRouter()
crud_tarea = CRUDTarea()


@router.post("/", response_model=TareaRead)
def create_tarea(tarea_in: TareaCreate, db: Session = Depends(get_db)):
    """Crear una nueva tarea"""
    return crud_tarea.create(db, obj_in=tarea_in)


@router.get("/{tarea_id}", response_model=TareaRead)
def get_tarea(tarea_id: UUID, db: Session = Depends(get_db)):
    """Obtener una tarea por ID"""
    tarea = crud_tarea.get(db, tarea_id=tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea


@router.get("/", response_model=List[TareaRead])
def get_tareas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener todas las tareas con paginación"""
    return crud_tarea.get_multi(db, skip=skip, limit=limit)


@router.get("/clase/{clase_id}", response_model=List[TareaRead])
def get_tareas_by_clase(clase_id: UUID, db: Session = Depends(get_db)):
    """Obtener tareas de una clase específica"""
    return crud_tarea.get_by_clase(db, clase_id=clase_id)


@router.get("/docente/{docente_id}", response_model=List[TareaRead])
def get_tareas_by_docente(docente_id: UUID, db: Session = Depends(get_db)):
    """Obtener tareas de un docente específico"""
    return crud_tarea.get_by_docente(db, docente_id=docente_id)


@router.get("/activas", response_model=List[TareaRead])
def get_tareas_activas(db: Session = Depends(get_db)):
    """Obtener tareas activas"""
    return crud_tarea.get_active_tasks(db)


@router.get("/vencidas", response_model=List[TareaRead])
def get_tareas_vencidas(db: Session = Depends(get_db)):
    """Obtener tareas vencidas (que no permiten entregas tardías)"""
    return crud_tarea.get_overdue_tasks(db)


@router.get("/rango-fechas", response_model=List[TareaRead])
def get_tareas_por_rango(
    start_date: datetime = Query(..., description="Fecha inicio"),
    end_date: datetime = Query(..., description="Fecha fin"),
    db: Session = Depends(get_db),
):
    """Obtener tareas asignadas en un rango de fechas"""
    return crud_tarea.get_tasks_by_date_range(
        db, start_date=start_date, end_date=end_date
    )


@router.get("/con-entregas-tardias", response_model=List[TareaRead])
def get_tareas_con_entregas_tardias(db: Session = Depends(get_db)):
    """Obtener tareas que permiten entregas tardías"""
    return crud_tarea.get_tasks_with_late_submissions(db)


@router.put("/{tarea_id}", response_model=TareaRead)
def update_tarea(tarea_id: UUID, tarea_in: TareaUpdate, db: Session = Depends(get_db)):
    """Actualizar una tarea"""
    db_obj = crud_tarea.get(db, tarea_id=tarea_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return crud_tarea.update(db, db_obj=db_obj, obj_in=tarea_in)


@router.delete("/{tarea_id}", response_model=TareaRead)
def delete_tarea(tarea_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una tarea"""
    obj = crud_tarea.remove(db, tarea_id=tarea_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return obj
