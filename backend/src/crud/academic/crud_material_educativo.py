from sqlalchemy.orm import Session
from ..base import CRUDBase
from uuid import UUID
from ...models.academic.material_educativo import MaterialEducativo
from ...schemas.academic.material_educativo import (
    MaterialEducativoCreate,
    MaterialEducativoUpdate,
)


class CRUDMaterialEducativo(
    CRUDBase[MaterialEducativo, MaterialEducativoCreate, MaterialEducativoUpdate]
):
    def get(self, db: Session, material_id: UUID):
        return (
            db.query(MaterialEducativo)
            .filter(MaterialEducativo.material_id == material_id)
            .first()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(MaterialEducativo).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: MaterialEducativoCreate):
        db_obj = MaterialEducativo(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: MaterialEducativo, obj_in: MaterialEducativoUpdate
    ):
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, material_id: UUID):
        obj = db.query(MaterialEducativo).get(material_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


material_educativo_crud = CRUDMaterialEducativo(MaterialEducativo, id_field="material_id")
