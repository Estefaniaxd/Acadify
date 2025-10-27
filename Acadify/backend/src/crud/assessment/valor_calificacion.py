# src/crud/crud_valor_calificacion.py
from typing import List, Optional
from ..base import CRUDBase
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import asc
from ...models.assessment.valor_calificacion import ValorCalificacion
from ...schemas.assessment.valor_calificacion import (
    ValorCalificacionCreate,
    ValorCalificacionUpdate,
)


class CRUDValorCalificacion(CRUDBase[ValorCalificacion, ValorCalificacionCreate, ValorCalificacionUpdate]):
    def get_by_escala(
        self, db: Session, *, escala_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[ValorCalificacion]:
        """Obtiene todos los valores de calificación de una escala específica ordenados por orden."""
        return (
            db.query(self.model)
            .filter(ValorCalificacion.escala_id == escala_id)
            .order_by(asc(ValorCalificacion.orden))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_valor_and_escala(
        self, db: Session, *, valor: str, escala_id: UUID
    ) -> Optional[ValorCalificacion]:
        """Obtiene un valor de calificación por valor y escala."""
        return (
            db.query(self.model)
            .filter(
                ValorCalificacion.valor == valor,
                ValorCalificacion.escala_id == escala_id,
            )
            .first()
        )

    def get_by_orden_and_escala(
        self, db: Session, *, orden: int, escala_id: UUID
    ) -> Optional[ValorCalificacion]:
        """Obtiene un valor de calificación por orden y escala."""
        return (
            db.query(self.model)
            .filter(
                ValorCalificacion.orden == orden,
                ValorCalificacion.escala_id == escala_id,
            )
            .first()
        )

    def get_max_orden_by_escala(self, db: Session, *, escala_id: UUID) -> Optional[int]:
        """Obtiene el mayor orden de una escala específica."""
        result = (
            db.query(db.func.max(ValorCalificacion.orden))
            .filter(ValorCalificacion.escala_id == escala_id)
            .scalar()
        )
        return result or 0


valor_calificacion = CRUDValorCalificacion(ValorCalificacion)
