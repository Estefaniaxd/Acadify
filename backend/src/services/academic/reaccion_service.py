"""Service para gestión de reacciones (likes, emojis).

SOLID + Clean Code
"""

from datetime import UTC, datetime
import logging
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.models.users.usuario import Usuario


logger = logging.getLogger(__name__)


class ReaccionService:
    """Service para gestión de reacciones."""

    # Constantes
    TIPOS_REACCION_VALIDOS = {"like", "love", "haha", "wow", "sad", "angry"}

    @staticmethod
    def agregar_reaccion(
        db: Session, comentario_id: str, tipo_reaccion: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Agrega o actualiza una reacción a un comentario.

        Args:
            db: Sesión de BD
            comentario_id: ID del comentario
            tipo_reaccion: Tipo (like, love, haha, wow, sad, angry)
            usuario: Usuario que reacciona

        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validaciones
            ReaccionService._validar_tipo_reaccion(tipo_reaccion)
            ReaccionService._validar_acceso_comentario(db, comentario_id, usuario)

            # Verificar si ya reaccionó
            existe = ReaccionService._obtener_reaccion_existente(
                db, comentario_id, usuario.usuario_id
            )

            if existe:
                # Actualizar
                ReaccionService._actualizar_reaccion(
                    db, existe["reaccion_id"], tipo_reaccion
                )
                mensaje = "Reacción actualizada"
            else:
                # Crear nueva
                ReaccionService._crear_reaccion(
                    db, comentario_id, tipo_reaccion, usuario.usuario_id
                )
                mensaje = "Reacción agregada"

            # Obtener estadísticas actualizadas
            stats = ReaccionService._obtener_estadisticas(db, comentario_id)

            logger.info(
                f"Reacción '{tipo_reaccion}' de usuario {usuario.usuario_id} en comentario {comentario_id}"
            )

            return {
                "success": True,
                "message": mensaje,
                "data": {"tipo_reaccion": tipo_reaccion, "estadisticas": stats},
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error agregando reacción: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al agregar reacción: {e!s}",
            ) from e

    @staticmethod
    def eliminar_reaccion(
        db: Session, comentario_id: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Elimina la reacción de un usuario."""
        try:
            ReaccionService._validar_acceso_comentario(db, comentario_id, usuario)

            query = text(
                """
                DELETE FROM reacciones
                WHERE comentario_id = :comentario_id
                    AND usuario_id = :usuario_id
            """
            )

            result = db.execute(
                query,
                {"comentario_id": comentario_id, "usuario_id": usuario.usuario_id},
            )

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No tienes reacción en este comentario",
                )

            db.commit()

            stats = ReaccionService._obtener_estadisticas(db, comentario_id)

            logger.info(
                f"Reacción eliminada de comentario {comentario_id} por usuario {usuario.usuario_id}"
            )

            return {
                "success": True,
                "message": "Reacción eliminada",
                "data": {"estadisticas": stats},
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error eliminando reacción: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar reacción",
            ) from e

    @staticmethod
    def obtener_reacciones(
        db: Session, comentario_id: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Obtiene todas las reacciones de un comentario."""
        try:
            ReaccionService._validar_acceso_comentario(db, comentario_id, usuario)

            query = text(
                """
                SELECT
                    r.tipo_reaccion,
                    r.fecha_reaccion,
                    u.nombres || ' ' || u.apellidos as usuario,
                    r.usuario_id = :usuario_id as es_mi_reaccion
                FROM reacciones r
                JOIN "Usuario" u ON r.usuario_id = u.usuario_id
                WHERE r.comentario_id = :comentario_id
                ORDER BY r.fecha_reaccion DESC
            """
            )

            result = db.execute(
                query,
                {"comentario_id": comentario_id, "usuario_id": usuario.usuario_id},
            ).fetchall()

            reacciones = [dict(row._mapping) for row in result]
            stats = ReaccionService._obtener_estadisticas(db, comentario_id)

            return {
                "success": True,
                "data": {
                    "reacciones": reacciones,
                    "estadisticas": stats,
                    "total": len(reacciones),
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo reacciones: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al obtener reacciones",
            ) from e

    # ========== MÉTODOS PRIVADOS ==========

    @staticmethod
    def _validar_tipo_reaccion(tipo: str) -> None:
        """Valida el tipo de reacción."""
        if tipo not in ReaccionService.TIPOS_REACCION_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de reacción inválido. Válidos: {', '.join(ReaccionService.TIPOS_REACCION_VALIDOS)}",
            )

    @staticmethod
    def _validar_acceso_comentario(
        db: Session, comentario_id: str, usuario: Usuario
    ) -> None:
        """Valida que el usuario tenga acceso al comentario."""
        query = text(
            """
            SELECT c.curso_id
            FROM comentarios c
            WHERE c.comentario_id = :comentario_id
        """
        )

        result = db.execute(query, {"comentario_id": comentario_id}).fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado"
            )

        curso_id = result[0]

        from src.services.academic.curso_service import CursoService

        if not CursoService._usuario_tiene_acceso(db, curso_id, usuario):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este curso",
            )

    @staticmethod
    def _obtener_reaccion_existente(
        db: Session, comentario_id: str, usuario_id
    ) -> dict[str, Any] | None:
        """Obtiene reacción existente del usuario."""
        query = text(
            """
            SELECT reaccion_id, tipo_reaccion
            FROM reacciones
            WHERE comentario_id = :comentario_id
                AND usuario_id = :usuario_id
        """
        )

        result = db.execute(
            query, {"comentario_id": comentario_id, "usuario_id": usuario_id}
        ).fetchone()

        return dict(result._mapping) if result else None

    @staticmethod
    def _crear_reaccion(
        db: Session, comentario_id: str, tipo_reaccion: str, usuario_id
    ) -> None:
        """Crea nueva reacción."""
        query = text(
            """
            INSERT INTO reacciones (comentario_id, usuario_id, tipo_reaccion, fecha_reaccion)
            VALUES (:comentario_id, :usuario_id, :tipo_reaccion, :fecha_reaccion)
        """
        )

        db.execute(
            query,
            {
                "comentario_id": comentario_id,
                "usuario_id": usuario_id,
                "tipo_reaccion": tipo_reaccion,
                "fecha_reaccion": datetime.now(UTC),
            },
        )
        db.commit()

    @staticmethod
    def _actualizar_reaccion(db: Session, reaccion_id: str, tipo_reaccion: str) -> None:
        """Actualiza reacción existente."""
        query = text(
            """
            UPDATE reacciones
            SET tipo_reaccion = :tipo_reaccion,
                fecha_reaccion = :fecha_reaccion
            WHERE reaccion_id = :reaccion_id
        """
        )

        db.execute(
            query,
            {
                "reaccion_id": reaccion_id,
                "tipo_reaccion": tipo_reaccion,
                "fecha_reaccion": datetime.now(UTC),
            },
        )
        db.commit()

    @staticmethod
    def _obtener_estadisticas(db: Session, comentario_id: str) -> dict[str, int]:
        """Obtiene estadísticas de reacciones."""
        query = text(
            """
            SELECT tipo_reaccion, COUNT(*) as cantidad
            FROM reacciones
            WHERE comentario_id = :comentario_id
            GROUP BY tipo_reaccion
        """
        )

        result = db.execute(query, {"comentario_id": comentario_id}).fetchall()

        stats = dict.fromkeys(ReaccionService.TIPOS_REACCION_VALIDOS, 0)
        for row in result:
            stats[row.tipo_reaccion] = row.cantidad

        stats["total"] = sum(stats.values())

        return stats


# Instancia global
reaccion_service = ReaccionService()
