# crud/classes.entregar_tarea.py
from typing import List, Optional
from ..base import CRUDBase
from uuid import UUID
from sqlalchemy.orm import Session
from ...models.classes.entregar_tarea import EntregarTarea
from ...schemas.classes.entregar_tarea import EntregarTareaCreate, EntregarTareaUpdate


class CRUDEntregarTarea(
    CRUDBase[EntregarTarea, EntregarTareaCreate, EntregarTareaUpdate]
):
    def create(self, db: Session, *, obj_in: EntregarTareaCreate) -> EntregarTarea:
        """Crear nueva entrega de tarea"""
        db_obj = EntregarTarea(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, entrega_id: UUID) -> Optional[EntregarTarea]:
        """Obtener entrega por ID"""
        return (
            db.query(EntregarTarea)
            .filter(EntregarTarea.entrega_id == entrega_id)
            .first()
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[EntregarTarea]:
        """Obtener múltiples entregas con paginación"""
        return db.query(EntregarTarea).offset(skip).limit(limit).all()

    def get_by_tarea(self, db: Session, tarea_id: UUID) -> List[EntregarTarea]:
        """Obtener entregas por tarea"""
        return db.query(EntregarTarea).filter(EntregarTarea.tarea_id == tarea_id).all()

    def get_by_estudiante(
        self, db: Session, estudiante_id: UUID
    ) -> List[EntregarTarea]:
        """Obtener entregas por estudiante"""
        return (
            db.query(EntregarTarea)
            .filter(EntregarTarea.estudiante_id == estudiante_id)
            .all()
        )

    def get_by_tarea_and_estudiante(
        self, db: Session, tarea_id: UUID, estudiante_id: UUID
    ) -> Optional[EntregarTarea]:
        """Obtener entrega específica de un estudiante para una tarea"""
        return (
            db.query(EntregarTarea)
            .filter(
                EntregarTarea.tarea_id == tarea_id,
                EntregarTarea.estudiante_id == estudiante_id,
            )
            .first()
        )

    def update(
        self, db: Session, *, db_obj: EntregarTarea, obj_in: EntregarTareaUpdate
    ) -> EntregarTarea:
        """Actualizar entrega de tarea"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, entrega_id: UUID) -> EntregarTarea:
        """Eliminar entrega de tarea"""
        obj = (
            db.query(EntregarTarea)
            .filter(EntregarTarea.entrega_id == entrega_id)
            .first()
        )
        if obj:
            db.delete(obj)
            db.commit()
        return obj


entrega_tarea = CRUDEntregarTarea(EntregarTarea)
