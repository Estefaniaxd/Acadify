from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from src.crud.base import CRUDMensajeBot
from src.enums.communication.mensaje_bots_enum import ContextoMensaje
from src.models.communication.mensaje_bot import MensajeBot
from src.schemas.communication.mensaje_bot import MensajeBotCreate, MensajeBotUpdate


class CRUDMensajeBot(CRUDMensajeBot[MensajeBot, MensajeBotCreate, MensajeBotUpdate]):
    def create(self, db: Session, *, obj_in: MensajeBotCreate) -> MensajeBot:
        """Crear nuevo mensaje de bot."""
        # Asegurar que fecha_hora se establezca si no se proporciona
        mensaje_data = obj_in.model_dump()
        if not mensaje_data.get("fecha_hora"):
            mensaje_data["fecha_hora"] = datetime.now(UTC)

        db_obj = MensajeBot(**mensaje_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, mensaje_bot_id: UUID) -> MensajeBot | None:
        """Obtener mensaje bot por ID."""
        return (
            db.query(MensajeBot)
            .filter(MensajeBot.mensaje_bot_id == mensaje_bot_id)
            .first()
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[MensajeBot]:
        """Obtener múltiples mensajes bot con paginación."""
        return (
            db.query(MensajeBot)
            .order_by(desc(MensajeBot.fecha_hora))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_usuario(self, db: Session, usuario_id: UUID) -> list[MensajeBot]:
        """Obtener mensajes bot por usuario."""
        return (
            db.query(MensajeBot)
            .filter(MensajeBot.usuario_id == usuario_id)
            .order_by(desc(MensajeBot.fecha_hora))
            .all()
        )

    def get_by_chat_grupo(self, db: Session, chat_grupo_id: UUID) -> list[MensajeBot]:
        """Obtener mensajes bot por chat grupo."""
        return (
            db.query(MensajeBot)
            .filter(MensajeBot.chat_grupo_id == chat_grupo_id)
            .order_by(MensajeBot.fecha_hora)
            .all()
        )

    def get_by_material_educativo(
        self, db: Session, material_id: UUID
    ) -> list[MensajeBot]:
        """Obtener mensajes bot relacionados con material educativo."""
        return (
            db.query(MensajeBot)
            .filter(MensajeBot.referencia_material_id == material_id)
            .order_by(desc(MensajeBot.fecha_hora))
            .all()
        )

    def get_by_contexto(
        self, db: Session, contexto: ContextoMensaje
    ) -> list[MensajeBot]:
        """Obtener mensajes bot por contexto."""
        return (
            db.query(MensajeBot)
            .filter(MensajeBot.contexto == contexto)
            .order_by(desc(MensajeBot.fecha_hora))
            .all()
        )

    def get_by_date_range(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> list[MensajeBot]:
        """Obtener mensajes bot en un rango de fechas."""
        return (
            db.query(MensajeBot)
            .filter(
                MensajeBot.fecha_hora >= start_date,
                MensajeBot.fecha_hora <= end_date,
            )
            .order_by(desc(MensajeBot.fecha_hora))
            .all()
        )

    def get_recent_messages(self, db: Session, limit: int = 50) -> list[MensajeBot]:
        """Obtener mensajes bot más recientes."""
        return (
            db.query(MensajeBot)
            .order_by(desc(MensajeBot.fecha_hora))
            .limit(limit)
            .all()
        )

    def search_by_content(self, db: Session, search_term: str) -> list[MensajeBot]:
        """Buscar mensajes bot por contenido o respuesta."""
        return (
            db.query(MensajeBot)
            .filter(
                or_(
                    MensajeBot.contenido.ilike(f"%{search_term}%"),
                    MensajeBot.respuesta.ilike(f"%{search_term}%"),
                )
            )
            .order_by(desc(MensajeBot.fecha_hora))
            .all()
        )

    def get_conversation_history(
        self, db: Session, usuario_id: UUID, chat_grupo_id: UUID, limit: int = 100
    ) -> list[MensajeBot]:
        """Obtener historial de conversación de un usuario en un chat específico."""
        return (
            db.query(MensajeBot)
            .filter(
                and_(
                    MensajeBot.usuario_id == usuario_id,
                    MensajeBot.chat_grupo_id == chat_grupo_id,
                )
            )
            .order_by(MensajeBot.fecha_hora)
            .limit(limit)
            .all()
        )

    def get_messages_by_context_and_chat(
        self, db: Session, contexto: ContextoMensaje, chat_grupo_id: UUID
    ) -> list[MensajeBot]:
        """Obtener mensajes por contexto en un chat específico."""
        return (
            db.query(MensajeBot)
            .filter(
                and_(
                    MensajeBot.contexto == contexto,
                    MensajeBot.chat_grupo_id == chat_grupo_id,
                )
            )
            .order_by(desc(MensajeBot.fecha_hora))
            .all()
        )

    def get_unanswered_messages(self, db: Session) -> list[MensajeBot]:
        """Obtener mensajes sin respuesta (respuesta vacía o nula)."""
        return (
            db.query(MensajeBot)
            .filter(or_(MensajeBot.respuesta.is_(None), MensajeBot.respuesta == ""))
            .order_by(MensajeBot.fecha_hora)
            .all()
        )

    def count_messages_by_context(self, db: Session) -> dict:
        """Contar mensajes por contexto."""
        results = (
            db.query(MensajeBot.contexto, func.count(MensajeBot.mensaje_bot_id))
            .group_by(MensajeBot.contexto)
            .all()
        )
        return {contexto.value: count for contexto, count in results}

    def count_messages_by_user(self, db: Session, limit: int = 10) -> dict:
        """Contar mensajes por usuario (top usuarios más activos)."""
        results = (
            db.query(MensajeBot.usuario_id, func.count(MensajeBot.mensaje_bot_id))
            .filter(MensajeBot.usuario_id.is_not(None))
            .group_by(MensajeBot.usuario_id)
            .order_by(desc(func.count(MensajeBot.mensaje_bot_id)))
            .limit(limit)
            .all()
        )
        return {str(usuario_id): count for usuario_id, count in results}

    def update(
        self, db: Session, *, db_obj: MensajeBot, obj_in: MensajeBotUpdate
    ) -> MensajeBot:
        """Actualizar mensaje bot."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_response(
        self, db: Session, *, mensaje_bot_id: UUID, new_response: str
    ) -> MensajeBot | None:
        """Actualizar solo la respuesta de un mensaje bot."""
        db_obj = self.get(db, mensaje_bot_id)
        if db_obj:
            db_obj.respuesta = new_response
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, mensaje_bot_id: UUID) -> MensajeBot | None:
        """Eliminar mensaje bot."""
        obj = (
            db.query(MensajeBot)
            .filter(MensajeBot.mensaje_bot_id == mensaje_bot_id)
            .first()
        )
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def remove_old_messages(self, db: Session, *, older_than: datetime) -> int:
        """Eliminar mensajes más antiguos que una fecha específica."""
        deleted_count = (
            db.query(MensajeBot).filter(MensajeBot.fecha_hora < older_than).delete()
        )
        db.commit()
        return deleted_count


mensaje_bot = CRUDMensajeBot(MensajeBot)
