from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date

from src.models.academic.estudiante_grupo import EstudianteGrupo
from src.schemas.academic.estudiante_grupo import (
    EstudianteGrupoCreate,
    EstudianteGrupoUpdate,
)


class CRUDEstudianteGrupo:
    def get(self, db: Session, grupo_id: UUID, estudiante_id: UUID):
        return (
            db.query(EstudianteGrupo)
            .filter(
                EstudianteGrupo.grupo_id == grupo_id,
                EstudianteGrupo.estudiante_id == estudiante_id,
            )
            .first()
        )

    def create(self, db: Session, obj_in: EstudianteGrupoCreate) -> EstudianteGrupo:
        db_obj = EstudianteGrupo(
            grupo_id=obj_in.grupo_id,
            estudiante_id=obj_in.estudiante_id,
            fecha_vinculacion=obj_in.fecha_vinculacion,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: EstudianteGrupo,
        obj_in: EstudianteGrupoUpdate,
    ) -> EstudianteGrupo:
        db_obj.fecha_vinculacion = obj_in.fecha_vinculacion
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, grupo_id: UUID, estudiante_id: UUID):
        obj = self.get(db, grupo_id, estudiante_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def get_by_grupo(self, db: Session, grupo_id: UUID):
        return db.query(EstudianteGrupo).filter(EstudianteGrupo.grupo_id == grupo_id).all()

    def get_by_estudiante(self, db: Session, estudiante_id: UUID):
        return (
            db.query(EstudianteGrupo)
            .filter(EstudianteGrupo.estudiante_id == estudiante_id)
            .all()
        )


estudiante_grupo_crud = CRUDEstudianteGrupo()
