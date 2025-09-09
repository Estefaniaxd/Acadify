from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from src.models.communication.mensaje import Mensaje
from src.schemas.communication.mensaje import MensajeCreate, MensajeUpdate
from src.enums.communication.mensaje_enums import TipoMensaje


class CRUDMensaje:
    def create(self, db: Session, *, obj_in: MensajeCreate) -> Mensaje:
        """Crear nuevo mensaje"""
        # Generar UUID si no se proporciona
        mensaje_data = obj_in.dict()
        if not mensaje_data.get('mensaje_id'):
            import uuid
            mensaje_data['mensaje_id'] = uuid.uuid4()
        
        # Asegurar fecha_hora si no se proporciona    
        if not mensaje_data.get('fecha_hora'):
            mensaje_data['fecha_hora'] = datetime.now()
            
        db_obj = Mensaje(**mensaje_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, mensaje_id: UUID) -> Optional[Mensaje]:
        """Obtener mensaje por ID"""
        return db.query(Mensaje).filter(Mensaje.mensaje_id == mensaje_id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Mensaje]:
        """Obtener múltiples mensajes con paginación"""
        return (
            db.query(Mensaje)
            .order_by(desc(Mensaje.fecha_hora))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_chat_grupo(
        self, db: Session, chat_grupo_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Mensaje]:
        """Obtener mensajes por chat grupo con paginación"""
        return (
            db.query(Mensaje)
            .filter(Mensaje.chat_grupo_id == chat_grupo_id)
            .order_by(Mensaje.fecha_hora)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_emisor(self, db: Session, emisor_id: UUID) -> List[Mensaje]:
        """Obtener mensajes por emisor"""
        return (
            db.query(Mensaje)
            .filter(Mensaje.emisor_id == emisor_id)
            .order_by(desc(Mensaje.fecha_hora))
            .all()
        )

    def get_by_tipo(self, db: Session, tipo: TipoMensaje) -> List[Mensaje]:
        """Obtener mensajes por tipo"""
        return (
            db.query(Mensaje)
            .filter(Mensaje.tipo == tipo)
            .order_by(desc(Mensaje.fecha_hora))
            .all()
        )

    def get_by_date_range(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> List[Mensaje]:
        """Obtener mensajes en un rango de fechas"""
        return (
            db.query(Mensaje)
            .filter(
                Mensaje.fecha_hora >= start_date,
                Mensaje.fecha_hora <= end_date,
            )
            .order_by(desc(Mensaje.fecha_hora))
            .all()
        )

    def get_recent_messages_in_chat(
        self, db: Session, chat_grupo_id: UUID, limit: int = 50
    ) -> List[Mensaje]:
        """Obtener mensajes más recientes de un chat específico"""
        return (
            db.query(Mensaje)
            .filter(Mensaje.chat_grupo_id == chat_grupo_id)
            .order_by(desc(Mensaje.fecha_hora))
            .limit(limit)
            .all()
        )

    def search_by_content(self, db: Session, search_term: str) -> List[Mensaje]:
        """Buscar mensajes por contenido"""
        return (
            db.query(Mensaje)
            .filter(Mensaje.contenido.ilike(f"%{search_term}%"))
            .order_by(desc(Mensaje.fecha_hora))
            .all()
        )

    def get_messages_by_user_in_chat(
        self, db: Session, emisor_id: UUID, chat_grupo_id: UUID
    ) -> List[Mensaje]:
        """Obtener mensajes de un usuario específico en un chat específico"""
        return (
            db.query(Mensaje)
            .filter(
                and_(
                    Mensaje.emisor_id == emisor_id,
                    Mensaje.chat_grupo_id == chat_grupo_id
                )
            )
            .order_by(Mensaje.fecha_hora)
            .all()
        )

    def get_messages_by_type_in_chat(
        self, db: Session, tipo: TipoMensaje, chat_grupo_id: UUID
    ) -> List[Mensaje]:
        """Obtener mensajes por tipo en un chat específico"""
        return (
            db.query(Mensaje)
            .filter(
                and_(
                    Mensaje.tipo == tipo,
                    Mensaje.chat_grupo_id == chat_grupo_id
                )
            )
            .order_by(desc(Mensaje.fecha_hora))
            .all()
        )

    def get_chat_statistics(self, db: Session, chat_grupo_id: UUID) -> dict:
        """Obtener estadísticas de un chat específico"""
        # Total de mensajes
        total_messages = (
            db.query(func.count(Mensaje.mensaje_id))
            .filter(Mensaje.chat_grupo_id == chat_grupo_id)
            .scalar()
        )
        
        # Mensajes por tipo
        messages_by_type = (
            db.query(Mensaje.tipo, func.count(Mensaje.mensaje_id))
            .filter(Mensaje.chat_grupo_id == chat_grupo_id)
            .group_by(Mensaje.tipo)
            .all()
        )
        
        # Usuarios más activos
        active_users = (
            db.query(Mensaje.emisor_id, func.count(Mensaje.mensaje_id))
            .filter(
                and_(
                    Mensaje.chat_grupo_id == chat_grupo_id,
                    Mensaje.emisor_id.is_not(None)
                )
            )
            .group_by(Mensaje.emisor_id)
            .order_by(desc(func.count(Mensaje.mensaje_id)))
            .limit(10)
            .all()
        )
        
        return {
            "total_mensajes": total_messages,
            "mensajes_por_tipo": {tipo.value: count for tipo, count in messages_by_type},
            "usuarios_activos": {str(user_id): count for user_id, count in active_users}
        }

    def count_messages_by_type(self, db: Session) -> dict:
        """Contar mensajes por tipo globalmente"""
        results = (
            db.query(Mensaje.tipo, func.count(Mensaje.mensaje_id))
            .group_by(Mensaje.tipo)
            .all()
        )
        return {tipo.value: count for tipo, count in results}

    def get_most_active_chats(self, db: Session, limit: int = 10) -> List[dict]:
        """Obtener los chats más activos"""
        results = (
            db.query(Mensaje.chat_grupo_id, func.count(Mensaje.mensaje_id))
            .group_by(Mensaje.chat_grupo_id)
            .order_by(desc(func.count(Mensaje.mensaje_id)))
            .limit(limit)
            .all()
        )
        
        return [
            {"chat_grupo_id": str(chat_id), "total_mensajes": count}
            for chat_id, count in results
        ]

    def get_anonymous_messages(self, db: Session) -> List[Mensaje]:
        """Obtener mensajes sin emisor (anónimos)"""
        return (
            db.query(Mensaje)
            .filter(Mensaje.emisor_id.is_(None))
            .order_by(desc(Mensaje.fecha_hora))
            .all()
        )

    def update(
        self, db: Session, *, db_obj: Mensaje, obj_in: MensajeUpdate
    ) -> Mensaje:
        """Actualizar mensaje"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_content(
        self, db: Session, *, mensaje_id: UUID, new_content: str
    ) -> Optional[Mensaje]:
        """Actualizar solo el contenido de un mensaje"""
        db_obj = self.get(db, mensaje_id)
        if db_obj:
            db_obj.contenido = new_content
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, mensaje_id: UUID) -> Optional[Mensaje]:
        """Eliminar mensaje"""
        obj = db.query(Mensaje).filter(Mensaje.mensaje_id == mensaje_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def remove_messages_from_chat(self, db: Session, *, chat_grupo_id: UUID) -> int:
        """Eliminar todos los mensajes de un chat"""
        deleted_count = (
            db.query(Mensaje)
            .filter(Mensaje.chat_grupo_id == chat_grupo_id)
            .delete()
        )
        db.commit()
        return deleted_count

    def remove_old_messages(self, db: Session, *, older_than: datetime) -> int:
        """Eliminar mensajes más antiguos que una fecha específica"""
        deleted_count = (
            db.query(Mensaje)
            .filter(Mensaje.fecha_hora < older_than)
            .delete()
        )
        db.commit()
        return deleted_count

    def remove_messages_by_user(self, db: Session, *, emisor_id: UUID) -> int:
        """Eliminar todos los mensajes de un usuario específico"""
        deleted_count = (
            db.query(Mensaje)
            .filter(Mensaje.emisor_id == emisor_id)
            .delete()
        )
        db.commit()
        return deleted_count