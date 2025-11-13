"""Service para gestión de instituciones.

Este servicio maneja toda la lógica de negocio relacionada con instituciones,
incluyendo registro, vinculación de usuarios, y gestión de coordinadores.
"""

import logging
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.crud.academic.crud_institucion import institucion_crud
from src.models.academic.institucion import Institucion
from src.models.users.usuario import Usuario
from src.schemas.academic.institucion import InstitucionCreate, InstitucionUpdate
from src.schemas.academic.institucion_onboarding import (
    InstitucionBrandingUpdate,
    InstitucionOnboardingComplete,
    InstitucionOnboardingStatus,
)


logger = logging.getLogger(__name__)


class InstitucionService:
    """Servicio para gestión de instituciones."""

    @staticmethod
    def crear_institucion(
        db: Session, institucion_data: InstitucionCreate, coordinador: Usuario
    ) -> dict[str, Any]:
        """Crea una nueva institución y vincula al coordinador.

        Args:
            db: Sesión de base de datos
            institucion_data: Datos de la institución
            coordinador: Usuario coordinador que crea la institución

        Returns:
            Dict con la institución creada
        """
        try:
            # Validar que el usuario sea coordinador
            if coordinador.rol != "coordinador":
                raise HTTPException(
                    status_code=403,
                    detail="Solo coordinadores pueden crear instituciones",
                )

            # Extraer dominio del correo institucional si no está presente
            if (
                not institucion_data.dominio_principal
                and institucion_data.correo_institucional
            ):
                dominio = institucion_data.correo_institucional.split("@")[1]
                institucion_data.dominio_principal = dominio

            # Verificar que el dominio no exista
            if institucion_data.dominio_principal:
                dominio_existente = (
                    db.query(Institucion)
                    .filter(
                        Institucion.dominio_principal
                        == institucion_data.dominio_principal
                    )
                    .first()
                )

                if dominio_existente:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ya existe una institución con el dominio '{institucion_data.dominio_principal}'",
                    )

            # Crear la institución
            institucion = institucion_crud.create(db, obj_in=institucion_data)

            # Vincular al coordinador con la institución
            query = text(
                """
                INSERT INTO "InstitucionCoordinador"
                (institucion_id, coordinador_id, fecha_asignacion)
                VALUES (:institucion_id, :coordinador_id, NOW())
                ON CONFLICT (institucion_id, coordinador_id) DO NOTHING
            """
            )

            db.execute(
                query,
                {
                    "institucion_id": institucion.institucion_id,
                    "coordinador_id": coordinador.usuario_id,
                },
            )
            db.commit()

            logger.info(
                f"Institución '{institucion.nombre}' creada por coordinador {coordinador.usuario_id}"
            )

            return {
                "success": True,
                "message": "Institución creada exitosamente",
                "data": {
                    "institucion_id": institucion.institucion_id,
                    "nombre": institucion.nombre,
                    "dominio_principal": institucion.dominio_principal,
                    "coordinador_vinculado": True,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error creando institución: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error al crear institución: {e!s}"
            ) from e

    @staticmethod
    def obtener_instituciones_coordinador(
        db: Session, coordinador: Usuario, incluir_estadisticas: bool = False
    ) -> dict[str, Any]:
        """Obtiene las instituciones de un coordinador.

        Args:
            db: Sesión de base de datos
            coordinador: Usuario coordinador
            incluir_estadisticas: Si debe incluir estadísticas

        Returns:
            Dict con las instituciones
        """
        try:
            if coordinador.rol != "coordinador":
                raise HTTPException(
                    status_code=403,
                    detail="Solo coordinadores pueden acceder a esta información",
                )

            query = text(
                """
                SELECT
                    i.institucion_id,
                    i.nombre,
                    i.tipo,
                    i.direccion,
                    i.telefono,
                    i.correo_institucional,
                    i.dominio_principal,
                    i.estado,
                    ic.fecha_asignacion,
                    CASE WHEN :incluir_stats THEN
                        (SELECT COUNT(*) FROM "Curso" c WHERE c.institucion_id = i.institucion_id)
                    ELSE NULL END as total_cursos,
                    CASE WHEN :incluir_stats THEN
                        (SELECT COUNT(DISTINCT cd.docente_id)
                         FROM "Curso" c
                         JOIN "CursoDocente" cd ON c.curso_id = cd.curso_id
                         WHERE c.institucion_id = i.institucion_id)
                    ELSE NULL END as total_docentes,
                    CASE WHEN :incluir_stats THEN
                        (SELECT COUNT(DISTINCT eg.estudiante_id)
                         FROM "Curso" c
                         JOIN "GrupoCurso" gc ON c.curso_id = gc.curso_id
                         JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id
                         WHERE c.institucion_id = i.institucion_id)
                    ELSE NULL END as total_estudiantes
                FROM "Institucion" i
                JOIN "InstitucionCoordinador" ic
                    ON i.institucion_id = ic.institucion_id
                WHERE ic.coordinador_id = :coordinador_id
                ORDER BY i.nombre
            """
            )

            result = db.execute(
                query,
                {
                    "coordinador_id": coordinador.usuario_id,
                    "incluir_stats": incluir_estadisticas,
                },
            ).fetchall()

            instituciones = [dict(row._mapping) for row in result]

            return {
                "success": True,
                "data": instituciones,
                "total": len(instituciones),
                "message": "Instituciones obtenidas exitosamente",
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo instituciones: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error al obtener instituciones: {e!s}"
            ) from e

    @staticmethod
    def buscar_por_dominio(db: Session, dominio: str) -> Institucion | None:
        """Busca una institución por su dominio de email.

        Args:
            db: Sesión de base de datos
            dominio: Dominio a buscar (ej: "example.edu")

        Returns:
            Institución encontrada o None
        """
        try:
            return (
                db.query(Institucion)
                .filter(
                    Institucion.dominio_principal == dominio,
                    Institucion.estado == "activa",
                )
                .first()
            )
        except Exception as e:
            logger.exception(f"Error buscando institución por dominio: {e!s}")
            return None

    @staticmethod
    def vincular_usuario_institucion(
        db: Session, institucion_id: UUID, usuario_id: UUID, rol: str
    ) -> dict[str, Any]:
        """Vincula un usuario a una institución según su rol.

        Args:
            db: Sesión de base de datos
            institucion_id: ID de la institución
            usuario_id: ID del usuario
            rol: Rol del usuario (coordinador, docente, estudiante)

        Returns:
            Dict con resultado de la vinculación
        """
        try:
            # Verificar que la institución exista
            institucion = (
                db.query(Institucion)
                .filter(Institucion.institucion_id == institucion_id)
                .first()
            )

            if not institucion:
                raise HTTPException(status_code=404, detail="Institución no encontrada")

            # Vincular según el rol
            if rol == "coordinador":
                query = text(
                    """
                    INSERT INTO "InstitucionCoordinador"
                    (institucion_id, coordinador_id, fecha_asignacion)
                    VALUES (:institucion_id, :usuario_id, NOW())
                    ON CONFLICT (institucion_id, coordinador_id) DO NOTHING
                """
                )
            elif rol == "docente":
                # Los docentes se vinculan a través de cursos, no directamente
                logger.warning(
                    f"Intento de vincular docente {usuario_id} directamente a institución. "
                    "Los docentes se vinculan a través de CursoDocente"
                )
                return {
                    "success": False,
                    "message": "Los docentes se vinculan a través de cursos, no directamente a instituciones",
                }
            elif rol == "estudiante":
                # Los estudiantes se vinculan a través de grupos/cursos
                logger.warning(
                    f"Intento de vincular estudiante {usuario_id} directamente a institución. "
                    "Los estudiantes se vinculan a través de EstudianteGrupo"
                )
                return {
                    "success": False,
                    "message": "Los estudiantes se vinculan a través de grupos y cursos",
                }
            else:
                raise HTTPException(
                    status_code=400, detail=f"Rol '{rol}' no válido para vinculación"
                )

            db.execute(
                query, {"institucion_id": institucion_id, "usuario_id": usuario_id}
            )
            db.commit()

            logger.info(
                f"Usuario {usuario_id} ({rol}) vinculado a institución {institucion_id}"
            )

            return {
                "success": True,
                "message": f"{rol.capitalize()} vinculado exitosamente a la institución",
                "data": {
                    "institucion_id": institucion_id,
                    "usuario_id": usuario_id,
                    "rol": rol,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error vinculando usuario a institución: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error al vincular usuario: {e!s}"
            ) from e

    @staticmethod
    def actualizar_institucion(
        db: Session,
        institucion_id: UUID,
        institucion_data: InstitucionUpdate,
        coordinador: Usuario,
    ) -> dict[str, Any]:
        """Actualiza una institución.

        Args:
            db: Sesión de base de datos
            institucion_id: ID de la institución
            institucion_data: Datos a actualizar
            coordinador: Usuario coordinador

        Returns:
            Dict con la institución actualizada
        """
        try:
            # Verificar que sea coordinador
            if coordinador.rol != "coordinador":
                raise HTTPException(
                    status_code=403,
                    detail="Solo coordinadores pueden actualizar instituciones",
                )

            # Verificar que tenga acceso a la institución
            query = text(
                """
                SELECT EXISTS(
                    SELECT 1 FROM "InstitucionCoordinador"
                    WHERE institucion_id = :institucion_id
                    AND coordinador_id = :coordinador_id
                )
            """
            )

            tiene_acceso = db.execute(
                query,
                {
                    "institucion_id": institucion_id,
                    "coordinador_id": coordinador.usuario_id,
                },
            ).scalar()

            if not tiene_acceso:
                raise HTTPException(
                    status_code=403, detail="No tienes acceso a esta institución"
                )

            # Obtener institución
            institucion = (
                db.query(Institucion)
                .filter(Institucion.institucion_id == institucion_id)
                .first()
            )

            if not institucion:
                raise HTTPException(status_code=404, detail="Institución no encontrada")

            # Actualizar
            institucion_actualizada = institucion_crud.update(
                db, db_obj=institucion, obj_in=institucion_data
            )

            logger.info(
                f"Institución {institucion_id} actualizada por coordinador {coordinador.usuario_id}"
            )

            return {
                "success": True,
                "message": "Institución actualizada exitosamente",
                "data": {
                    "institucion_id": institucion_actualizada.institucion_id,
                    "nombre": institucion_actualizada.nombre,
                    "dominio_principal": institucion_actualizada.dominio_principal,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error actualizando institución: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error al actualizar institución: {e!s}"
            ) from e

    @staticmethod
    def obtener_estadisticas_institucion(
        db: Session, institucion_id: UUID, coordinador: Usuario
    ) -> dict[str, Any]:
        """Obtiene estadísticas detalladas de una institución.

        Args:
            db: Sesión de base de datos
            institucion_id: ID de la institución
            coordinador: Usuario coordinador

        Returns:
            Dict con estadísticas
        """
        try:
            # Verificar acceso
            if coordinador.rol != "coordinador":
                raise HTTPException(
                    status_code=403, detail="Solo coordinadores pueden ver estadísticas"
                )

            query = text(
                """
                SELECT EXISTS(
                    SELECT 1 FROM "InstitucionCoordinador"
                    WHERE institucion_id = :institucion_id
                    AND coordinador_id = :coordinador_id
                )
            """
            )

            tiene_acceso = db.execute(
                query,
                {
                    "institucion_id": institucion_id,
                    "coordinador_id": coordinador.usuario_id,
                },
            ).scalar()

            if not tiene_acceso:
                raise HTTPException(
                    status_code=403, detail="No tienes acceso a esta institución"
                )

            # Obtener estadísticas
            stats_query = text(
                """
                SELECT
                    i.institucion_id,
                    i.nombre,
                    (SELECT COUNT(*) FROM "Curso" c
                     WHERE c.institucion_id = i.institucion_id) as total_cursos,
                    (SELECT COUNT(*) FROM "Curso" c
                     WHERE c.institucion_id = i.institucion_id
                     AND c.estado IN ('inscripciones_abiertas', 'en_curso', 'programado', 'proximo')) as cursos_activos,
                    (SELECT COUNT(DISTINCT cd.docente_id)
                     FROM "Curso" c
                     JOIN "CursoDocente" cd ON c.curso_id = cd.curso_id
                     WHERE c.institucion_id = i.institucion_id) as total_docentes,
                    (SELECT COUNT(DISTINCT eg.estudiante_id)
                     FROM "Curso" c
                     JOIN "GrupoCurso" gc ON c.curso_id = gc.curso_id
                     JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id
                     WHERE c.institucion_id = i.institucion_id) as total_estudiantes,
                    (SELECT COUNT(*) FROM "Programa" p
                     WHERE p.institucion_id = i.institucion_id) as total_programas,
                    (SELECT COUNT(DISTINCT ic.coordinador_id)
                     FROM "InstitucionCoordinador" ic
                     WHERE ic.institucion_id = i.institucion_id) as total_coordinadores
                FROM "Institucion" i
                WHERE i.institucion_id = :institucion_id
            """
            )

            result = db.execute(
                stats_query, {"institucion_id": institucion_id}
            ).fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Institución no encontrada")

            estadisticas = dict(result._mapping)

            return {
                "success": True,
                "data": estadisticas,
                "message": "Estadísticas obtenidas exitosamente",
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo estadísticas: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error al obtener estadísticas: {e!s}"
            ) from e

    @staticmethod
    def completar_onboarding(
        db: Session,
        institucion_id: UUID,
        data: InstitucionOnboardingComplete,
        coordinador: Usuario,
    ) -> dict[str, Any]:
        """Completa el onboarding de una institución.

        Args:
            db: Sesión de base de datos
            institucion_id: ID de la institución
            data: Datos del onboarding
            coordinador: Usuario coordinador

        Returns:
            Dict con la institución actualizada y estado
        """
        try:
            # Verificar acceso
            if coordinador.rol != "coordinador":
                raise HTTPException(
                    status_code=403,
                    detail="Solo coordinadores pueden completar el onboarding",
                )

            # Verificar que tenga acceso a la institución
            query = text(
                """
                SELECT EXISTS(
                    SELECT 1 FROM "InstitucionCoordinador"
                    WHERE institucion_id = :institucion_id
                    AND coordinador_id = :coordinador_id
                )
            """
            )

            tiene_acceso = db.execute(
                query,
                {
                    "institucion_id": institucion_id,
                    "coordinador_id": coordinador.usuario_id,
                },
            ).scalar()

            if not tiene_acceso:
                raise HTTPException(
                    status_code=403, detail="No tienes acceso a esta institución"
                )

            # Obtener institución
            institucion = (
                db.query(Institucion)
                .filter(Institucion.institucion_id == institucion_id)
                .first()
            )

            if not institucion:
                raise HTTPException(status_code=404, detail="Institución no encontrada")

            # Actualizar campos del onboarding
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(institucion, field, value)

            db.add(institucion)
            db.commit()
            db.refresh(institucion)

            # Obtener estado del onboarding
            estado_onboarding = InstitucionService._calcular_estado_onboarding(
                institucion
            )

            logger.info(
                f"Onboarding actualizado para institución {institucion_id} por coordinador {coordinador.usuario_id}"
            )

            return {
                "success": True,
                "message": "Onboarding actualizado exitosamente",
                "data": {
                    "institucion_id": institucion.institucion_id,
                    "nombre": institucion.nombre,
                    "onboarding": estado_onboarding,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error completando onboarding: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error al completar onboarding: {e!s}"
            ) from e

    @staticmethod
    def actualizar_branding(
        db: Session,
        institucion_id: UUID,
        data: InstitucionBrandingUpdate,
        coordinador: Usuario,
    ) -> dict[str, Any]:
        """Actualiza el branding de una institución.

        Args:
            db: Sesión de base de datos
            institucion_id: ID de la institución
            data: Datos de branding
            coordinador: Usuario coordinador

        Returns:
            Dict con la institución actualizada
        """
        try:
            # Verificar acceso (reutilizar lógica de actualizar_institucion)
            if coordinador.rol != "coordinador":
                raise HTTPException(
                    status_code=403,
                    detail="Solo coordinadores pueden actualizar branding",
                )

            query = text(
                """
                SELECT EXISTS(
                    SELECT 1 FROM "InstitucionCoordinador"
                    WHERE institucion_id = :institucion_id
                    AND coordinador_id = :coordinador_id
                )
            """
            )

            tiene_acceso = db.execute(
                query,
                {
                    "institucion_id": institucion_id,
                    "coordinador_id": coordinador.usuario_id,
                },
            ).scalar()

            if not tiene_acceso:
                raise HTTPException(
                    status_code=403, detail="No tienes acceso a esta institución"
                )

            # Obtener institución
            institucion = (
                db.query(Institucion)
                .filter(Institucion.institucion_id == institucion_id)
                .first()
            )

            if not institucion:
                raise HTTPException(status_code=404, detail="Institución no encontrada")

            # Actualizar branding
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(institucion, field, value)

            db.add(institucion)
            db.commit()
            db.refresh(institucion)

            logger.info(
                f"Branding actualizado para institución {institucion_id} por coordinador {coordinador.usuario_id}"
            )

            return {
                "success": True,
                "message": "Branding actualizado exitosamente",
                "data": {
                    "institucion_id": institucion.institucion_id,
                    "nombre": institucion.nombre,
                    "logo_url": institucion.logo_url,
                    "color_primario": institucion.color_primario,
                    "color_secundario": institucion.color_secundario,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error actualizando branding: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error al actualizar branding: {e!s}"
            ) from e

    @staticmethod
    def agregar_dominio_adicional(
        db: Session, institucion_id: UUID, dominio: str, coordinador: Usuario
    ) -> dict[str, Any]:
        """Agrega un dominio adicional a una institución.

        Args:
            db: Sesión de base de datos
            institucion_id: ID de la institución
            dominio: Dominio a agregar (sin @)
            coordinador: Usuario coordinador

        Returns:
            Dict con la institución y lista de dominios
        """
        try:
            # Verificar acceso
            if coordinador.rol != "coordinador":
                raise HTTPException(
                    status_code=403,
                    detail="Solo coordinadores pueden agregar dominios",
                )

            query = text(
                """
                SELECT EXISTS(
                    SELECT 1 FROM "InstitucionCoordinador"
                    WHERE institucion_id = :institucion_id
                    AND coordinador_id = :coordinador_id
                )
            """
            )

            tiene_acceso = db.execute(
                query,
                {
                    "institucion_id": institucion_id,
                    "coordinador_id": coordinador.usuario_id,
                },
            ).scalar()

            if not tiene_acceso:
                raise HTTPException(
                    status_code=403, detail="No tienes acceso a esta institución"
                )

            # Obtener institución
            institucion = (
                db.query(Institucion)
                .filter(Institucion.institucion_id == institucion_id)
                .first()
            )

            if not institucion:
                raise HTTPException(status_code=404, detail="Institución no encontrada")

            # Limpiar y validar dominio
            dominio_clean = dominio.lower().strip()

            # Verificar que no sea el dominio principal
            if dominio_clean == institucion.dominio_principal:
                raise HTTPException(
                    status_code=400,
                    detail="Este dominio ya es el dominio principal de la institución",
                )

            # Verificar que no esté ya en la lista
            if institucion.dominios_adicionales and dominio_clean in [
                d.lower() for d in institucion.dominios_adicionales
            ]:
                raise HTTPException(
                    status_code=400,
                    detail="Este dominio ya está registrado en la institución",
                )

            # Verificar que no esté usado por otra institución
            dominio_existente = (
                db.query(Institucion)
                .filter(Institucion.dominio_principal == dominio_clean)
                .first()
            )

            if dominio_existente:
                raise HTTPException(
                    status_code=400,
                    detail=f"Este dominio ya está registrado por otra institución: {dominio_existente.nombre}",
                )

            # Agregar dominio
            if not institucion.dominios_adicionales:
                institucion.dominios_adicionales = []

            institucion.dominios_adicionales.append(dominio_clean)

            db.add(institucion)
            db.commit()
            db.refresh(institucion)

            logger.info(
                f"Dominio '{dominio_clean}' agregado a institución {institucion_id}"
            )

            return {
                "success": True,
                "message": "Dominio agregado exitosamente",
                "data": {
                    "institucion_id": institucion.institucion_id,
                    "nombre": institucion.nombre,
                    "dominio_principal": institucion.dominio_principal,
                    "dominios_adicionales": institucion.dominios_adicionales,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error agregando dominio: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Error al agregar dominio: {e!s}"
            ) from e

    @staticmethod
    def obtener_estado_onboarding(
        db: Session, institucion_id: UUID, coordinador: Usuario
    ) -> InstitucionOnboardingStatus:
        """Obtiene el estado del onboarding de una institución.

        Args:
            db: Sesión de base de datos
            institucion_id: ID de la institución
            coordinador: Usuario coordinador

        Returns:
            InstitucionOnboardingStatus con el progreso
        """
        try:
            # Verificar acceso
            if coordinador.rol != "coordinador":
                raise HTTPException(
                    status_code=403,
                    detail="Solo coordinadores pueden ver el estado del onboarding",
                )

            query = text(
                """
                SELECT EXISTS(
                    SELECT 1 FROM "InstitucionCoordinador"
                    WHERE institucion_id = :institucion_id
                    AND coordinador_id = :coordinador_id
                )
            """
            )

            tiene_acceso = db.execute(
                query,
                {
                    "institucion_id": institucion_id,
                    "coordinador_id": coordinador.usuario_id,
                },
            ).scalar()

            if not tiene_acceso:
                raise HTTPException(
                    status_code=403, detail="No tienes acceso a esta institución"
                )

            # Obtener institución
            institucion = (
                db.query(Institucion)
                .filter(Institucion.institucion_id == institucion_id)
                .first()
            )

            if not institucion:
                raise HTTPException(status_code=404, detail="Institución no encontrada")

            return InstitucionService._calcular_estado_onboarding(institucion)

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo estado onboarding: {e!s}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener estado del onboarding: {e!s}",
            ) from e

    @staticmethod
    def _calcular_estado_onboarding(
        institucion: Institucion,
    ) -> InstitucionOnboardingStatus:
        """Calcula el estado del onboarding basado en los campos completados.

        Args:
            institucion: Instancia de Institucion

        Returns:
            InstitucionOnboardingStatus
        """
        pasos = {
            "informacion_basica": bool(
                institucion.nombre
                and institucion.tipo_institucion
                and institucion.nivel_educativo
            ),
            "branding": bool(
                institucion.logo_url
                and institucion.color_primario
                and institucion.color_secundario
            ),
            "contacto": bool(
                institucion.direccion and institucion.telefono and institucion.ciudad
            ),
            "redes_sociales": bool(
                institucion.redes_sociales and len(institucion.redes_sociales) > 0
            ),
            "dominios": bool(
                institucion.dominio_principal
                or (
                    institucion.dominios_adicionales
                    and len(institucion.dominios_adicionales) > 0
                )
            ),
            "acreditacion": bool(
                institucion.acreditacion_nacional or institucion.acreditacion_internacional
            ),
        }

        completados = sum(pasos.values())
        total = len(pasos)
        porcentaje = int((completados / total) * 100)

        faltantes = [paso for paso, completado in pasos.items() if not completado]

        return InstitucionOnboardingStatus(
            onboarding_completo=completados == total,
            pasos_completados=pasos,
            pasos_faltantes=faltantes,
            porcentaje_completado=porcentaje,
        )


# Instancia global del servicio
institucion_service = InstitucionService()
