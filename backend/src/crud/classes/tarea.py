# crud/tarea.py
from typing import List, Optional
from ..base import CRUDBase
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from ...models.classes.tarea import Tarea
from ...schemas.classes.tarea import TareaCreate, TareaUpdate


class CRUDTarea(CRUDBase[Tarea, TareaCreate, TareaUpdate]):
    def create(self, db: Session, *, obj_in: TareaCreate) -> Tarea:
        """Crear nueva tarea"""
        db_obj = Tarea(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, tarea_id: UUID) -> Optional[Tarea]:
        """Obtener tarea por ID"""
        return db.query(Tarea).filter(Tarea.tarea_id == tarea_id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Tarea]:
        """Obtener múltiples tareas con paginación"""
        return db.query(Tarea).offset(skip).limit(limit).all()

    def get_by_clase(self, db: Session, clase_id: UUID) -> List[Tarea]:
        """Obtener tareas por clase"""
        return db.query(Tarea).filter(Tarea.clase_id == clase_id).all()

    def get_by_docente(self, db: Session, docente_id: UUID) -> List[Tarea]:
        """Obtener tareas por docente"""
        return db.query(Tarea).filter(Tarea.docente_id == docente_id).all()

    def get_active_tasks(self, db: Session) -> List[Tarea]:
        """Obtener tareas activas (sin fecha límite o con fecha límite futura)"""
        now = datetime.now()
        return (
            db.query(Tarea)
            .filter(
                (Tarea.fecha_limite.is_(None)) | (Tarea.fecha_limite > now)
            )
            .order_by(Tarea.fecha_limite.asc())
            .all()
        )

    def get_overdue_tasks(self, db: Session) -> List[Tarea]:
        """Obtener tareas vencidas"""
        now = datetime.now()
        return (
            db.query(Tarea)
            .filter(
                Tarea.fecha_limite < now,
                Tarea.permite_entregas_tardias == False
            )
            .all()
        )

    def get_tasks_by_date_range(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> List[Tarea]:
        """Obtener tareas asignadas en un rango de fechas"""
        return (
            db.query(Tarea)
            .filter(
                Tarea.fecha_asignacion >= start_date,
                Tarea.fecha_asignacion <= end_date,
            )
            .order_by(Tarea.fecha_asignacion)
            .all()
        )

    def get_tasks_with_late_submissions(self, db: Session) -> List[Tarea]:
        """Obtener tareas que permiten entregas tardías"""
        return (
            db.query(Tarea)
            .filter(Tarea.permite_entregas_tardias == True)
            .all()
        )

    def update(
        self, db: Session, *, db_obj: Tarea, obj_in: TareaUpdate
    ) -> Tarea:
        """Actualizar tarea"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, tarea_id: UUID) -> Tarea:
        """Eliminar tarea"""
        obj = db.query(Tarea).filter(Tarea.tarea_id == tarea_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

tarea = CRUDTarea(Tarea)