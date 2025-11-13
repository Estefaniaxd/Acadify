from uuid import UUID

from sqlalchemy.orm import Session

from src.models.gamification.historial_puntos import HistorialPuntos
from src.models.gamification.racha_usuario import RachaUsuario
from src.models.gamification.usuario_puntos import UsuarioPuntos


class PuntosService:
    @staticmethod
    def asignar_puntos(
        db: Session, usuario_id: UUID, puntos: int, motivo: str | None = None
    ):
        """Suma puntos al usuario, registra historial y actualiza racha."""
        usuario_puntos = (
            db.query(UsuarioPuntos).filter_by(usuario_id=usuario_id).first()
        )
        if not usuario_puntos:
            usuario_puntos = UsuarioPuntos(usuario_id=usuario_id, puntos_acumulados=0)
            db.add(usuario_puntos)
        usuario_puntos.puntos_acumulados += puntos
        db.add(HistorialPuntos(usuario_id=usuario_id, cambio=puntos, motivo=motivo))
        db.commit()
        db.refresh(usuario_puntos)
        PuntosService.actualizar_racha(db, usuario_id)
        return usuario_puntos

    @staticmethod
    def descontar_puntos(
        db: Session, usuario_id: UUID, puntos: int, motivo: str | None = None
    ):
        """Resta puntos al usuario, registra historial."""
        usuario_puntos = (
            db.query(UsuarioPuntos).filter_by(usuario_id=usuario_id).first()
        )
        if not usuario_puntos or usuario_puntos.puntos_acumulados < puntos:
            msg = "El usuario no tiene suficientes puntos"
            raise ValueError(msg)
        usuario_puntos.puntos_acumulados -= puntos
        db.add(HistorialPuntos(usuario_id=usuario_id, cambio=-puntos, motivo=motivo))
        db.commit()
        db.refresh(usuario_puntos)
        return usuario_puntos

    @staticmethod
    def actualizar_racha(db: Session, usuario_id: UUID):
        """Actualiza la racha diaria del usuario. Si el usuario ya participó hoy, no suma. Si es día consecutivo, suma. Si no, reinicia."""
        from datetime import date, timedelta

        hoy = date.today()
        racha = db.query(RachaUsuario).filter_by(usuario_id=usuario_id).first()
        if not racha:
            racha = RachaUsuario(
                usuario_id=usuario_id,
                racha_actual=1,
                mejor_racha=1,
                fecha_ultimo_dia=hoy,
            )
            db.add(racha)
        else:
            if racha.fecha_ultimo_dia == hoy:
                return None  # Ya se contó hoy
            if racha.fecha_ultimo_dia == hoy - timedelta(days=1):
                racha.racha_actual += 1
            else:
                racha.racha_actual = 1
            racha.mejor_racha = max(racha.mejor_racha, racha.racha_actual)
            racha.fecha_ultimo_dia = hoy
        db.commit()
        db.refresh(racha)
        return racha

    @staticmethod
    def obtener_racha(db: Session, usuario_id: UUID) -> int:
        racha = db.query(RachaUsuario).filter_by(usuario_id=usuario_id).first()
        return racha.racha_actual if racha else 0
