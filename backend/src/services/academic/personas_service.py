"""Service para gestión de personas y perfiles de usuario.

Maneja la obtención de listas de personas en cursos,
perfiles de usuario con información completa, y actividad reciente.
"""

import logging
from typing import Any

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.models.users.usuario import Usuario


logger = logging.getLogger(__name__)


class PersonasService:
    """Servicio para gestión de personas y perfiles."""

    @staticmethod
    def obtener_personas_curso(
        db: Session,
        curso_id: str,
        rol_filtro: str | None = None,
        busqueda: str | None = None,
        usuario_actual: Usuario = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Obtiene las personas asociadas a un curso.

        Args:
            db: Sesión de base de datos
            curso_id: ID del curso
            rol_filtro: Filtro opcional por rol (docente, estudiante)
            busqueda: Búsqueda por nombre
            usuario_actual: Usuario que hace la solicitud
            skip: Offset para paginación
            limit: Límite de resultados

        Returns:
            Dict con personas y metadata
        """
        try:
            personas = []

            # Obtener docentes del curso
            if not rol_filtro or rol_filtro == "docente":
                docentes_query = text(
                    """
                    SELECT DISTINCT
                        u.usuario_id,
                        u.nombres,
                        u.apellidos,
                        u.correo_institucional,
                        u.perfil_url,
                        u.estado_cuenta,
                        u.ultimo_acceso,
                        'docente' as rol,
                        d.horario_atencion
                    FROM "Usuario" u
                    JOIN "Docente" d ON u.usuario_id = d.docente_id
                    JOIN "CursoDocente" cd ON d.docente_id = cd.docente_id
                    WHERE cd.curso_id = :curso_id
                        AND (:busqueda IS NULL OR
                             u.nombres ILIKE '%' || :busqueda || '%' OR
                             u.apellidos ILIKE '%' || :busqueda || '%')
                    ORDER BY u.nombres, u.apellidos
                    LIMIT :limit OFFSET :skip
                """
                )

                docentes = db.execute(
                    docentes_query,
                    {
                        "curso_id": curso_id,
                        "busqueda": busqueda,
                        "limit": limit,
                        "skip": skip,
                    },
                ).fetchall()

                personas.extend([dict(row._mapping) for row in docentes])

            # Obtener estudiantes del curso
            if not rol_filtro or rol_filtro == "estudiante":
                estudiantes_query = text(
                    """
                    SELECT DISTINCT
                        u.usuario_id,
                        u.nombres,
                        u.apellidos,
                        u.correo_institucional,
                        u.perfil_url,
                        u.estado_cuenta,
                        u.ultimo_acceso,
                        'estudiante' as rol,
                        g.nombre as grupo_nombre
                    FROM "Usuario" u
                    JOIN "Estudiante" e ON u.usuario_id = e.estudiante_id
                    JOIN "EstudianteGrupo" eg ON e.estudiante_id = eg.estudiante_id
                    JOIN "Grupo" g ON eg.grupo_id = g.grupo_id
                    JOIN "GrupoCurso" gc ON g.grupo_id = gc.grupo_id
                    WHERE gc.curso_id = :curso_id
                        AND (:busqueda IS NULL OR
                             u.nombres ILIKE '%' || :busqueda || '%' OR
                             u.apellidos ILIKE '%' || :busqueda || '%')
                    ORDER BY u.nombres, u.apellidos
                    LIMIT :limit OFFSET :skip
                """
                )

                estudiantes = db.execute(
                    estudiantes_query,
                    {
                        "curso_id": curso_id,
                        "busqueda": busqueda,
                        "limit": limit,
                        "skip": skip,
                    },
                ).fetchall()

                personas.extend([dict(row._mapping) for row in estudiantes])

            # Contar total
            count_query = text(
                """
                SELECT COUNT(DISTINCT u.usuario_id) as total
                FROM "Usuario" u
                WHERE u.usuario_id IN (
                    -- Docentes
                    SELECT d.docente_id
                    FROM "Docente" d
                    JOIN "CursoDocente" cd ON d.docente_id = cd.docente_id
                    WHERE cd.curso_id = :curso_id

                    UNION

                    -- Estudiantes
                    SELECT e.estudiante_id
                    FROM "Estudiante" e
                    JOIN "EstudianteGrupo" eg ON e.estudiante_id = eg.estudiante_id
                    JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
                    WHERE gc.curso_id = :curso_id
                )
                AND (:busqueda IS NULL OR
                     u.nombres ILIKE '%' || :busqueda || '%' OR
                     u.apellidos ILIKE '%' || :busqueda || '%')
            """
            )

            total = db.execute(
                count_query, {"curso_id": curso_id, "busqueda": busqueda}
            ).scalar()

            return {
                "success": True,
                "data": personas,
                "total": total or 0,
                "skip": skip,
                "limit": limit,
                "message": "Personas obtenidas exitosamente",
            }

        except Exception as e:
            logger.exception(f"Error obteniendo personas del curso: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error al obtener personas: {e!s}"
            ) from e

    @staticmethod
    def obtener_perfil_usuario(
        db: Session, usuario_id: str, usuario_actual: Usuario
    ) -> dict[str, Any]:
        """Obtiene el perfil completo de un usuario.

        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            usuario_actual: Usuario que hace la solicitud

        Returns:
            Dict con información completa del perfil
        """
        try:
            # Información básica del usuario
            usuario_query = text(
                """
                SELECT
                    u.usuario_id,
                    u.nombres,
                    u.apellidos,
                    u.correo_institucional,
                    u.rol,
                    u.perfil_url,
                    u.portada_url,
                    u.telefono,
                    u.descripcion,
                    u.estado_cuenta,
                    u.fecha_creacion,
                    u.ultimo_acceso
                FROM "Usuario" u
                WHERE u.usuario_id = :usuario_id
            """
            )

            usuario_result = db.execute(
                usuario_query, {"usuario_id": usuario_id}
            ).fetchone()

            if not usuario_result:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            perfil = dict(usuario_result._mapping)

            # Información específica según rol
            if perfil["rol"] == "docente":
                docente_query = text(
                    """
                    SELECT
                        d.horario_atencion,
                        d.especialidad,
                        COUNT(DISTINCT cd.curso_id) as total_cursos
                    FROM "Docente" d
                    LEFT JOIN "CursoDocente" cd ON d.docente_id = cd.docente_id
                    WHERE d.docente_id = :usuario_id
                    GROUP BY d.docente_id, d.horario_atencion, d.especialidad
                """
                )

                docente_info = db.execute(
                    docente_query, {"usuario_id": usuario_id}
                ).fetchone()

                if docente_info:
                    perfil["info_docente"] = dict(docente_info._mapping)

            elif perfil["rol"] == "estudiante":
                estudiante_query = text(
                    """
                    SELECT
                        e.fecha_ingreso,
                        e.codigo_estudiantil,
                        COUNT(DISTINCT gc.curso_id) as total_cursos
                    FROM "Estudiante" e
                    LEFT JOIN "EstudianteGrupo" eg ON e.estudiante_id = eg.estudiante_id
                    LEFT JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
                    WHERE e.estudiante_id = :usuario_id
                    GROUP BY e.estudiante_id, e.fecha_ingreso, e.codigo_estudiantil
                """
                )

                estudiante_info = db.execute(
                    estudiante_query, {"usuario_id": usuario_id}
                ).fetchone()

                if estudiante_info:
                    perfil["info_estudiante"] = dict(estudiante_info._mapping)

            elif perfil["rol"] == "coordinador":
                coordinador_query = text(
                    """
                    SELECT
                        c.horario_atencion,
                        COUNT(DISTINCT ic.institucion_id) as total_instituciones
                    FROM "Coordinador" c
                    LEFT JOIN "InstitucionCoordinador" ic ON c.coordinador_id = ic.coordinador_id
                    WHERE c.coordinador_id = :usuario_id
                    GROUP BY c.coordinador_id, c.horario_atencion
                """
                )

                coordinador_info = db.execute(
                    coordinador_query, {"usuario_id": usuario_id}
                ).fetchone()

                if coordinador_info:
                    perfil["info_coordinador"] = dict(coordinador_info._mapping)

            # Cursos activos
            cursos_query = text(
                """
                SELECT
                    c.curso_id,
                    c.nombre,
                    c.codigo_curso,
                    i.nombre as institucion_nombre
                FROM "Curso" c
                LEFT JOIN "Institucion" i ON c.institucion_id = i.institucion_id
                WHERE c.curso_id IN (
                    SELECT cd.curso_id FROM "CursoDocente" cd WHERE cd.docente_id = :usuario_id
                    UNION
                    SELECT gc.curso_id
                    FROM "EstudianteGrupo" eg
                    JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
                    WHERE eg.estudiante_id = :usuario_id
                )
                AND c.activo = true
                ORDER BY c.nombre
                LIMIT 10
            """
            )

            cursos = db.execute(cursos_query, {"usuario_id": usuario_id}).fetchall()

            perfil["cursos_activos"] = [dict(row._mapping) for row in cursos]

            # Actividad reciente (últimas tareas/entregas)
            actividad_query = text(
                """
                SELECT
                    'entrega' as tipo,
                    et.fecha_entrega as fecha,
                    t.titulo as descripcion,
                    c.nombre as curso_nombre
                FROM "EntregaTarea" et
                JOIN "Tarea" t ON et.tarea_id = t.tarea_id
                JOIN "Curso" c ON t.curso_id = c.curso_id
                WHERE et.estudiante_id = :usuario_id
                ORDER BY et.fecha_entrega DESC
                LIMIT 5
            """
            )

            actividad = db.execute(
                actividad_query, {"usuario_id": usuario_id}
            ).fetchall()

            perfil["actividad_reciente"] = [dict(row._mapping) for row in actividad]

            return {
                "success": True,
                "data": perfil,
                "message": "Perfil obtenido exitosamente",
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo perfil: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error al obtener perfil: {e!s}"
            ) from e


# Instancia global del servicio
personas_service = PersonasService()
