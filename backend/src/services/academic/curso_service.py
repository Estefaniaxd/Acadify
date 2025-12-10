"""Service para gestión de cursos.

Este servicio contiene toda la lógica de negocio relacionada con cursos.
Las rutas solo deben llamar a estos métodos, no hacer queries directas.
"""

import logging
from typing import Any

from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.models.users.usuario import Usuario


logger = logging.getLogger(__name__)

def _serialize_row(row_mapping: dict) -> dict:
    """Convierte UUIDs a strings para serialización JSON."""
    result = {}
    for key, value in row_mapping.items():
        result[key] = str(value) if isinstance(value, UUID) else value
    return result


class CursoService:
    """Servicio para gestión de cursos."""

    @staticmethod
    def obtener_cursos_usuario(
        db: Session, usuario: Usuario, limit: int = 100, offset: int = 0
    ) -> dict[str, Any]:
        """Obtiene los cursos de un usuario según su rol.

        Args:
            db: Sesión de base de datos
            usuario: Usuario actual
            limit: Límite de resultados (paginación)
            offset: Offset para paginación

        Returns:
            Dict con cursos y metadata
        """
        try:
            cursos = []
            source = ""

            # Determinar según rol
            if usuario.rol == "estudiante":
                cursos = CursoService._get_cursos_estudiante(db, usuario, limit, offset)
                source = "student_enrollments"
            elif usuario.rol == "docente":
                cursos = CursoService._get_cursos_docente(db, usuario, limit, offset)
                source = "teacher_assignments"
            elif usuario.rol == "coordinador":
                cursos = CursoService._get_cursos_coordinador(
                    db, usuario, limit, offset
                )
                source = "coordinator_institution"
            else:
                raise HTTPException(
                    status_code=403,
                    detail=f"Rol '{usuario.rol}' no tiene acceso a cursos",
                )

            return {
                "success": True,
                "message": "Cursos obtenidos exitosamente",
                "data": cursos,
                "total": len(cursos),
                "source": source,
                "user_role": usuario.rol,
                "empty_state": len(cursos) == 0,
                "empty_message": (
                    CursoService._get_empty_message(usuario.rol)
                    if len(cursos) == 0
                    else None
                ),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo cursos: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error interno al obtener cursos: {e!s}"
            ) from e

    @staticmethod
    def _get_cursos_estudiante(
        db: Session, usuario: Usuario, limit: int, offset: int
    ) -> list[dict]:
        """Obtiene cursos de un estudiante."""
        query = text(
            """
            SELECT
                c.curso_id,
                c.nombre,
                c.descripcion,
                c.codigo_acceso,
                c.estado,
                i.nombre as institucion_nombre,
                COALESCE(
                    json_agg(
                        jsonb_build_object(
                            'docente_id', d.docente_id,
                            'nombres', u_doc.nombres,
                            'apellidos', u_doc.apellidos
                        )
                    ) FILTER (WHERE d.docente_id IS NOT NULL),
                    '[]'
                ) as docentes
            FROM "Curso" c
            LEFT JOIN "Institucion" i ON c.institucion_id = i.institucion_id
            LEFT JOIN "CursoDocente" cd ON c.curso_id = cd.curso_id
            LEFT JOIN "Docente" d ON cd.docente_id = d.docente_id
            LEFT JOIN "Usuario" u_doc ON d.docente_id = u_doc.usuario_id
            WHERE c.curso_id IN (
                SELECT DISTINCT gc.curso_id
                FROM "EstudianteGrupo" eg
                JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
                WHERE eg.estudiante_id = :usuario_id
            )
            GROUP BY c.curso_id, c.nombre, c.descripcion, c.codigo_acceso, c.estado, i.nombre
            ORDER BY c.nombre
            LIMIT :limit OFFSET :offset
        """
        )

        result = db.execute(
            query, {"usuario_id": usuario.usuario_id, "limit": limit, "offset": offset}
        ).fetchall()

        return [_serialize_row(dict(row._mapping)) for row in result]

    @staticmethod
    def _get_cursos_docente(
        db: Session, usuario: Usuario, limit: int, offset: int
    ) -> list[dict]:
        """Obtiene cursos de un docente."""
        query = text(
            """
            SELECT DISTINCT
                c.curso_id,
                c.nombre,
                c.descripcion,
                c.codigo_acceso,
                c.estado,
                i.nombre as institucion_nombre,
                COUNT(DISTINCT eg.estudiante_id) as total_estudiantes
            FROM "Curso" c
            LEFT JOIN "Institucion" i ON c.institucion_id = i.institucion_id
            LEFT JOIN "CursoDocente" cd ON c.curso_id = cd.curso_id
            LEFT JOIN "GrupoCurso" gc ON c.curso_id = gc.curso_id
            LEFT JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id
            -- Considerar asignaciones tanto a nivel de curso (CursoDocente)
            -- como a nivel de grupo (GrupoCurso). Algunos procesos crean solo
            -- entradas en GrupoCurso, por eso incluimos ambas fuentes.
            WHERE (cd.docente_id = :usuario_id OR gc.docente_id = :usuario_id)
            GROUP BY c.curso_id, c.nombre, c.descripcion, c.codigo_acceso, c.estado, i.nombre
            ORDER BY c.nombre
            LIMIT :limit OFFSET :offset
        """
        )

        result = db.execute(
            query, {"usuario_id": usuario.usuario_id, "limit": limit, "offset": offset}
        ).fetchall()

        return [_serialize_row(dict(row._mapping)) for row in result]

    @staticmethod
    def _get_cursos_coordinador(
        db: Session, usuario: Usuario, limit: int, offset: int
    ) -> list[dict]:
        """Obtiene cursos de un coordinador (todos de su institución)."""
        query = text(
            """
            SELECT DISTINCT
                c.curso_id,
                c.nombre,
                c.descripcion,
                c.codigo_acceso,
                c.estado,
                i.nombre as institucion_nombre,
                COUNT(DISTINCT eg.estudiante_id) as total_estudiantes,
                COUNT(DISTINCT cd.docente_id) as total_docentes
            FROM "Curso" c
            LEFT JOIN "Institucion" i ON c.institucion_id = i.institucion_id
            LEFT JOIN "GrupoCurso" gc ON c.curso_id = gc.curso_id
            LEFT JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id
            LEFT JOIN "CursoDocente" cd ON c.curso_id = cd.curso_id
            WHERE c.institucion_id IN (
                SELECT ic.institucion_id
                FROM "InstitucionCoordinador" ic
                WHERE ic.coordinador_id = :usuario_id
            )
            GROUP BY c.curso_id, c.nombre, c.descripcion, c.codigo_acceso, c.estado, i.nombre
            ORDER BY c.nombre
            LIMIT :limit OFFSET :offset
        """
        )

        result = db.execute(
            query, {"usuario_id": usuario.usuario_id, "limit": limit, "offset": offset}
        ).fetchall()

        return [_serialize_row(dict(row._mapping)) for row in result]

    @staticmethod
    def _get_empty_message(rol: str) -> str:
        """Retorna mensaje apropiado cuando no hay cursos."""
        messages = {
            "estudiante": "No estás inscrito en ningún curso. Usa un código de acceso para inscribirte.",
            "docente": "No tienes cursos asignados. Contacta al coordinador de tu institución.",
            "coordinador": "No hay cursos registrados en tu institución. Crea un nuevo curso.",
        }
        return messages.get(rol, "No hay cursos disponibles")

    @staticmethod
    def obtener_cursos_disponibles(
        db: Session,
        usuario: Usuario,
        institucion_id: str | None = None,
        area: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Obtiene cursos disponibles para inscripción.

        Args:
            db: Sesión de base de datos
            usuario: Usuario actual
            institucion_id: Filtro opcional por institución
            area: Filtro opcional por área
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Dict con cursos disponibles
        """
        try:
            query = text(
                """
                SELECT DISTINCT
                    c.curso_id,
                    c.nombre,
                    c.descripcion,
                    c.codigo_acceso,
                    c.estado,
                    i.nombre as institucion_nombre,
                    p.nombre as programa_nombre,
                    COUNT(DISTINCT eg.estudiante_id) as total_estudiantes
                FROM "Curso" c
                LEFT JOIN "Institucion" i ON c.institucion_id = i.institucion_id
                LEFT JOIN "Programa" p ON c.programa_id = p.programa_id
                LEFT JOIN "GrupoCurso" gc ON c.curso_id = gc.curso_id
                LEFT JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id
                WHERE c.estado IN ('inscripciones_abiertas', 'en_curso', 'programado')
                    AND (:institucion_id IS NULL OR c.institucion_id = :institucion_id)
                    AND (:area IS NULL OR p.nombre ILIKE '%' || :area || '%')
                    AND NOT EXISTS (
                        SELECT 1 FROM "EstudianteGrupo" eg2
                        JOIN "GrupoCurso" gc2 ON eg2.grupo_id = gc2.grupo_id
                        WHERE gc2.curso_id = c.curso_id
                        AND eg2.estudiante_id = :usuario_id
                    )
                GROUP BY c.curso_id, c.nombre, c.descripcion, c.codigo_acceso, c.estado, i.nombre, p.nombre
                ORDER BY c.nombre
                LIMIT :limit OFFSET :offset
            """
            )

            result = db.execute(
                query,
                {
                    "usuario_id": usuario.usuario_id,
                    "institucion_id": institucion_id,
                    "area": area,
                    "limit": limit,
                    "offset": offset,
                },
            ).fetchall()

            cursos = [dict(row._mapping) for row in result]

            return {
                "success": True,
                "data": cursos,
                "total": len(cursos),
                "message": "Cursos disponibles obtenidos exitosamente",
            }

        except Exception as e:
            logger.exception(f"Error obteniendo cursos disponibles: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error al obtener cursos disponibles: {e!s}"
            ) from e

    @staticmethod
    def obtener_detalle_curso(
        db: Session, curso_id: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Obtiene el detalle completo de un curso.

        Args:
            db: Sesión de base de datos
            curso_id: ID del curso
            usuario: Usuario actual

        Returns:
            Dict con información completa del curso
        """
        # Verificar que el usuario tenga acceso al curso
        if not CursoService._usuario_tiene_acceso(db, curso_id, usuario):
            raise HTTPException(status_code=403, detail="No tienes acceso a este curso")

        # Obtener información del curso
        query = text(
            """
            SELECT
                c.curso_id,
                c.nombre,
                c.descripcion,
                c.codigo_acceso,
                c.estado,
                c.fecha_creacion,
                i.nombre as institucion_nombre,
                i.institucion_id,
                p.nombre as programa_nombre,
                p.programa_id
            FROM "Curso" c
            LEFT JOIN "Institucion" i ON c.institucion_id = i.institucion_id
            LEFT JOIN "Programa" p ON c.programa_id = p.programa_id
            WHERE c.curso_id = :curso_id
        """
        )

        result = db.execute(query, {"curso_id": curso_id}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        curso_data = _serialize_row(dict(result._mapping))

        # Obtener profesores del curso
        profesores_query = text(
            """
            SELECT DISTINCT
                u.usuario_id as id,
                u.nombres,
                u.apellidos,
                u.correo_institucional as correo
            FROM "Usuario" u
            JOIN "Docente" d ON u.usuario_id = d.docente_id
            JOIN "GrupoCurso" gc ON d.docente_id = gc.docente_id
            WHERE gc.curso_id = :curso_id
            ORDER BY u.nombres, u.apellidos
        """
        )

        profesores_result = db.execute(profesores_query, {"curso_id": curso_id}).fetchall()
        profesores = []

        for prof_row in profesores_result:
            prof_data = dict(prof_row._mapping)
            profesores.append({
                "id": str(prof_data["id"]),
                "nombres": prof_data["nombres"],
                "apellidos": prof_data["apellidos"],
                "nombre_completo": f"{prof_data['nombres']} {prof_data['apellidos']}",
                "correo": prof_data["correo"],
                "fecha_asignacion": None,
                "rol": "docente"
            })

        # Obtener estudiantes del curso (conteo)
        estudiantes_query = text(
            """
            SELECT COUNT(DISTINCT eg.estudiante_id) as total_estudiantes
            FROM "EstudianteGrupo" eg
            JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
            WHERE gc.curso_id = :curso_id
        """
        )

        estudiantes_result = db.execute(estudiantes_query, {"curso_id": curso_id}).fetchone()
        total_estudiantes = estudiantes_result._mapping["total_estudiantes"] if estudiantes_result else 0

        # Construir respuesta completa
        response = {
            "success": True,
            "message": "Curso obtenido exitosamente",
            "data": {
                **curso_data,
                "personas": {
                    "profesores": profesores,
                    "estudiantes": [],  # Lista vacía por ahora, se puede poblar si es necesario
                    "total_profesores": len(profesores),
                    "total_estudiantes": total_estudiantes
                }
            }
        }

        return response

    @staticmethod
    def _usuario_tiene_acceso(db: Session, curso_id: str, usuario: Usuario) -> bool:
        """Verifica si un usuario tiene acceso a un curso."""
        if usuario.rol == "estudiante":
            query = text(
                """
                SELECT EXISTS(
                    SELECT 1 FROM "EstudianteGrupo" ge
                    JOIN "GrupoCurso" gc ON ge.grupo_id = gc.grupo_id
                    WHERE gc.curso_id = :curso_id
                    AND ge.estudiante_id = :usuario_id
                )
            """
            )
        elif usuario.rol == "docente":
            query = text(
                """
                SELECT EXISTS(
                    SELECT 1 FROM "GrupoCurso" gc
                    WHERE gc.curso_id = :curso_id
                    AND gc.docente_id = :usuario_id
                )
            """
            )
        elif usuario.rol == "coordinador":
            query = text(
                """
                SELECT EXISTS(
                    SELECT 1 FROM "Curso" c
                    JOIN "InstitucionCoordinador" ic
                        ON c.institucion_id = ic.institucion_id
                    WHERE c.curso_id = :curso_id
                    AND ic.coordinador_id = :usuario_id
                )
            """
            )
        else:
            return False

        result = db.execute(
            query, {"curso_id": curso_id, "usuario_id": usuario.usuario_id}
        ).scalar()

        return bool(result)

    @staticmethod
    def validar_acceso_curso(db: Session, curso_id: str, usuario: Usuario) -> bool:
        """Método público para validar acceso a un curso.

        Args:
            db: Sesión de base de datos
            curso_id: ID del curso
            usuario: Usuario a validar

        Returns:
            True si tiene acceso, False otherwise
        """
        return CursoService._usuario_tiene_acceso(db, curso_id, usuario)


# Instancia global del servicio
curso_service = CursoService()
