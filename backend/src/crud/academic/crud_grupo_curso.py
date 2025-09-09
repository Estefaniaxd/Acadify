from sqlalchemy.orm import Session
from src.models.academic.grupo_curso import GrupoCurso
from src.schemas.academic.grupo_curso import GrupoCursoCreate, GrupoCursoUpdate
from uuid import UUID

class CRUDGrupoCurso:
    def get(self, db: Session, grupo_curso_id: UUID):
        return db.query(GrupoCurso).filter(GrupoCurso.grupo_curso_id == grupo_curso_id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(GrupoCurso).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: GrupoCursoCreate):
        db_obj = GrupoCurso(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: GrupoCurso, obj_in: GrupoCursoUpdate):
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, grupo_curso_id: UUID):
        obj = self.get(db, grupo_curso_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

grupo_curso_crud = CRUDGrupoCurso()
