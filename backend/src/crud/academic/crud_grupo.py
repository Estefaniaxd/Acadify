from uuid import UUID

from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.models.academic.grupo import Grupo
from src.schemas.academic.grupo import GrupoCreate, GrupoUpdate


class CRUDGrupo(CRUDBase[Grupo, GrupoCreate, GrupoUpdate]):
    def get(self, db: Session, grupo_id: UUID):
        return db.query(Grupo).filter(Grupo.grupo_id == grupo_id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Grupo).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: GrupoCreate):
        db_obj = Grupo(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Grupo, obj_in: GrupoUpdate):
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, grupo_id: UUID):
        obj = db.query(Grupo).get(grupo_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


grupo_crud = CRUDGrupo(Grupo)
