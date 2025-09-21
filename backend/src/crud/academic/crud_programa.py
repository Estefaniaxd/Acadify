from sqlalchemy.orm import Session
from ..base import CRUDBase
from uuid import UUID
from ...models.academic.programa import Programa
from ...schemas.academic.programa import ProgramaCreate, ProgramaUpdate


class CRUDPrograma(CRUDBase[Programa, ProgramaCreate, ProgramaUpdate]):
    def get(self, db: Session, programa_id: UUID):
        return db.query(Programa).filter(Programa.programa_id == programa_id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Programa).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: ProgramaCreate):
        db_obj = Programa(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Programa, obj_in: ProgramaUpdate):
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, programa_id: UUID):
        obj = db.query(Programa).get(programa_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


programa_crud = CRUDPrograma(Programa, id_field="programa_id")
