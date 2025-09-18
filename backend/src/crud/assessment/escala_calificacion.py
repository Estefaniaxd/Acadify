# src/crud/crud_escala_calificacion.py
from typing import List, Optional
from ..base import CRUDBase
from uuid import UUID
from sqlalchemy.orm import Session
from ...models.assessment.escala_calificacion import EscalaCalificacion
from ...schemas.assessment.escala_calificacion import (
    EscalaCalificacionCreate,
    EscalaCalificacionUpdate,
)


class CRUDEscalaCalificacion(
    CRUDBase[EscalaCalificacion, EscalaCalificacionCreate, EscalaCalificacionUpdate]
):
    def get_by_institucion(
        self, db: Session, *, institucion_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[EscalaCalificacion]:
        """Obtiene todas las escalas de calificación de una institución específica."""
        return (
            db.query(self.model)
            .filter(EscalaCalificacion.institucion_id == institucion_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_nombre_and_institucion(
        self, db: Session, *, nombre: str, institucion_id: UUID
    ) -> Optional[EscalaCalificacion]:
        """Obtiene una escala de calificación por nombre e institución."""
        return (
            db.query(self.model)
            .filter(
                EscalaCalificacion.nombre == nombre,
                EscalaCalificacion.institucion_id == institucion_id,
            )
            .first()
        )

    def get_by_tipo_and_institucion(
        self,
        db: Session,
        *,
        tipo: str,
        institucion_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[EscalaCalificacion]:
        """Obtiene escalas de calificación por tipo e institución."""
        return (
            db.query(self.model)
            .filter(
                EscalaCalificacion.tipo == tipo,
                EscalaCalificacion.institucion_id == institucion_id,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )


escala_calificacion = CRUDEscalaCalificacion(EscalaCalificacion)
