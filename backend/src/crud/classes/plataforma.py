from uuid import UUID

from sqlalchemy.orm import Session

from ...models.classes.plataforma import Plataforma
from ...schemas.classes.plataforma import PlataformaCreate, PlataformaUpdate
from ..base import CRUDBase


class CRUDPlataforma(CRUDBase[Plataforma, PlataformaCreate, PlataformaUpdate]):
    def create(self, db: Session, *, obj_in: PlataformaCreate) -> Plataforma:
        """Crear una nueva plataforma."""
        db_obj = Plataforma(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, plataforma_id: UUID) -> Plataforma | None:
        """Obtener plataforma por ID."""
        return (
            db.query(Plataforma)
            .filter(Plataforma.plataforma_id == plataforma_id)
            .first()
        )

    def get_by_nombre(self, db: Session, nombre: str) -> Plataforma | None:
        """Obtener plataforma por nombre."""
        return db.query(Plataforma).filter(Plataforma.nombre == nombre).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Plataforma]:
        """Obtener múltiples plataformas con paginación."""
        return db.query(Plataforma).offset(skip).limit(limit).all()

    def update(
        self, db: Session, *, db_obj: Plataforma, obj_in: PlataformaUpdate
    ) -> Plataforma:
        """Actualizar plataforma."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, plataforma_id: UUID) -> Plataforma | None:
        """Eliminar plataforma."""
        obj = (
            db.query(Plataforma)
            .filter(Plataforma.plataforma_id == plataforma_id)
            .first()
        )
        if obj:
            db.delete(obj)
            db.commit()
        return obj


plataforma = CRUDPlataforma(Plataforma)
