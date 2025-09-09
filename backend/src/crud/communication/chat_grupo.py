# crud/chat_grupo.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.communication.chat_grupo import ChatGrupo
from src.schemas.communication.chat_grupo import ChatGrupoCreate, ChatGrupoUpdate
from src.enums.communication.chat_grupo_enums import EstadoChatGrupo


class CRUDChatGrupo:
    def create(self, db: Session, *, obj_in: ChatGrupoCreate) -> ChatGrupo:
        """Crear nuevo chat de grupo"""
        db_obj = ChatGrupo(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, chat_grupo_id: UUID) -> Optional[ChatGrupo]:
        """Obtener chat de grupo por ID"""
        return (
            db.query(ChatGrupo).filter(ChatGrupo.chat_grupo_id == chat_grupo_id).first()
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ChatGrupo]:
        """Obtener múltiples chats de grupo con paginación"""
        return db.query(ChatGrupo).offset(skip).limit(limit).all()

    def get_by_grupo(self, db: Session, grupo_id: UUID) -> Optional[ChatGrupo]:
        """Obtener chat por grupo (relación uno a uno)"""
        return db.query(ChatGrupo).filter(ChatGrupo.grupo_id == grupo_id).first()

    def get_by_estado(self, db: Session, estado: EstadoChatGrupo) -> List[ChatGrupo]:
        """Obtener chats por estado"""
        return db.query(ChatGrupo).filter(ChatGrupo.estado_chat == estado).all()

    def get_active_chats(self, db: Session) -> List[ChatGrupo]:
        """Obtener chats activos"""
        return (
            db.query(ChatGrupo)
            .filter(ChatGrupo.estado_chat == EstadoChatGrupo.activo)
            .all()
        )

    def get_archived_chats(self, db: Session) -> List[ChatGrupo]:
        """Obtener chats archivados"""
        return (
            db.query(ChatGrupo)
            .filter(ChatGrupo.estado_chat == EstadoChatGrupo.archivado)
            .all()
        )

    def get_by_date_range(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> List[ChatGrupo]:
        """Obtener chats creados en un rango de fechas"""
        return (
            db.query(ChatGrupo)
            .filter(
                ChatGrupo.fecha_creacion >= start_date,
                ChatGrupo.fecha_creacion <= end_date,
            )
            .order_by(ChatGrupo.fecha_creacion.desc())
            .all()
        )

    def get_chats_with_files_allowed(self, db: Session) -> List[ChatGrupo]:
        """Obtener chats que permiten archivos"""
        return db.query(ChatGrupo).filter(ChatGrupo.permite_archivos == True).all()

    def get_chats_by_storage_capacity(
        self, db: Session, min_capacity: int, max_capacity: int = None
    ) -> List[ChatGrupo]:
        """Obtener chats por capacidad de almacenamiento"""
        query = db.query(ChatGrupo).filter(
            ChatGrupo.capacidad_almacenamiento >= min_capacity
        )
        if max_capacity:
            query = query.filter(ChatGrupo.capacidad_almacenamiento <= max_capacity)
        return query.all()

    def get_recent_chats(self, db: Session, limit: int = 10) -> List[ChatGrupo]:
        """Obtener chats más recientes"""
        return (
            db.query(ChatGrupo)
            .order_by(ChatGrupo.fecha_creacion.desc())
            .limit(limit)
            .all()
        )

    def update(
        self, db: Session, *, db_obj: ChatGrupo, obj_in: ChatGrupoUpdate
    ) -> ChatGrupo:
        """Actualizar chat de grupo"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def archive_chat(self, db: Session, *, chat_grupo_id: UUID) -> Optional[ChatGrupo]:
        """Archivar chat"""
        db_obj = self.get(db, chat_grupo_id)
        if db_obj:
            db_obj.estado_chat = EstadoChatGrupo.archivado
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def activate_chat(self, db: Session, *, chat_grupo_id: UUID) -> Optional[ChatGrupo]:
        """Activar chat"""
        db_obj = self.get(db, chat_grupo_id)
        if db_obj:
            db_obj.estado_chat = EstadoChatGrupo.activo
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def update_storage_capacity(
        self, db: Session, *, chat_grupo_id: UUID, new_capacity: int
    ) -> Optional[ChatGrupo]:
        """Actualizar capacidad de almacenamiento"""
        db_obj = self.get(db, chat_grupo_id)
        if db_obj:
            db_obj.capacidad_almacenamiento = new_capacity
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def toggle_file_permissions(
        self, db: Session, *, chat_grupo_id: UUID
    ) -> Optional[ChatGrupo]:
        """Alternar permisos de archivos"""
        db_obj = self.get(db, chat_grupo_id)
        if db_obj:
            db_obj.permite_archivos = not db_obj.permite_archivos
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, chat_grupo_id: UUID) -> Optional[ChatGrupo]:
        """Eliminar chat de grupo"""
        obj = (
            db.query(ChatGrupo).filter(ChatGrupo.chat_grupo_id == chat_grupo_id).first()
        )
        if obj:
            db.delete(obj)
            db.commit()
        return obj
