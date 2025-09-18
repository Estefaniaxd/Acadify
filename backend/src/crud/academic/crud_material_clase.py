from sqlalchemy.orm import Session
from ..base import CRUDBase
from uuid import UUID
from ...models.academic.material_clase import MaterialClase
from ...schemas.academic.material_clase import MaterialClaseCreate, MaterialClaseUpdate


class CRUDMaterialClase(
    CRUDBase[MaterialClase, MaterialClaseCreate, MaterialClaseUpdate]
):
    def get(self, db: Session, material_clase_id: UUID):
        return (
            db.query(MaterialClase)
            .filter(MaterialClase.material_clase_id == material_clase_id)
            .first()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(MaterialClase).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: MaterialClaseCreate):
        db_obj = MaterialClase(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: MaterialClase, obj_in: MaterialClaseUpdate):
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, material_clase_id: UUID):
        obj = db.query(MaterialClase).get(material_clase_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


material_clase = CRUDMaterialClase(MaterialClase)
