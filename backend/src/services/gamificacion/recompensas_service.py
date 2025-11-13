from uuid import UUID

from sqlalchemy.orm import Session

from src.models.gamification.recompensa import Recompensa
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.models.gamification.usuario_recompensa import UsuarioRecompensa


class RecompensasService:
    @staticmethod
    def canjear_recompensa(db: Session, usuario_id: UUID, recompensa_id: UUID):
        """Canjea una recompensa si el usuario tiene suficientes puntos."""
        recompensa = db.query(Recompensa).filter_by(recompensa_id=recompensa_id).first()
        if not recompensa:
            msg = "Recompensa no encontrada"
            raise ValueError(msg)
        usuario_puntos = (
            db.query(UsuarioPuntos).filter_by(usuario_id=usuario_id).first()
        )
        if (
            not usuario_puntos
            or usuario_puntos.puntos_acumulados < recompensa.costo_puntos
        ):
            msg = "No tienes suficientes puntos para canjear esta recompensa"
            raise ValueError(msg)
        # Descontar puntos
        usuario_puntos.puntos_acumulados -= recompensa.costo_puntos
        # Registrar canje
        usuario_recompensa = UsuarioRecompensa(
            usuario_id=usuario_id, recompensa_id=recompensa_id
        )
        db.add(usuario_recompensa)
        db.commit()
        db.refresh(usuario_recompensa)
        return usuario_recompensa

    @staticmethod
    def listar_tienda(db: Session, usuario_id: UUID):
        """Lista todas las recompensas y si el usuario puede canjearlas."""
        recompensas = db.query(Recompensa).all()
        usuario_puntos = (
            db.query(UsuarioPuntos).filter_by(usuario_id=usuario_id).first()
        )
        puntos = usuario_puntos.puntos_acumulados if usuario_puntos else 0
        tienda = []
        for r in recompensas:
            tienda.append(
                {
                    "recompensa_id": str(r.recompensa_id),
                    "nombre": r.nombre,
                    "descripcion": r.descripcion,
                    "costo_puntos": r.costo_puntos,
                    "tipo": r.tipo,
                    "puede_canjear": puntos >= r.costo_puntos,
                }
            )
        return tienda
