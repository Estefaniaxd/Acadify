# crud/clase.py
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from ...models.classes.clase import Clase
from ...schemas.classes.clase import ClaseCreate, ClaseUpdate
from ..base import CRUDBase


class CRUDClase(CRUDBase[Clase, ClaseCreate, ClaseUpdate]):
    def create(self, db: Session, *, obj_in: ClaseCreate) -> Clase:
        """Crear nueva clase."""
        db_obj = Clase(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, clase_id: UUID) -> Clase | None:
        """Obtener clase por ID."""
        return db.query(Clase).filter(Clase.clase_id == clase_id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[Clase]:
        """Obtener múltiples clases con paginación."""
        return db.query(Clase).offset(skip).limit(limit).all()

    def get_by_grupo_curso(self, db: Session, grupo_curso_id: UUID) -> list[Clase]:
        """Obtener clases por grupo curso."""
        return db.query(Clase).filter(Clase.grupo_curso_id == grupo_curso_id).all()

    def get_by_plataforma(self, db: Session, plataforma_id: UUID) -> list[Clase]:
        """Obtener clases por plataforma."""
        return db.query(Clase).filter(Clase.plataforma_id == plataforma_id).all()

    def get_by_date_range(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> list[Clase]:
        """Obtener clases en un rango de fechas."""
        return (
            db.query(Clase)
            .filter(
                Clase.hora_inicio >= start_date,
                Clase.hora_inicio <= end_date,
            )
            .order_by(Clase.hora_inicio)
            .all()
        )

    def get_upcoming_classes(self, db: Session, limit: int = 10) -> list[Clase]:
        """Obtener próximas clases."""
        return (
            db.query(Clase)
            .filter(Clase.hora_inicio > datetime.now(UTC))
            .order_by(Clase.hora_inicio)
            .limit(limit)
            .all()
        )

    def update(self, db: Session, *, db_obj: Clase, obj_in: ClaseUpdate) -> Clase:
        """Actualizar clase."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, clase_id: UUID) -> Clase:
        """Eliminar clase."""
        obj = db.query(Clase).filter(Clase.clase_id == clase_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj


clase = CRUDClase(Clase)
