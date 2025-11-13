from uuid import UUID

from sqlalchemy.orm import Session

from src.models.gamification.insignia import Insignia
from src.models.gamification.usuario_insignia import UsuarioInsignia


class InsigniasService:
    @staticmethod
    def otorgar_insignia(
        db: Session,
        usuario_id: UUID,
        insignia_id: UUID,
        otorgada_por: UUID | None = None,
    ):
        """Asigna una insignia a un usuario si no la tiene (si es única)."""
        insignia = db.query(Insignia).filter_by(insignia_id=insignia_id).first()
        if not insignia:
            msg = "Insignia no encontrada"
            raise ValueError(msg)
        # Si es única, verificar que no la tenga
        if insignia.es_unica:
            existe = (
                db.query(UsuarioInsignia)
                .filter_by(usuario_id=usuario_id, insignia_id=insignia_id)
                .first()
            )
            if existe:
                msg = "El usuario ya tiene esta insignia única"
                raise ValueError(msg)
        usuario_insignia = UsuarioInsignia(
            usuario_id=usuario_id, insignia_id=insignia_id, otorgada_por=otorgada_por
        )
        db.add(usuario_insignia)
        db.commit()
        db.refresh(usuario_insignia)
        return usuario_insignia

    @staticmethod
    def revocar_insignia(db: Session, usuario_id: UUID, insignia_id: UUID) -> bool:
        """Quita una insignia a un usuario."""
        usuario_insignia = (
            db.query(UsuarioInsignia)
            .filter_by(usuario_id=usuario_id, insignia_id=insignia_id)
            .first()
        )
        if not usuario_insignia:
            msg = "El usuario no tiene esta insignia"
            raise ValueError(msg)
        db.delete(usuario_insignia)
        db.commit()
        return True
