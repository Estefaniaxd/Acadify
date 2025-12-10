"""Service para gestión de reacciones (likes, emojis).

SOLID + Clean Code
"""

from datetime import UTC, datetime
import logging
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.models.users.usuario import Usuario


logger = logging.getLogger(__name__)


class ReaccionService:
    """Service para gestión de reacciones."""



    @staticmethod
    def agregar_reaccion(
        db: Session, comentario_id: str, tipo_reaccion: str | None, usuario: Usuario, emoji: str = None, action: str = None
    ) -> dict[str, Any]:
        """Agrega o actualiza una reacción a un comentario. Ahora permite cualquier emoji y tipo_reaccion opcional."""
        try:
            logger.warning(f"[DEBUG] agregar_reaccion: comentario_id={comentario_id}, usuario_id={getattr(usuario, 'usuario_id', None)}, tipo_reaccion={tipo_reaccion}, emoji={emoji}, action={action}")
            # Validaciones
            try:
                ReaccionService._validar_acceso_comentario(db, comentario_id, usuario)
            except Exception as e:
                logger.error(f"[ERROR] _validar_acceso_comentario fallo: {e!s}")
                raise

            # Usar emoji si se proporciona, sino usar tipo como emoji
            emoji_final = emoji or tipo_reaccion or "like"

            logger.warning(f"[DEBUG] emoji_final={emoji_final}")
            # Verificar si ya reaccionó con este emoji
            existe = ReaccionService._obtener_reaccion_existente_emoji(
                db, comentario_id, usuario.usuario_id, emoji_final
            )
            logger.warning(f"[DEBUG] existing reaction check result: {existe}")

            if existe:
                if action == 'add':
                    logger.info(f"Intento de agregar reacción duplicada: comentario_id={comentario_id} usuario={usuario.usuario_id} emoji={emoji_final}")
                    mensaje = "Reacción ya existe"
                    act = "noop_add"
                elif action == 'remove':
                    logger.warning(f"[DEBUG] Removing existing reaction id={existe.get('reaccion_id')} for user={usuario.usuario_id} (intent remove)")
                    ReaccionService._eliminar_reaccion_por_id(db, existe["reaccion_id"])
                    mensaje = "Reacción eliminada"
                    act = "removed"
                else:
                    logger.warning(f"[DEBUG] Removing existing reaction id={existe.get('reaccion_id')} for user={usuario.usuario_id} (toggle)")
                    ReaccionService._eliminar_reaccion_por_id(db, existe["reaccion_id"])
                    mensaje = "Reacción eliminada"
                    act = "removed"
            else:
                if action == 'remove':
                    logger.info(f"Intento de eliminar reacción inexistente: comentario_id={comentario_id} usuario={usuario.usuario_id} emoji={emoji_final}")
                    mensaje = "Reacción ya eliminada"
                    act = "noop_remove"
                else:
                    logger.warning(f"[DEBUG] Creating reaction emoji={emoji_final} for user={usuario.usuario_id} comment={comentario_id}")
                    try:
                        ReaccionService._crear_reaccion_emoji(
                            db, comentario_id, tipo_reaccion or emoji_final, emoji_final, usuario.usuario_id
                        )
                    except Exception as e:
                        logger.error(f"[ERROR] _crear_reaccion_emoji fallo: {e!s}")
                        raise
                    # Verify the insert actually created a record; if not, mark as failed
                    existe_despues = ReaccionService._obtener_reaccion_existente_emoji(
                        db, comentario_id, usuario.usuario_id, emoji_final
                    )
                    if existe_despues:
                        mensaje = "Reacción agregada"
                        act = "created"
                    else:
                        logger.error(f"[ERROR] crear_reaccion_emoji reported no error but reaction not found after insert: comentario={comentario_id} usuario={usuario.usuario_id} emoji={emoji_final}")
                        # Diagnostic: list any reactions present for this user/comment to aid debugging
                        try:
                            diag_q = text(
                                """
                                SELECT reaccion_id, tipo, emoji, fecha_creacion
                                FROM "Reacciones"
                                WHERE comentario_id = :comentario_id AND usuario_id = :usuario_id
                                ORDER BY fecha_creacion DESC
                                """
                            )
                            rows = db.execute(diag_q, {"comentario_id": comentario_id, "usuario_id": usuario.usuario_id}).fetchall()
                            diag = [dict(r._mapping) for r in rows]
                            logger.error(f"[DIAG] Reacciones existentes para comentario/usuario: {diag}")
                        except Exception as ex:
                            logger.exception(f"[DIAG] fallo al consultar diagnostico de reacciones: {ex!s}")
                        mensaje = "Error al agregar reacción"
                        act = "failed"

            # Obtener estadísticas actualizadas
            try:
                stats = ReaccionService._obtener_estadisticas(db, comentario_id)
            except Exception as e:
                logger.error(f"[ERROR] _obtener_estadisticas fallo: {e!s}")
                stats = None

            logger.warning(f"[DEBUG] Reacción '{emoji_final}' de usuario {usuario.usuario_id} en comentario {comentario_id}: {act}")

            # Obtener lista canónica de reacciones para devolver al cliente y facilitar sincronización
            try:
                reacciones_resp = ReaccionService.obtener_reacciones(db, comentario_id, usuario)
                reacciones_list = reacciones_resp.get("data") if isinstance(reacciones_resp, dict) else None
            except Exception as e:
                logger.error(f"[ERROR] obtener_reacciones fallo: {e!s}")
                reacciones_list = None

            logger.warning(f"[DEBUG] Returning stats count={len(stats) if isinstance(stats, dict) else 'n/a'} reacciones_len={len(reacciones_list) if reacciones_list else 0}")

            success_flag = act != 'failed'
            return {
                "success": success_flag,
                "message": mensaje,
                "data": {"tipo_reaccion": tipo_reaccion, "emoji": emoji_final, "estadisticas": stats},
                "reacciones": reacciones_list,
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"[ERROR] Error agregando reacción: {e!s}")
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
            logger.debug(f"eliminar_reaccion called: comentario_id={comentario_id} usuario={usuario.usuario_id}")
            ReaccionService._validar_acceso_comentario(db, comentario_id, usuario)

            query = text(
                """
                DELETE FROM "Reacciones"
                WHERE comentario_id = :comentario_id
                    AND usuario_id = :usuario_id
                """
            )

            result = db.execute(
                query,
                {"comentario_id": comentario_id, "usuario_id": usuario.usuario_id},
            )

            logger.debug(f"delete result rowcount={result.rowcount}")
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

            # also return canonical reacciones list to help frontend sync
            try:
                reacciones_resp = ReaccionService.obtener_reacciones(db, comentario_id, usuario)
                reacciones_list = reacciones_resp.get("data") if isinstance(reacciones_resp, dict) else None
            except Exception:
                reacciones_list = None

            return {
                "success": True,
                "message": "Reacción eliminada",
                "data": {"estadisticas": stats},
                "reacciones": reacciones_list,
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
        """Obtiene todas las reacciones de un comentario agrupadas por emoji."""
        try:
            ReaccionService._validar_acceso_comentario(db, comentario_id, usuario)

            # Query para obtener reacciones agrupadas por emoji
            query = text(
                """
                SELECT
                    COALESCE(r.emoji, r.tipo) as emoji,
                    COUNT(*) as cantidad,
                    ARRAY_AGG(
                        JSON_BUILD_OBJECT(
                            'usuario_id', u.usuario_id,
                            'usuario_nombre', u.nombres || ' ' || u.apellidos,
                            'fecha', r.fecha_creacion,
                            'reaccion_id', r.reaccion_id
                        )
                    ) as usuarios
                FROM "Reacciones" r
                JOIN "Usuario" u ON r.usuario_id = u.usuario_id
                WHERE r.comentario_id = :comentario_id
                GROUP BY COALESCE(r.emoji, r.tipo)
                ORDER BY COUNT(*) DESC, COALESCE(r.emoji, r.tipo)
                """
            )

            result = db.execute(query, {"comentario_id": comentario_id}).fetchall()

            # Convertir a formato esperado por frontend
            reacciones = []
            for row in result:
                reacciones.append({
                    "emoji": row.emoji,
                    "cantidad": row.cantidad,
                    "usuarios": row.usuarios
                })

            return {
                "success": True,
                "data": reacciones,
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

    # _validar_tipo_reaccion eliminado: ahora se permite cualquier tipo/emoji

    @staticmethod
    def _validar_acceso_comentario(
        db: Session, comentario_id: str, usuario: Usuario
    ) -> None:
        """Valida que el usuario tenga acceso al comentario."""
        query = text(
            """
            SELECT c.curso_id
            FROM "Comentario" c
            WHERE c.comentario_id = :comentario_id
        """
        )

        try:
            result = db.execute(query, {"comentario_id": comentario_id}).fetchone()
        except Exception:
            # Si falla (ej. UUID inválido), asumimos que no existe
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado (ID inválido)"
            )

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
            SELECT reaccion_id, tipo
            FROM "Reacciones"
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
        reaccion_id = str(uuid4())
        query = text(
            """
            INSERT INTO "Reacciones" (reaccion_id, comentario_id, usuario_id, tipo, fecha_creacion, activo, emoji)
            VALUES (:reaccion_id, :comentario_id, :usuario_id, :tipo, :fecha_creacion, true, :emoji)
            """
        )
        try:
            db.execute(
                query,
                {
                    "reaccion_id": reaccion_id,
                    "comentario_id": comentario_id,
                    "usuario_id": usuario_id,
                    "tipo": tipo_reaccion,
                    "fecha_creacion": datetime.now(UTC),
                    "emoji": tipo_reaccion,
                },
            )
            db.commit()
            logger.debug(f"_crear_reaccion: created tipo_reaccion={tipo_reaccion} comentario_id={comentario_id} usuario_id={usuario_id}")
        except Exception as e:
            logger.warning(f"_crear_reaccion fallo: {e!s}")
            try:
                db.rollback()
            except Exception:
                pass

    @staticmethod
    def _actualizar_reaccion(db: Session, reaccion_id: str, tipo_reaccion: str) -> None:
        """Actualiza reacción existente."""
        query = text(
            """
            UPDATE "Reacciones"
            SET tipo = :tipo,
                fecha_creacion = :fecha_creacion
            WHERE reaccion_id = :reaccion_id
            """
        )
        db.execute(
            query,
            {
                "reaccion_id": reaccion_id,
                "tipo": tipo_reaccion,
                "fecha_creacion": datetime.now(UTC),
            },
        )
        db.commit()

    @staticmethod
    def _obtener_reaccion_existente_emoji(
        db: Session, comentario_id: str, usuario_id: str, emoji: str
    ) -> dict[str, Any] | None:
        """Obtiene reacción existente del usuario para un emoji específico."""
        query = text(
            """
            SELECT reaccion_id, tipo, emoji
            FROM "Reacciones"
            WHERE comentario_id = :comentario_id
                AND usuario_id = :usuario_id
                AND COALESCE(emoji, tipo) = :emoji
            """
        )

        result = db.execute(
            query, {"comentario_id": comentario_id, "usuario_id": usuario_id, "emoji": emoji}
        ).fetchone()

        return dict(result._mapping) if result else None

    @staticmethod
    def _crear_reaccion_emoji(
        db: Session, comentario_id: str, tipo_reaccion: str, emoji: str, usuario_id: str
    ) -> None:
        """Crea nueva reacción con emoji."""
        reaccion_id = str(uuid4())
        query = text(
            """
            INSERT INTO "Reacciones" (reaccion_id, comentario_id, usuario_id, tipo, fecha_creacion, activo, emoji)
            VALUES (:reaccion_id, :comentario_id, :usuario_id, :tipo, :fecha_creacion, true, :emoji)
            """
        )
        try:
            db.execute(
                query,
                {
                    "reaccion_id": reaccion_id,
                    "comentario_id": comentario_id,
                    "usuario_id": usuario_id,
                    "tipo": tipo_reaccion,
                    "fecha_creacion": datetime.now(UTC),
                    "emoji": emoji,
                },
            )
            db.commit()
            logger.info(f"[SUCCESS] _crear_reaccion_emoji: created reaccion_id={reaccion_id} emoji={emoji} comentario={comentario_id} usuario={usuario_id}")
        except Exception as e:
            logger.error(f"[ERROR] _crear_reaccion_emoji fallo: {type(e).__name__}: {e!s}")
            try:
                db.rollback()
            except Exception:
                pass

    @staticmethod
    def _eliminar_reaccion_por_id(db: Session, reaccion_id: str) -> None:
        """Elimina una reacción por su ID."""
        query = text(
            """
            DELETE FROM "Reacciones"
            WHERE reaccion_id = :reaccion_id
            """
        )
        db.execute(query, {"reaccion_id": reaccion_id})
        db.commit()
        logger.debug(f"_eliminar_reaccion_por_id: deleted reaccion_id={reaccion_id}")

    @staticmethod
    def _obtener_estadisticas(db: Session, comentario_id: str) -> dict[str, Any]:
        """Obtiene estadísticas simples de reacciones para un comentario.

        Retorna un dict con conteo total y conteo por emoji para ayudar al frontend.
        """
        try:
            query_total = text(
                """
                SELECT COUNT(*) as total
                FROM "Reacciones"
                WHERE comentario_id = :comentario_id
                """
            )
            total_row = db.execute(query_total, {"comentario_id": comentario_id}).fetchone()
            total = int(total_row[0]) if total_row else 0

            query_by_emoji = text(
                """
                SELECT COALESCE(emoji, tipo) as emoji, COUNT(*) as cantidad
                FROM "Reacciones"
                WHERE comentario_id = :comentario_id
                GROUP BY COALESCE(emoji, tipo)
                ORDER BY COUNT(*) DESC
                """
            )
            rows = db.execute(query_by_emoji, {"comentario_id": comentario_id}).fetchall()
            por_emoji = [{"emoji": r.emoji, "cantidad": int(r.cantidad)} for r in rows]

            return {"total": total, "por_emoji": por_emoji}
        except Exception:
            logger.exception("_obtener_estadisticas fallo")
            return {"total": 0, "por_emoji": []}

    def eliminar_reaccion_por_id(db: Session, reaccion_id: str, usuario: Usuario) -> dict[str, Any]:
        """Public wrapper to delete a reaction by its id with ownership check and return canonical list."""
        try:
            # Verify reaction exists and belongs to user (or allow admins in future)
            query = text(
                """
                SELECT reaccion_id, comentario_id, usuario_id
                FROM "Reacciones"
                WHERE reaccion_id = :reaccion_id
                """
            )
            row = db.execute(query, {"reaccion_id": reaccion_id}).fetchone()
            if not row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reacción no encontrada")

            if str(row.usuario_id) != str(usuario.usuario_id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes eliminar esta reacción")

            # Delete the single reaction
            ReaccionService._eliminar_reaccion_por_id(db, reaccion_id)

            # Return canonical list for the comment to help frontend sync
            comentario_id = row.comentario_id
            try:
                reacciones_resp = ReaccionService.obtener_reacciones(db, comentario_id, usuario)
                reacciones_list = reacciones_resp.get("data") if isinstance(reacciones_resp, dict) else None
            except Exception:
                reacciones_list = None

            stats = ReaccionService._obtener_estadisticas(db, comentario_id)

            return {
                "success": True,
                "message": "Reacción eliminada",
                "data": {"estadisticas": stats},
                "reacciones": reacciones_list,
            }
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error eliminando reaccion por id: {e!s}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar reacción") from e


# Instancia global
reaccion_service = ReaccionService()
