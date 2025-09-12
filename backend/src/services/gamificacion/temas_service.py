from sqlalchemy.orm import Session
from uuid import UUID
from src.models.gamification.tema import Tema
from src.models.gamification.tema_personalizado import TemaPersonalizado
from src.models.gamification.usuario_puntos import UsuarioPuntos

class TemasService:
    @staticmethod
    def comprar_tema(db: Session, usuario_id: UUID, tema_id: UUID, costo: int = 10):
        """
        Permite comprar y asignar un tema personalizado al usuario si tiene suficientes puntos.
        """
        tema = db.query(Tema).filter_by(tema_id=tema_id).first()
        if not tema:
            raise ValueError("Tema no encontrado")
        usuario_puntos = db.query(UsuarioPuntos).filter_by(usuario_id=usuario_id).first()
        if not usuario_puntos or usuario_puntos.puntos_acumulados < costo:
            raise ValueError("No tienes suficientes puntos para comprar este tema")
        # Verificar que el usuario no tenga ya el tema
        ya_tiene = db.query(TemaPersonalizado).filter_by(usuario_id=usuario_id, tema_id=tema_id).first()
        if ya_tiene:
            raise ValueError("Ya tienes este tema")
        usuario_puntos.puntos_acumulados -= costo
        tema_personalizado = TemaPersonalizado(usuario_id=usuario_id, tema_id=tema_id)
        db.add(tema_personalizado)
        db.commit()
        db.refresh(tema_personalizado)
        return tema_personalizado

    @staticmethod
    def listar_temas_disponibles(db: Session, usuario_id: UUID):
        """
        Lista los temas que el usuario aún no ha comprado.
        """
        subq = db.query(TemaPersonalizado.tema_id).filter_by(usuario_id=usuario_id)
        temas = db.query(Tema).filter(~Tema.tema_id.in_(subq)).all()
        return temas
