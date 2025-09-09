from sqlalchemy.orm import Session
from src.models.academic.curso_docente import CursoDocente
from src.schemas.academic.curso_docente import CursoDocenteCreate, CursoDocenteUpdate
from uuid import UUID

class CRUDCursoDocente:
    def get(self, db: Session, curso_id: UUID, docente_id: UUID):
        return db.query(CursoDocente).filter(
            CursoDocente.curso_id == curso_id,
            CursoDocente.docente_id == docente_id
        ).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(CursoDocente).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CursoDocenteCreate):
        db_obj = CursoDocente(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: CursoDocente, obj_in: CursoDocenteUpdate):
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, curso_id: UUID, docente_id: UUID):
        obj = self.get(db, curso_id, docente_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

curso_docente_crud = CRUDCursoDocente()
