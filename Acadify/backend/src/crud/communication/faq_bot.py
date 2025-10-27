# crud/faq_bot.py
from typing import List, Optional
from ..base import CRUDBase
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from ...models.communication.faq_bot import FAQBot
from ...schemas.communication.faq_bot import FAQBotCreate, FAQBotUpdate


class CRUDFAQBot(CRUDBase[FAQBot, FAQBotCreate, FAQBotUpdate]):
    def create(self, db: Session, *, obj_in: FAQBotCreate) -> FAQBot:
        """Crear nueva FAQ"""
        # Establecer timestamp de actualización si no se proporciona
        faq_data = obj_in.model_dump()
        if not faq_data.get("ultima_actualizacion"):
            faq_data["ultima_actualizacion"] = datetime.now()

        db_obj = FAQBot(**faq_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, faq_id: UUID) -> Optional[FAQBot]:
        """Obtener FAQ por ID"""
        return db.query(FAQBot).filter(FAQBot.faq_id == faq_id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[FAQBot]:
        """Obtener múltiples FAQs con paginación"""
        return db.query(FAQBot).offset(skip).limit(limit).all()

    def get_by_categoria(self, db: Session, categoria: str) -> List[FAQBot]:
        """Obtener FAQs por categoría"""
        return db.query(FAQBot).filter(FAQBot.categoria == categoria).all()

    def get_all_categorias(self, db: Session) -> List[str]:
        """Obtener todas las categorías únicas"""
        categorias = db.query(FAQBot.categoria).distinct().all()
        return [cat[0] for cat in categorias]

    def search_by_pregunta(self, db: Session, search_term: str) -> List[FAQBot]:
        """Buscar FAQs por pregunta"""
        return db.query(FAQBot).filter(FAQBot.pregunta.ilike(f"%{search_term}%")).all()

    def search_by_respuesta(self, db: Session, search_term: str) -> List[FAQBot]:
        """Buscar FAQs por respuesta"""
        return db.query(FAQBot).filter(FAQBot.respuesta.ilike(f"%{search_term}%")).all()

    def search_in_content(self, db: Session, search_term: str) -> List[FAQBot]:
        """Buscar FAQs en pregunta o respuesta"""
        return (
            db.query(FAQBot)
            .filter(
                (FAQBot.pregunta.ilike(f"%{search_term}%"))
                | (FAQBot.respuesta.ilike(f"%{search_term}%"))
            )
            .all()
        )

    def get_recent_updates(self, db: Session, limit: int = 10) -> List[FAQBot]:
        """Obtener FAQs actualizadas recientemente"""
        return (
            db.query(FAQBot)
            .filter(FAQBot.ultima_actualizacion.is_not(None))
            .order_by(FAQBot.ultima_actualizacion.desc())
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> List[FAQBot]:
        """Obtener FAQs actualizadas en un rango de fechas"""
        return (
            db.query(FAQBot)
            .filter(
                FAQBot.ultima_actualizacion >= start_date,
                FAQBot.ultima_actualizacion <= end_date,
            )
            .order_by(FAQBot.ultima_actualizacion.desc())
            .all()
        )

    def get_faqs_grouped_by_categoria(self, db: Session) -> dict:
        """Obtener FAQs agrupadas por categoría"""
        faqs = db.query(FAQBot).all()
        grouped = {}
        for faq in faqs:
            if faq.categoria not in grouped:
                grouped[faq.categoria] = []
            grouped[faq.categoria].append(faq)
        return grouped

    def count_by_categoria(self, db: Session) -> dict:
        """Contar FAQs por categoría"""
        from sqlalchemy import func

        results = (
            db.query(FAQBot.categoria, func.count(FAQBot.faq_id))
            .group_by(FAQBot.categoria)
            .all()
        )

        return {categoria: count for categoria, count in results}

    def update(self, db: Session, *, db_obj: FAQBot, obj_in: FAQBotUpdate) -> FAQBot:
        """Actualizar FAQ"""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Actualizar timestamp de modificación
        update_data["ultima_actualizacion"] = datetime.now()

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, faq_id: UUID) -> Optional[FAQBot]:
        """Eliminar FAQ"""
        obj = db.query(FAQBot).filter(FAQBot.faq_id == faq_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def bulk_update_categoria(
        self, db: Session, *, old_categoria: str, new_categoria: str
    ) -> int:
        """Actualizar categoría en lote"""
        updated_count = (
            db.query(FAQBot)
            .filter(FAQBot.categoria == old_categoria)
            .update(
                {
                    FAQBot.categoria: new_categoria,
                    FAQBot.ultima_actualizacion: datetime.now(),
                }
            )
        )
        db.commit()
        return updated_count

    def duplicate_faq(
        self, db: Session, *, faq_id: UUID, new_categoria: str = None
    ) -> Optional[FAQBot]:
        """Duplicar FAQ existente"""
        original_faq = self.get(db, faq_id)
        if not original_faq:
            return None

        # Crear nueva FAQ basada en la original
        new_faq_data = FAQBotCreate(
            pregunta=f"[Copia] {original_faq.pregunta}",
            respuesta=original_faq.respuesta,
            categoria=new_categoria or original_faq.categoria,
            ultima_actualizacion=datetime.now(),
        )

        return self.create(db=db, obj_in=new_faq_data)

faq_bot = CRUDFAQBot(FAQBot)