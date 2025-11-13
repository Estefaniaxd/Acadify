"""Service para gestión de Períodos Académicos.

Contiene toda la lógica de negocio relacionada con períodos académicos.
Implementa validaciones, cambios de estado, verificación de fechas y cache.

Principios SOLID aplicados:
- Single Responsibility: Cada método tiene una responsabilidad clara
- Open/Closed: Extensible sin modificar código existente
- Dependency Inversion: Depende de abstracciones (CRUD)
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.redis_manager import RedisManager
from src.crud.academic.crud_institucion import institucion_crud
from src.crud.academic.crud_periodo_academico import periodo_academico_crud
from src.enums.academic import EstadoPeriodo, TipoPeriodo
from src.models.academic.periodo_academico import PeriodoAcademico
from src.models.users.usuario import Usuario
from src.schemas.academic.periodo_academico_schemas import (
    PeriodoAcademicoCreate,
    PeriodoAcademicoUpdate,
)


logger = logging.getLogger(__name__)


class PeriodoAcademicoService:
    """Servicio para gestión de períodos académicos.

    Responsabilidades:
    - Validaciones de negocio
    - Gestión de estados
    - Cache de períodos
    - Verificación de permisos
    - Lógica de inscripciones
    """

    # Prefijo para cache en Redis
    CACHE_PREFIX = "periodo_academico"
    CACHE_TTL = 3600  # 1 hora

    def __init__(self, redis_manager: RedisManager | None = None) -> None:
        """Inicializa el servicio.

        Args:
            redis_manager: Gestor de Redis para cache (opcional)
        """
        self.redis = redis_manager

    # ==================== Operaciones de Creación ====================

    def crear_periodo(
        self, db: Session, periodo_in: PeriodoAcademicoCreate, usuario: Usuario
    ) -> PeriodoAcademico:
        """Crea un nuevo período académico con validaciones.

        Args:
            db: Sesión de base de datos
            periodo_in: Datos del período
            usuario: Usuario que crea el período

        Returns:
            Período creado

        Raises:
            HTTPException: Si falla alguna validación
        """
        try:
            # 1. Validar que la institución existe
            institucion = institucion_crud.get(db, periodo_in.institucion_id)
            if not institucion:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Institución {periodo_in.institucion_id} no encontrada",
                )

            # 2. Validar permisos del usuario
            self._validar_permisos_institucion(usuario, periodo_in.institucion_id)

            # 3. Validar código único
            if periodo_academico_crud.existe_codigo(db, periodo_in.codigo):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un período con código '{periodo_in.codigo}'",
                )

            # 4. Validar coherencia de fechas
            self._validar_coherencia_fechas(periodo_in)

            # 5. Validar conflictos con otros períodos
            if periodo_academico_crud.tiene_conflicto_fechas(
                db,
                periodo_in.institucion_id,
                periodo_in.fecha_inicio,
                periodo_in.fecha_fin,
                periodo_in.tipo,
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El período tiene conflicto de fechas con otro período de tipo '{periodo_in.tipo.value}'",
                )

            # 6. Crear el período
            periodo = periodo_academico_crud.create(
                db, obj_in=periodo_in, creado_por_id=usuario.usuario_id
            )

            # 7. Invalidar cache
            self._invalidar_cache_institucion(periodo_in.institucion_id)

            logger.info(
                f"Período '{periodo.nombre}' creado por usuario {usuario.usuario_id} "
                f"en institución {periodo_in.institucion_id}"
            )

            return periodo

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error creando período: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno al crear período: {e!s}",
            ) from e

    # ==================== Operaciones de Consulta ====================

    def obtener_periodo(
        self, db: Session, periodo_id: int, usuario: Usuario
    ) -> PeriodoAcademico:
        """Obtiene un período por ID con validaciones.

        Intenta obtener de cache primero, luego de BD.
        """
        try:
            # Intentar obtener de cache
            if self.redis:
                cache_key = f"{self.CACHE_PREFIX}:id:{periodo_id}"
                cached = self.redis.get_json(cache_key)
                if cached:
                    logger.debug(f"Período {periodo_id} obtenido de cache")
                    # Convertir a modelo
                    return PeriodoAcademico(**cached)

            # Obtener de BD
            periodo = periodo_academico_crud.get(db, periodo_id)
            if not periodo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Período {periodo_id} no encontrado",
                )

            # Validar permisos
            self._validar_permisos_institucion(usuario, periodo.institucion_id)

            # Guardar en cache
            if self.redis:
                self.redis.set_json(cache_key, periodo, ttl=self.CACHE_TTL)

            return periodo

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo período: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {e!s}",
            ) from e

    def listar_periodos(
        self,
        db: Session,
        institucion_id: int,
        usuario: Usuario,
        *,
        tipo: TipoPeriodo | None = None,
        estado: EstadoPeriodo | None = None,
        anio: int | None = None,
        activo: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[PeriodoAcademico], int]:
        """Lista períodos con filtros y paginación.

        Returns:
            Tupla (lista_periodos, total_count)
        """
        try:
            # Validar permisos
            self._validar_permisos_institucion(usuario, institucion_id)

            # Aplicar filtros según rol
            visible_estudiantes = None
            if usuario.rol == "estudiante":
                visible_estudiantes = True

            # Obtener períodos
            periodos, total = periodo_academico_crud.get_by_filtros(
                db,
                institucion_id,
                tipo=tipo,
                estado=estado,
                anio=anio,
                activo=activo,
                visible_estudiantes=visible_estudiantes,
                skip=skip,
                limit=limit,
            )

            return periodos, total

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error listando períodos: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {e!s}",
            ) from e

    def obtener_periodo_actual(
        self, db: Session, institucion_id: int, usuario: Usuario
    ) -> PeriodoAcademico | None:
        """Obtiene el período académico actual.

        Usa cache agresivo porque se consulta frecuentemente.
        """
        try:
            # Validar permisos
            self._validar_permisos_institucion(usuario, institucion_id)

            # Intentar cache
            if self.redis:
                cache_key = f"{self.CACHE_PREFIX}:actual:{institucion_id}"
                cached = self.redis.get_json(cache_key)
                if cached:
                    return PeriodoAcademico(**cached)

            # Obtener de BD
            periodo = periodo_academico_crud.get_periodo_actual(db, institucion_id)

            # Guardar en cache (TTL corto porque puede cambiar)
            if self.redis and periodo:
                cache_key = f"{self.CACHE_PREFIX}:actual:{institucion_id}"
                self.redis.set_json(cache_key, periodo, ttl=600)  # 10 min

            return periodo

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo período actual: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {e!s}",
            ) from e

    def obtener_periodos_con_inscripciones_abiertas(
        self, db: Session, institucion_id: int, usuario: Usuario
    ) -> list[PeriodoAcademico]:
        """Obtiene períodos que actualmente aceptan inscripciones."""
        try:
            self._validar_permisos_institucion(usuario, institucion_id)
            return periodo_academico_crud.get_periodos_con_inscripciones_abiertas(
                db, institucion_id
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo períodos con inscripciones: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {e!s}",
            ) from e

    # ==================== Operaciones de Actualización ====================

    def actualizar_periodo(
        self,
        db: Session,
        periodo_id: int,
        periodo_update: PeriodoAcademicoUpdate,
        usuario: Usuario,
    ) -> PeriodoAcademico:
        """Actualiza un período con validaciones."""
        try:
            # Obtener período existente
            periodo = periodo_academico_crud.get(db, periodo_id)
            if not periodo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Período {periodo_id} no encontrado",
                )

            # Validar permisos
            self._validar_permisos_institucion(usuario, periodo.institucion_id)

            # Validar código si se proporciona y es diferente del actual
            # Principio SOLID: Defensive Programming - usar hasattr para Optional
            # Usar getattr con default None es más seguro que acceso directo
            codigo_nuevo = getattr(periodo_update, "codigo", None)
            if codigo_nuevo is not None and codigo_nuevo != periodo.codigo:
                if periodo_academico_crud.existe_codigo(
                    db, codigo_nuevo, excluir_id=periodo_id
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ya existe otro período con código '{codigo_nuevo}'",
                    )

            # Validar coherencia de fechas si se modifican
            # Principio: Guard Clauses - validar condiciones tempranas
            fecha_inicio_nueva = getattr(periodo_update, "fecha_inicio", None)
            fecha_fin_nueva = getattr(periodo_update, "fecha_fin", None)

            if fecha_inicio_nueva is not None or fecha_fin_nueva is not None:
                fecha_inicio = (
                    fecha_inicio_nueva
                    if fecha_inicio_nueva is not None
                    else periodo.fecha_inicio
                )
                fecha_fin = (
                    fecha_fin_nueva
                    if fecha_fin_nueva is not None
                    else periodo.fecha_fin
                )

                if fecha_inicio >= fecha_fin:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="La fecha de fin debe ser posterior a la fecha de inicio",
                    )

            # Actualizar
            periodo_actualizado = periodo_academico_crud.update(
                db,
                db_obj=periodo,
                obj_in=periodo_update,
                modificado_por_id=usuario.usuario_id,
            )

            # Invalidar cache
            self._invalidar_cache_periodo(periodo_id, periodo.institucion_id)

            logger.info(
                f"Período {periodo_id} actualizado por usuario {usuario.usuario_id}"
            )

            return periodo_actualizado

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error actualizando período: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {e!s}",
            ) from e

    # ==================== Operaciones de Estado ====================

    def activar_periodo(
        self, db: Session, periodo_id: int, usuario: Usuario
    ) -> PeriodoAcademico:
        """Activa un período."""
        try:
            periodo = periodo_academico_crud.get(db, periodo_id)
            if not periodo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Período {periodo_id} no encontrado",
                )

            self._validar_permisos_institucion(usuario, periodo.institucion_id)

            periodo_activado = periodo_academico_crud.activar(
                db, periodo_id, modificado_por_id=usuario.usuario_id
            )

            self._invalidar_cache_periodo(periodo_id, periodo.institucion_id)
            logger.info(
                f"Período {periodo_id} activado por usuario {usuario.usuario_id}"
            )

            return periodo_activado

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error activando período: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {e!s}",
            ) from e

    def marcar_como_actual(
        self, db: Session, periodo_id: int, usuario: Usuario
    ) -> PeriodoAcademico:
        """Marca un período como actual."""
        try:
            periodo = periodo_academico_crud.get(db, periodo_id)
            if not periodo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Período {periodo_id} no encontrado",
                )

            self._validar_permisos_institucion(usuario, periodo.institucion_id)

            # Validar que el período esté en estado válido para ser marcado como actual
            # Nota: estado es string (no enum), por lo tanto no usar .value
            estados_validos = [EstadoPeriodo.programado, EstadoPeriodo.en_curso]
            if periodo.estado not in estados_validos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se puede marcar como actual un período en estado '{periodo.estado}'",
                )

            periodo_actual = periodo_academico_crud.marcar_como_actual(
                db,
                periodo_id,
                periodo.institucion_id,
                modificado_por_id=usuario.usuario_id,
            )

            # Invalidar cache de toda la institución (cambió el período actual)
            self._invalidar_cache_institucion(periodo.institucion_id)

            logger.info(
                f"Período {periodo_id} marcado como actual por usuario {usuario.usuario_id}"
            )

            return periodo_actual

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error marcando período como actual: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {e!s}",
            ) from e

    def finalizar_periodo(
        self, db: Session, periodo_id: int, usuario: Usuario
    ) -> PeriodoAcademico:
        """Finaliza un período."""
        try:
            periodo = periodo_academico_crud.get(db, periodo_id)
            if not periodo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Período {periodo_id} no encontrado",
                )

            self._validar_permisos_institucion(usuario, periodo.institucion_id)

            # Validar que esté en estado válido para finalización
            # Nota: estado es string (no enum), por lo tanto no usar .value
            estados_validos = [EstadoPeriodo.en_curso, EstadoPeriodo.evaluaciones]
            if periodo.estado not in estados_validos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se puede finalizar un período en estado '{periodo.estado}'",
                )

            periodo_finalizado = periodo_academico_crud.finalizar(
                db, periodo_id, modificado_por_id=usuario.usuario_id
            )

            self._invalidar_cache_periodo(periodo_id, periodo.institucion_id)
            logger.info(
                f"Período {periodo_id} finalizado por usuario {usuario.usuario_id}"
            )

            return periodo_finalizado

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error finalizando período: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {e!s}",
            ) from e

    def cancelar_periodo(
        self, db: Session, periodo_id: int, motivo: str, usuario: Usuario
    ) -> PeriodoAcademico:
        """Cancela un período con motivo."""
        try:
            periodo = periodo_academico_crud.get(db, periodo_id)
            if not periodo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Período {periodo_id} no encontrado",
                )

            self._validar_permisos_institucion(usuario, periodo.institucion_id)

            # Validar que no esté finalizado
            if periodo.estado == EstadoPeriodo.finalizado:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede cancelar un período finalizado",
                )

            periodo_cancelado = periodo_academico_crud.cancelar(
                db, periodo_id, motivo, modificado_por_id=usuario.usuario_id
            )

            self._invalidar_cache_periodo(periodo_id, periodo.institucion_id)
            logger.warning(
                f"Período {periodo_id} cancelado por usuario {usuario.usuario_id}. Motivo: {motivo}"
            )

            return periodo_cancelado

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error cancelando período: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {e!s}",
            ) from e

    # ==================== Validaciones Privadas ====================

    def _validar_permisos_institucion(
        self, usuario: Usuario, institucion_id: int
    ) -> None:
        """Valida que el usuario tenga permisos sobre la institución.

        Raises:
            HTTPException: Si no tiene permisos
        """
        # Superadmin tiene acceso a todo
        if usuario.rol == "superadmin":
            return

        # Coordinadores deben estar asociados a la institución
        if usuario.rol == "coordinador":
            # TODO: Verificar en tabla InstitucionCoordinador
            return

        # Estudiantes y docentes solo lectura
        if usuario.rol in ["estudiante", "docente"]:
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuario con rol '{usuario.rol}' no tiene permisos sobre esta institución",
        )

    def _validar_coherencia_fechas(self, periodo: PeriodoAcademicoCreate) -> None:
        """Valida coherencia lógica de todas las fechas.

        Reglas:
        - fecha_fin > fecha_inicio
        - inscripciones antes o durante el período
        - clases dentro del período
        - etc.
        """
        # Fecha fin del período
        if periodo.fecha_fin <= periodo.fecha_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de fin debe ser posterior a la fecha de inicio",
            )

        # Inscripciones
        if periodo.fecha_fin_inscripciones < periodo.fecha_inicio_inscripciones:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha fin de inscripciones debe ser posterior al inicio",
            )

        # Clases deben estar dentro del período
        if periodo.fecha_inicio_clases < periodo.fecha_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El inicio de clases no puede ser antes del inicio del período",
            )

        if periodo.fecha_fin_clases > periodo.fecha_fin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El fin de clases no puede ser después del fin del período",
            )

        # Inscripciones deben cerrar antes o al iniciar clases
        if periodo.fecha_fin_inscripciones > periodo.fecha_inicio_clases:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las inscripciones deben cerrar antes del inicio de clases",
            )

    # ==================== Cache ====================

    def _invalidar_cache_periodo(self, periodo_id: int, institucion_id: int) -> None:
        """Invalida cache de un período específico."""
        if not self.redis:
            return

        try:
            self.redis.delete(f"{self.CACHE_PREFIX}:id:{periodo_id}")
            self.redis.delete(f"{self.CACHE_PREFIX}:actual:{institucion_id}")
            logger.debug(f"Cache invalidado para período {periodo_id}")
        except Exception as e:
            logger.warning(f"Error invalidando cache: {e!s}")

    def _invalidar_cache_institucion(self, institucion_id: int) -> None:
        """Invalida todo el cache de una institución."""
        if not self.redis:
            return

        try:
            pattern = f"{self.CACHE_PREFIX}:*:{institucion_id}*"
            self.redis.delete_pattern(pattern)
            logger.debug(f"Cache invalidado para institución {institucion_id}")
        except Exception as e:
            logger.warning(f"Error invalidando cache de institución: {e!s}")


# Instancia singleton del servicio
periodo_academico_service = PeriodoAcademicoService()
