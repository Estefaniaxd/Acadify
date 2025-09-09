from sqlalchemy.orm import Session
from src.models.academic.curso import Curso
from src.schemas.academic.curso import CursoCreate, CursoUpdate
from uuid import UUID

class CRUDCurso:
    def get(self, db: Session, curso_id: UUID):
        return db.query(Curso).filter(Curso.curso_id == curso_id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Curso).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CursoCreate):
        db_obj = Curso(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Curso, obj_in: CursoUpdate):
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, curso_id: UUID):
        obj = db.query(Curso).get(curso_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

curso_crud = CRUDCurso()
