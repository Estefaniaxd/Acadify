"""CRUD para Período Académico.

Operaciones de base de datos para períodos académicos.
Sigue principios SOLID y Clean Code.
"""

from datetime import date
from typing import Any

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.enums.academic import EstadoPeriodo, TipoPeriodo
from src.models.academic.periodo_academico import PeriodoAcademico
from src.schemas.academic.periodo_academico_schemas import (
    PeriodoAcademicoCreate,
    PeriodoAcademicoUpdate,
)


class CRUDPeriodoAcademico(
    CRUDBase[PeriodoAcademico, PeriodoAcademicoCreate, PeriodoAcademicoUpdate]
):
    """CRUD para Período Académico.

    Extiende CRUDBase con operaciones específicas:
    - Búsqueda por institución
    - Filtros por año, tipo, estado
    - Obtención de período actual
    - Validaciones de negocio
    """

    # ==================== Operaciones Básicas ====================

    def get(self, db: Session, periodo_id: int) -> PeriodoAcademico | None:
        """Obtiene un período por ID."""
        return (
            db.query(PeriodoAcademico).filter(PeriodoAcademico.id == periodo_id).first()
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[PeriodoAcademico]:
        """Obtiene múltiples períodos con paginación."""
        return db.query(PeriodoAcademico).offset(skip).limit(limit).all()

    def create(
        self,
        db: Session,
        *,
        obj_in: PeriodoAcademicoCreate,
        creado_por_id: int | None = None,
    ) -> PeriodoAcademico:
        """Crea un nuevo período académico.

        Args:
            db: Sesión de base de datos
            obj_in: Datos del período a crear
            creado_por_id: ID del usuario que crea el período

        Returns:
            Período académico creado
        """
        obj_in_data = obj_in.model_dump()

        # Agregar auditoría
        if creado_por_id:
            obj_in_data["creado_por_id"] = creado_por_id

        db_obj = PeriodoAcademico(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: PeriodoAcademico,
        obj_in: PeriodoAcademicoUpdate,
        modificado_por_id: int | None = None,
    ) -> PeriodoAcademico:
        """Actualiza un período existente.

        Args:
            db: Sesión de base de datos
            db_obj: Objeto del período a actualizar
            obj_in: Datos para actualizar
            modificado_por_id: ID del usuario que modifica

        Returns:
            Período actualizado
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        # Agregar auditoría
        if modificado_por_id:
            update_data["modificado_por_id"] = modificado_por_id

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, periodo_id: int) -> PeriodoAcademico | None:
        """Elimina un período académico.

        NOTA: Solo eliminar períodos sin inscripciones/cursos asociados.
        Considerar soft delete en producción.
        """
        obj = self.get(db, periodo_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # ==================== Búsquedas Específicas ====================

    def get_by_codigo(self, db: Session, codigo: str) -> PeriodoAcademico | None:
        """Busca un período por su código único."""
        return (
            db.query(PeriodoAcademico).filter(PeriodoAcademico.codigo == codigo).first()
        )

    def get_by_institucion(
        self, db: Session, institucion_id: int, *, skip: int = 0, limit: int = 100
    ) -> list[PeriodoAcademico]:
        """Obtiene todos los períodos de una institución."""
        return (
            db.query(PeriodoAcademico)
            .filter(PeriodoAcademico.institucion_id == institucion_id)
            .order_by(
                PeriodoAcademico.anio.desc(), PeriodoAcademico.fecha_inicio.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_periodo_actual(
        self, db: Session, institucion_id: int
    ) -> PeriodoAcademico | None:
        """Obtiene el período académico actual de una institución.

        Primero busca el marcado como 'es_actual=True'.
        Si no hay, busca el que contenga la fecha actual.
        """
        # Intentar obtener el marcado como actual
        periodo = (
            db.query(PeriodoAcademico)
            .filter(
                and_(
                    PeriodoAcademico.institucion_id == institucion_id,
                    PeriodoAcademico.es_actual,
                    PeriodoAcademico.activo,
                )
            )
            .first()
        )

        if periodo:
            return periodo

        # Si no hay, buscar por fechas
        hoy = date.today()
        return (
            db.query(PeriodoAcademico)
            .filter(
                and_(
                    PeriodoAcademico.institucion_id == institucion_id,
                    PeriodoAcademico.fecha_inicio <= hoy,
                    PeriodoAcademico.fecha_fin >= hoy,
                    PeriodoAcademico.activo,
                )
            )
            .order_by(PeriodoAcademico.fecha_inicio.desc())
            .first()
        )

    def get_periodos_activos(
        self, db: Session, institucion_id: int, *, skip: int = 0, limit: int = 100
    ) -> list[PeriodoAcademico]:
        """Obtiene períodos activos de una institución."""
        return (
            db.query(PeriodoAcademico)
            .filter(
                and_(
                    PeriodoAcademico.institucion_id == institucion_id,
                    PeriodoAcademico.activo,
                    PeriodoAcademico.estado != EstadoPeriodo.cancelado,
                )
            )
            .order_by(
                PeriodoAcademico.anio.desc(), PeriodoAcademico.fecha_inicio.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_anio(
        self,
        db: Session,
        institucion_id: int,
        anio: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PeriodoAcademico]:
        """Obtiene períodos de un año específico."""
        return (
            db.query(PeriodoAcademico)
            .filter(
                and_(
                    PeriodoAcademico.institucion_id == institucion_id,
                    PeriodoAcademico.anio == anio,
                )
            )
            .order_by(PeriodoAcademico.numero_periodo, PeriodoAcademico.fecha_inicio)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_tipo(
        self,
        db: Session,
        institucion_id: int,
        tipo: TipoPeriodo,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PeriodoAcademico]:
        """Obtiene períodos de un tipo específico."""
        return (
            db.query(PeriodoAcademico)
            .filter(
                and_(
                    PeriodoAcademico.institucion_id == institucion_id,
                    PeriodoAcademico.tipo == tipo,
                )
            )
            .order_by(
                PeriodoAcademico.anio.desc(), PeriodoAcademico.fecha_inicio.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_estado(
        self,
        db: Session,
        institucion_id: int,
        estado: EstadoPeriodo,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PeriodoAcademico]:
        """Obtiene períodos por estado."""
        return (
            db.query(PeriodoAcademico)
            .filter(
                and_(
                    PeriodoAcademico.institucion_id == institucion_id,
                    PeriodoAcademico.estado == estado,
                )
            )
            .order_by(
                PeriodoAcademico.anio.desc(), PeriodoAcademico.fecha_inicio.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_periodos_con_inscripciones_abiertas(
        self, db: Session, institucion_id: int
    ) -> list[PeriodoAcademico]:
        """Obtiene períodos que actualmente aceptan inscripciones.

        Verifica:
        - Estado sea 'inscripciones_abiertas'
        - Fecha actual esté en rango de inscripciones
        - Período esté activo
        """
        hoy = date.today()
        return (
            db.query(PeriodoAcademico)
            .filter(
                and_(
                    PeriodoAcademico.institucion_id == institucion_id,
                    PeriodoAcademico.activo,
                    PeriodoAcademico.permite_inscripciones,
                    PeriodoAcademico.estado == EstadoPeriodo.inscripciones_abiertas,
                    PeriodoAcademico.fecha_inicio_inscripciones <= hoy,
                    PeriodoAcademico.fecha_fin_inscripciones >= hoy,
                )
            )
            .all()
        )

    def get_periodos_en_curso(
        self, db: Session, institucion_id: int
    ) -> list[PeriodoAcademico]:
        """Obtiene períodos que están actualmente en curso."""
        hoy = date.today()
        return (
            db.query(PeriodoAcademico)
            .filter(
                and_(
                    PeriodoAcademico.institucion_id == institucion_id,
                    PeriodoAcademico.activo,
                    PeriodoAcademico.estado == EstadoPeriodo.en_curso,
                    PeriodoAcademico.fecha_inicio_clases <= hoy,
                    PeriodoAcademico.fecha_fin_clases >= hoy,
                )
            )
            .all()
        )

    def get_periodos_proximos(
        self, db: Session, institucion_id: int, dias: int = 30
    ) -> list[PeriodoAcademico]:
        """Obtiene períodos que iniciarán en los próximos N días.

        Args:
            institucion_id: ID de la institución
            dias: Días hacia adelante a considerar
        """
        from datetime import timedelta

        hoy = date.today()
        fecha_limite = hoy + timedelta(days=dias)

        return (
            db.query(PeriodoAcademico)
            .filter(
                and_(
                    PeriodoAcademico.institucion_id == institucion_id,
                    PeriodoAcademico.activo,
                    PeriodoAcademico.fecha_inicio_clases >= hoy,
                    PeriodoAcademico.fecha_inicio_clases <= fecha_limite,
                )
            )
            .order_by(PeriodoAcademico.fecha_inicio_clases)
            .all()
        )

    # ==================== Filtros Avanzados ====================

    def get_by_filtros(
        self,
        db: Session,
        institucion_id: int,
        *,
        tipo: TipoPeriodo | None = None,
        estado: EstadoPeriodo | None = None,
        anio: int | None = None,
        activo: bool | None = None,
        visible_estudiantes: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[PeriodoAcademico], int]:
        """Busca períodos aplicando múltiples filtros.

        Returns:
            Tupla (lista_periodos, total_count)
        """
        # Base query
        query = db.query(PeriodoAcademico).filter(
            PeriodoAcademico.institucion_id == institucion_id
        )

        # Aplicar filtros opcionales
        if tipo:
            query = query.filter(PeriodoAcademico.tipo == tipo)
        if estado:
            query = query.filter(PeriodoAcademico.estado == estado)
        if anio:
            query = query.filter(PeriodoAcademico.anio == anio)
        if activo is not None:
            query = query.filter(PeriodoAcademico.activo == activo)
        if visible_estudiantes is not None:
            query = query.filter(
                PeriodoAcademico.visible_estudiantes == visible_estudiantes
            )

        # Contar total antes de paginar
        total = query.count()

        # Ordenar y paginar
        periodos = (
            query.order_by(
                PeriodoAcademico.anio.desc(),
                PeriodoAcademico.numero_periodo.desc(),
                PeriodoAcademico.fecha_inicio.desc(),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        return periodos, total

    def search_by_nombre_o_codigo(
        self,
        db: Session,
        institucion_id: int,
        busqueda: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PeriodoAcademico]:
        """Busca períodos por nombre o código (búsqueda parcial)."""
        search_pattern = f"%{busqueda}%"
        return (
            db.query(PeriodoAcademico)
            .filter(
                and_(
                    PeriodoAcademico.institucion_id == institucion_id,
                    or_(
                        PeriodoAcademico.nombre.ilike(search_pattern),
                        PeriodoAcademico.codigo.ilike(search_pattern),
                    ),
                )
            )
            .order_by(
                PeriodoAcademico.anio.desc(), PeriodoAcademico.fecha_inicio.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ==================== Operaciones de Estado ====================

    def activar(
        self, db: Session, periodo_id: int, modificado_por_id: int | None = None
    ) -> PeriodoAcademico | None:
        """Activa un período académico."""
        periodo = self.get(db, periodo_id)
        if not periodo:
            return None

        periodo.activar()
        if modificado_por_id:
            periodo.modificado_por_id = modificado_por_id

        db.add(periodo)
        db.commit()
        db.refresh(periodo)
        return periodo

    def desactivar(
        self, db: Session, periodo_id: int, modificado_por_id: int | None = None
    ) -> PeriodoAcademico | None:
        """Desactiva un período académico."""
        periodo = self.get(db, periodo_id)
        if not periodo:
            return None

        periodo.desactivar()
        if modificado_por_id:
            periodo.modificado_por_id = modificado_por_id

        db.add(periodo)
        db.commit()
        db.refresh(periodo)
        return periodo

    def marcar_como_actual(
        self,
        db: Session,
        periodo_id: int,
        institucion_id: int,
        modificado_por_id: int | None = None,
    ) -> PeriodoAcademico | None:
        """Marca un período como actual.

        Desmarca cualquier otro período como actual en la misma institución.
        """
        # Desmarcar todos los períodos actuales de la institución
        db.query(PeriodoAcademico).filter(
            and_(
                PeriodoAcademico.institucion_id == institucion_id,
                PeriodoAcademico.es_actual,
            )
        ).update({"es_actual": False})

        # Marcar el nuevo período como actual
        periodo = self.get(db, periodo_id)
        if not periodo:
            return None

        periodo.marcar_como_actual()
        if modificado_por_id:
            periodo.modificado_por_id = modificado_por_id

        db.add(periodo)
        db.commit()
        db.refresh(periodo)
        return periodo

    def finalizar(
        self, db: Session, periodo_id: int, modificado_por_id: int | None = None
    ) -> PeriodoAcademico | None:
        """Finaliza un período académico."""
        periodo = self.get(db, periodo_id)
        if not periodo:
            return None

        periodo.finalizar()
        if modificado_por_id:
            periodo.modificado_por_id = modificado_por_id

        db.add(periodo)
        db.commit()
        db.refresh(periodo)
        return periodo

    def cancelar(
        self,
        db: Session,
        periodo_id: int,
        motivo: str,
        modificado_por_id: int | None = None,
    ) -> PeriodoAcademico | None:
        """Cancela un período académico con motivo."""
        periodo = self.get(db, periodo_id)
        if not periodo:
            return None

        periodo.cancelar(motivo)
        if modificado_por_id:
            periodo.modificado_por_id = modificado_por_id

        db.add(periodo)
        db.commit()
        db.refresh(periodo)
        return periodo

    # ==================== Validaciones ====================

    def existe_codigo(
        self, db: Session, codigo: str, excluir_id: int | None = None
    ) -> bool:
        """Verifica si ya existe un período con el código dado.

        Args:
            codigo: Código a verificar
            excluir_id: ID a excluir de la búsqueda (para updates)
        """
        query = db.query(PeriodoAcademico).filter(PeriodoAcademico.codigo == codigo)

        if excluir_id:
            query = query.filter(PeriodoAcademico.id != excluir_id)

        return query.first() is not None

    def tiene_conflicto_fechas(
        self,
        db: Session,
        institucion_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        tipo: TipoPeriodo,
        excluir_id: int | None = None,
    ) -> bool:
        """Verifica si hay conflicto de fechas con otros períodos del mismo tipo.

        Retorna True si hay conflicto (períodos superpuestos).
        """
        query = db.query(PeriodoAcademico).filter(
            and_(
                PeriodoAcademico.institucion_id == institucion_id,
                PeriodoAcademico.tipo == tipo,
                PeriodoAcademico.activo,
                or_(
                    # El nuevo período inicia durante otro período
                    and_(
                        PeriodoAcademico.fecha_inicio <= fecha_inicio,
                        PeriodoAcademico.fecha_fin >= fecha_inicio,
                    ),
                    # El nuevo período termina durante otro período
                    and_(
                        PeriodoAcademico.fecha_inicio <= fecha_fin,
                        PeriodoAcademico.fecha_fin >= fecha_fin,
                    ),
                    # El nuevo período contiene otro período completo
                    and_(
                        PeriodoAcademico.fecha_inicio >= fecha_inicio,
                        PeriodoAcademico.fecha_fin <= fecha_fin,
                    ),
                ),
            )
        )

        if excluir_id:
            query = query.filter(PeriodoAcademico.id != excluir_id)

        return query.first() is not None

    # ==================== Estadísticas ====================

    def get_estadisticas(
        self, db: Session, institucion_id: int, periodo_id: int
    ) -> dict[str, Any]:
        """Obtiene estadísticas de un período académico.

        TODO: Implementar cuando se creen modelos de Inscripcion, Grupo, etc.
        """
        periodo = self.get(db, periodo_id)
        if not periodo:
            return {}

        # Estadísticas básicas
        return {
            "periodo_id": periodo_id,
            "nombre": periodo.nombre,
            "codigo": periodo.codigo,
            "estado": periodo.estado,
            "tipo": periodo.tipo,
            "activo": periodo.activo,
            "es_actual": periodo.es_actual,
            "permite_inscribirse_ahora": periodo.permite_inscribirse_ahora,
            "esta_en_curso": periodo.esta_en_curso,
            "dias_hasta_inicio": periodo.dias_hasta_inicio,
            "dias_transcurridos": periodo.dias_transcurridos,
            "duracion_dias": periodo.duracion_dias,
            "porcentaje_avance": periodo.porcentaje_avance,
        }

        # TODO: Agregar cuando existan los modelos:
        # - total_inscripciones
        # - total_grupos
        # - total_cursos
        # - total_estudiantes
        # - total_profesores

    def count_by_institucion(self, db: Session, institucion_id: int) -> int:
        """Cuenta total de períodos de una institución."""
        return (
            db.query(PeriodoAcademico)
            .filter(PeriodoAcademico.institucion_id == institucion_id)
            .count()
        )

    def count_activos(self, db: Session, institucion_id: int) -> int:
        """Cuenta períodos activos de una institución."""
        return (
            db.query(PeriodoAcademico)
            .filter(
                and_(
                    PeriodoAcademico.institucion_id == institucion_id,
                    PeriodoAcademico.activo,
                )
            )
            .count()
        )


# Instancia singleton para usar en toda la aplicación
periodo_academico_crud = CRUDPeriodoAcademico(PeriodoAcademico)
