from sqlalchemy.orm import Session
from uuid import UUID
from src.models.academic.institucion import Institucion
from src.schemas.academic.institucion import InstitucionCreate, InstitucionUpdate

class CRUDInstitucion:
    def get(self, db: Session, institucion_id: UUID):
        return db.query(Institucion).filter(Institucion.institucion_id == institucion_id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Institucion).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: InstitucionCreate):
        db_obj = Institucion(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Institucion, obj_in: InstitucionUpdate):
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, institucion_id: UUID):
        obj = db.query(Institucion).get(institucion_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

crud_institucion = CRUDInstitucion()
