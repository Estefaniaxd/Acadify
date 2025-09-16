from typing import Optional
from sqlalchemy.orm import Session
from src.models.communication.archivo_chat import ArchivoChat
from src.schemas.communication.archivo_chat import (
    ArchivoChatCreate,
    ArchivoChatUpdate,
)


class CRUDArchivoChat:
    def get_by_nombre(
        self, db: Session, *, nombre_archivo: str
    ) -> Optional[ArchivoChat]:
        return (
            db.query(ArchivoChat)
            .filter(ArchivoChat.nombre_archivo == nombre_archivo)
            .first()
        )

    def get_by_usuario(self, db: Session, *, usuario_id: str) -> list[ArchivoChat]:
        return db.query(ArchivoChat).filter(ArchivoChat.usuario_id == usuario_id).all()

    def get_by_chat(self, db: Session, *, chat_grupo_id: str) -> list[ArchivoChat]:
        return (
            db.query(ArchivoChat)
            .filter(ArchivoChat.chat_grupo_id == chat_grupo_id)
            .all()
        )


archivo_chat = CRUDArchivoChat(ArchivoChat)
