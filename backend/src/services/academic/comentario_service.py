"""Service para gestión de comentarios en cursos.

Aplica principios SOLID:
- Single Responsibility: Solo gestiona comentarios
- Open/Closed: Extensible sin modificar código existente
- Liskov Substitution: Interfaces consistentes
- Interface Segregation: Métodos específicos y cohesivos
- Dependency Inversion: Depende de abstracciones (Session, models)

Clean Code:
- Nombres descriptivos
- Funciones pequeñas (< 50 líneas)
- Un solo nivel de abstracción por función
- Manejo de errores explícito
"""

from datetime import UTC, datetime
import logging
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.models.communication.comentario import Comentario, TipoComentario
from src.models.users.usuario import Usuario


logger = logging.getLogger(__name__)


class ComentarioService:
    """Service para gestión de comentarios.

    Responsabilidades:
    - CRUD de comentarios
    - Validación de permisos
    - Gestión de respuestas
    - Paginación de resultados
    """

    # Constantes (Clean Code: Magic numbers -> Named constants)
    MAX_COMENTARIO_LENGTH = 5000
    MAX_RESPUESTAS_PER_PAGE = 50
    DEFAULT_PAGE_SIZE = 20

    @staticmethod
    def crear_comentario(
        db: Session,
        curso_id: str,
        contenido: str,
        usuario: Usuario,
        tipo: TipoComentario = TipoComentario.comentario,
        comentario_padre_id: str | None = None,
    ) -> dict[str, Any]:
        """Crea un nuevo comentario en un curso.

        Args:
            db: Sesión de base de datos
            curso_id: ID del curso
            contenido: Contenido del comentario
            usuario: Usuario que crea el comentario
            tipo: Tipo de comentario (comentario, pregunta, anuncio, respuesta)
            comentario_padre_id: ID del comentario padre si es respuesta

        Returns:
            Dict con el comentario creado

        Raises:
            HTTPException: Si hay errores de validación o permisos
        """
        try:
            # Validación de entrada (Clean Code: Fail fast)
            ComentarioService._validar_contenido(contenido)
            ComentarioService._validar_acceso_curso(db, curso_id, usuario)

            # Si es respuesta, validar comentario padre
            if comentario_padre_id:
                ComentarioService._validar_comentario_padre(
                    db, comentario_padre_id, curso_id
                )

            # Crear comentario (Single Responsibility)
            comentario = Comentario(
                contenido=contenido,
                autor_id=usuario.usuario_id,
                tipo=tipo,
                curso_id=UUID(curso_id),
                comentario_padre_id=(
                    UUID(comentario_padre_id) if comentario_padre_id else None
                ),
                fecha_creacion=datetime.now(UTC),
            )

            db.add(comentario)
            db.commit()
            db.refresh(comentario)

            logger.info(
                f"Comentario creado: {comentario.comentario_id} por usuario {usuario.usuario_id}"
            )

            return {
                "success": True,
                "message": "Comentario creado exitosamente",
                "data": ComentarioService._comentario_to_dict(db, comentario),
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error creando comentario: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear comentario: {e!s}",
            ) from e

    @staticmethod
    def obtener_comentarios_curso(
        db: Session,
        curso_id: str,
        usuario: Usuario,
        limit: int = DEFAULT_PAGE_SIZE,
        offset: int = 0,
        tipo: TipoComentario | None = None,
    ) -> dict[str, Any]:
        """Obtiene comentarios de un curso con paginación.

        Args:
            db: Sesión de base de datos
            curso_id: ID del curso
            usuario: Usuario que consulta
            limit: Límite de resultados
            offset: Offset para paginación
            tipo: Filtro opcional por tipo de comentario

        Returns:
            Dict con comentarios y metadata de paginación
        """
        try:
            # Validar acceso
            ComentarioService._validar_acceso_curso(db, curso_id, usuario)

            # Query optimizada con JOINs (Clean Code: Avoid N+1)
            query = text(
                """
                SELECT
                    c.comentario_id,
                    c.contenido,
                    c.tipo,
                    c.fecha_creacion,
                    c.fecha_actualizacion,
                    c.comentario_padre_id,
                    u.usuario_id as autor_id,
                    u.nombres || ' ' || u.apellidos as autor_nombre,
                    u.perfil_url as autor_avatar,
                    COUNT(DISTINCT r.comentario_id) as total_respuestas,
                    COUNT(DISTINCT reac.reaccion_id) as total_reacciones
                FROM "Comentario" c
                JOIN "Usuario" u ON c.autor_id = u.usuario_id
                LEFT JOIN "Comentario" r ON r.comentario_padre_id = c.comentario_id
                LEFT JOIN "Reacciones" reac ON reac.comentario_id = c.comentario_id
                WHERE c.curso_id = :curso_id
                    AND c.comentario_padre_id IS NULL
                    AND (:tipo IS NULL OR c.tipo = :tipo)
                GROUP BY c.comentario_id, u.usuario_id
                ORDER BY c.fecha_creacion DESC
                LIMIT :limit OFFSET :offset
            """
            )

            result = db.execute(
                query,
                {
                    "curso_id": curso_id,
                    "tipo": tipo.value if tipo else None,
                    "limit": limit,
                    "offset": offset,
                },
            ).fetchall()

            # Contar total (para paginación)
            count_query = text(
                """
                SELECT COUNT(*)
                FROM "Comentario"
                WHERE curso_id = :curso_id
                    AND comentario_padre_id IS NULL
                    AND (:tipo IS NULL OR tipo = :tipo)
            """
            )

            total = db.execute(
                count_query,
                {"curso_id": curso_id, "tipo": tipo.value if tipo else None},
            ).scalar()

            comentarios = [dict(row._mapping) for row in result]

            return {
                "success": True,
                "data": comentarios,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo comentarios: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener comentarios: {e!s}",
            ) from e

    @staticmethod
    def actualizar_comentario(
        db: Session, comentario_id: str, nuevo_contenido: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Actualiza el contenido de un comentario.

        Args:
            db: Sesión de base de datos
            comentario_id: ID del comentario
            nuevo_contenido: Nuevo contenido
            usuario: Usuario que actualiza

        Returns:
            Dict con el comentario actualizado
        """
        try:
            # Validaciones
            ComentarioService._validar_contenido(nuevo_contenido)
            comentario = ComentarioService._obtener_comentario(db, comentario_id)
            ComentarioService._validar_permisos_edicion(comentario, usuario)

            # Actualizar
            comentario.contenido = nuevo_contenido
            comentario.fecha_actualizacion = datetime.now(UTC)

            db.commit()
            db.refresh(comentario)

            logger.info(f"Comentario actualizado: {comentario_id}")

            return {
                "success": True,
                "message": "Comentario actualizado exitosamente",
                "data": ComentarioService._comentario_to_dict(db, comentario),
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error actualizando comentario: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar comentario: {e!s}",
            ) from e

    @staticmethod
    def eliminar_comentario(
        db: Session, comentario_id: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Elimina un comentario (soft delete).

        Args:
            db: Sesión de base de datos
            comentario_id: ID del comentario
            usuario: Usuario que elimina

        Returns:
            Dict con confirmación
        """
        try:
            comentario = ComentarioService._obtener_comentario(db, comentario_id)
            ComentarioService._validar_permisos_edicion(comentario, usuario)

            # Soft delete: marcar como eliminado en lugar de borrar
            comentario.contenido = "[Comentario eliminado]"
            comentario.fecha_actualizacion = datetime.now(UTC)

            db.commit()

            logger.info(f"Comentario eliminado: {comentario_id}")

            return {"success": True, "message": "Comentario eliminado exitosamente"}

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error eliminando comentario: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar comentario: {e!s}",
            ) from e

    @staticmethod
    def obtener_respuestas(
        db: Session,
        comentario_id: str,
        usuario: Usuario,
        limit: int = MAX_RESPUESTAS_PER_PAGE,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Obtiene respuestas de un comentario.

        Args:
            db: Sesión de base de datos
            comentario_id: ID del comentario padre
            usuario: Usuario que consulta
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Dict con respuestas y paginación
        """
        try:
            # Validar que el comentario existe
            comentario_padre = ComentarioService._obtener_comentario(db, comentario_id)
            ComentarioService._validar_acceso_curso(
                db, str(comentario_padre.curso_id), usuario
            )

            # Obtener respuestas
            query = text(
                """
                SELECT
                    c.comentario_id,
                    c.contenido,
                    c.fecha_creacion,
                    c.fecha_actualizacion,
                    u.usuario_id as autor_id,
                    u.nombres || ' ' || u.apellidos as autor_nombre,
                    u.perfil_url as autor_avatar,
                    COUNT(DISTINCT reac.reaccion_id) as total_reacciones
                FROM "Comentario" c
                JOIN "Usuario" u ON c.autor_id = u.usuario_id
                LEFT JOIN "Reacciones" reac ON reac.comentario_id = c.comentario_id
                WHERE c.comentario_padre_id = :comentario_padre_id
                GROUP BY c.comentario_id, u.usuario_id
                ORDER BY c.fecha_creacion ASC
                LIMIT :limit OFFSET :offset
            """
            )

            result = db.execute(
                query,
                {
                    "comentario_padre_id": comentario_id,
                    "limit": limit,
                    "offset": offset,
                },
            ).fetchall()

            # Contar total
            count_query = text(
                """
                SELECT COUNT(*)
                FROM "Comentario"
                WHERE comentario_padre_id = :comentario_padre_id
            """
            )

            total = db.execute(
                count_query, {"comentario_padre_id": comentario_id}
            ).scalar()

            respuestas = [dict(row._mapping) for row in result]

            return {
                "success": True,
                "data": respuestas,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo respuestas: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener respuestas: {e!s}",
            ) from e

    # ========== MÉTODOS PRIVADOS (Helper functions) ==========

    @staticmethod
    def _validar_contenido(contenido: str) -> None:
        """Valida el contenido del comentario."""
        if not contenido or not contenido.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El contenido del comentario no puede estar vacío",
            )

        if len(contenido) > ComentarioService.MAX_COMENTARIO_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El comentario no puede exceder {ComentarioService.MAX_COMENTARIO_LENGTH} caracteres",
            )

    @staticmethod
    def _validar_acceso_curso(db: Session, curso_id: str, usuario: Usuario) -> None:
        """Valida que el usuario tenga acceso al curso."""
        # Reutilizar lógica de curso_service
        from src.services.academic.curso_service import CursoService

        if not CursoService._usuario_tiene_acceso(db, curso_id, usuario):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este curso",
            )

    @staticmethod
    def _validar_comentario_padre(
        db: Session, comentario_padre_id: str, curso_id: str
    ) -> None:
        """Valida que el comentario padre existe y pertenece al curso."""
        query = text(
            """
            SELECT comentario_id
            FROM "Comentario"
            WHERE comentario_id = :comentario_id
                AND curso_id = :curso_id
        """
        )

        result = db.execute(
            query, {"comentario_id": comentario_padre_id, "curso_id": curso_id}
        ).fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comentario padre no encontrado",
            )

    @staticmethod
    def _obtener_comentario(db: Session, comentario_id: str) -> Comentario:
        """Obtiene un comentario por ID."""
        comentario = (
            db.query(Comentario)
            .filter(Comentario.comentario_id == UUID(comentario_id))
            .first()
        )

        if not comentario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado"
            )

        return comentario

    @staticmethod
    def _validar_permisos_edicion(comentario: Comentario, usuario: Usuario) -> None:
        """Valida que el usuario puede editar/eliminar el comentario."""
        es_autor = str(comentario.autor_id) == str(usuario.usuario_id)
        es_coordinador = usuario.rol == "coordinador"
        es_docente = usuario.rol == "docente"

        if not (es_autor or es_coordinador or es_docente):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para modificar este comentario",
            )

    @staticmethod
    def _comentario_to_dict(db: Session, comentario: Comentario) -> dict[str, Any]:
        """Convierte un comentario a diccionario."""
        return {
            "comentario_id": str(comentario.comentario_id),
            "contenido": comentario.contenido,
            "tipo": comentario.tipo.value if comentario.tipo else "general",
            "fecha_creacion": (
                comentario.fecha_creacion.isoformat()
                if comentario.fecha_creacion
                else None
            ),
            "fecha_actualizacion": (
                comentario.fecha_actualizacion.isoformat()
                if comentario.fecha_actualizacion
                else None
            ),
            "autor_id": str(comentario.autor_id),
            "curso_id": str(comentario.curso_id),
            "comentario_padre_id": (
                str(comentario.comentario_padre_id)
                if comentario.comentario_padre_id
                else None
            ),
        }


# Instancia global del servicio
comentario_service = ComentarioService()
