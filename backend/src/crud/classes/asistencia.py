# crud/asistencia.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.models import Asistencia
from src.schemas.classes.asistencia import AsistenciaCreate, AsistenciaUpdate
from src.enums.classes.asistencia_enums import EstadoAsistencia


class CRUDAsistencia:
    def create(self, db: Session, *, obj_in: AsistenciaCreate) -> Asistencia:
        """Crear nueva asistencia"""
        db_obj = Asistencia(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, asistencia_id: UUID) -> Optional[Asistencia]:
        """Obtener asistencia por ID"""
        return db.query(Asistencia).filter(Asistencia.asistencia_id == asistencia_id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Asistencia]:
        """Obtener múltiples asistencias con paginación"""
        return db.query(Asistencia).offset(skip).limit(limit).all()

    def get_by_clase(self, db: Session, clase_id: UUID) -> List[Asistencia]:
        """Obtener asistencias por clase"""
        return db.query(Asistencia).filter(Asistencia.clase_id == clase_id).all()

    def get_by_estudiante(self, db: Session, estudiante_id: UUID) -> List[Asistencia]:
        """Obtener asistencias por estudiante"""
        return db.query(Asistencia).filter(Asistencia.estudiante_id == estudiante_id).all()

    def get_by_clase_and_estudiante(
        self, db: Session, clase_id: UUID, estudiante_id: UUID
    ) -> Optional[Asistencia]:
        """Obtener asistencia específica de un estudiante en una clase"""
        return (
            db.query(Asistencia)
            .filter(
                Asistencia.clase_id == clase_id,
                Asistencia.estudiante_id == estudiante_id,
            )
            .first()
        )

    def get_by_estado(self, db: Session, estado: EstadoAsistencia) -> List[Asistencia]:
        """Obtener asistencias por estado"""
        return db.query(Asistencia).filter(Asistencia.estado == estado).all()

    def update(
        self, db: Session, *, db_obj: Asistencia, obj_in: AsistenciaUpdate
    ) -> Asistencia:
        """Actualizar asistencia"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, asistencia_id: UUID) -> Asistencia:
        """Eliminar asistencia"""
        obj = db.query(Asistencia).filter(Asistencia.asistencia_id == asistencia_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
