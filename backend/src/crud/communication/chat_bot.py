# crud/chatbot.py
from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from src.models.communication.chat_bot import ChatBot
from src.schemas.communication.chat_bot import ChatBotCreate, ChatBotUpdate


class CRUDChatBot:
    def create(self, db: Session, *, obj_in: ChatBotCreate) -> ChatBot:
        """Crear nuevo chatbot"""
        db_obj = ChatBot(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, chat_bot_id: UUID) -> Optional[ChatBot]:
        """Obtener chatbot por ID"""
        return db.query(ChatBot).filter(ChatBot.chat_bot_id == chat_bot_id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ChatBot]:
        """Obtener múltiples chatbots con paginación"""
        return db.query(ChatBot).offset(skip).limit(limit).all()

    def get_by_nombre(self, db: Session, nombre: str) -> Optional[ChatBot]:
        """Obtener chatbot por nombre (único)"""
        return db.query(ChatBot).filter(ChatBot.nombre == nombre).first()

    def get_active_bots(self, db: Session) -> List[ChatBot]:
        """Obtener chatbots activos"""
        return db.query(ChatBot).filter(ChatBot.activo == True).all()

    def get_inactive_bots(self, db: Session) -> List[ChatBot]:
        """Obtener chatbots inactivos"""
        return db.query(ChatBot).filter(ChatBot.activo == False).all()

    def get_by_date_range(
        self, db: Session, start_date: date, end_date: date
    ) -> List[ChatBot]:
        """Obtener chatbots registrados en un rango de fechas"""
        return (
            db.query(ChatBot)
            .filter(
                ChatBot.fecha_registro >= start_date,
                ChatBot.fecha_registro <= end_date,
            )
            .order_by(ChatBot.fecha_registro.desc())
            .all()
        )

    def search_by_name_or_description(
        self, db: Session, search_term: str
    ) -> List[ChatBot]:
        """Buscar chatbots por nombre o descripción"""
        return (
            db.query(ChatBot)
            .filter(
                (ChatBot.nombre.ilike(f"%{search_term}%"))
                | (ChatBot.descripcion.ilike(f"%{search_term}%"))
            )
            .all()
        )

    def update(self, db: Session, *, db_obj: ChatBot, obj_in: ChatBotUpdate) -> ChatBot:
        """Actualizar chatbot"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def activate(self, db: Session, *, chat_bot_id: UUID) -> Optional[ChatBot]:
        """Activar chatbot"""
        db_obj = self.get(db, chat_bot_id)
        if db_obj:
            db_obj.activo = True
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def deactivate(self, db: Session, *, chat_bot_id: UUID) -> Optional[ChatBot]:
        """Desactivar chatbot"""
        db_obj = self.get(db, chat_bot_id)
        if db_obj:
            db_obj.activo = False
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, chat_bot_id: UUID) -> Optional[ChatBot]:
        """Eliminar chatbot"""
        obj = db.query(ChatBot).filter(ChatBot.chat_bot_id == chat_bot_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
