from sqlalchemy.orm import Session
from uuid import UUID
from src.models.academic.material_curso import MaterialCurso
from src.schemas.academic.material_curso import MaterialCursoCreate, MaterialCursoUpdate

class CRUDMaterialCurso:
    def get(self, db: Session, material_curso_id: UUID):
        return db.query(MaterialCurso).filter(MaterialCurso.material_curso_id == material_curso_id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(MaterialCurso).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: MaterialCursoCreate):
        db_obj = MaterialCurso(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: MaterialCurso, obj_in: MaterialCursoUpdate):
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, material_curso_id: UUID):
        obj = db.query(MaterialCurso).get(material_curso_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

crud_material_curso = CRUDMaterialCurso()
