"""CRUD para Inscripciones.

Operaciones de base de datos para el sistema de inscripciones.
Implementa SOLID: Single Responsibility, Open/Closed, Dependency Inversion.
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.enums.academic import (
    EstadoInscripcion,
    MotivoRechazo,
    MotivoRetiro,
    TipoInscripcion,
)
from src.models.academic.inscripcion import Inscripcion
from src.schemas.academic.inscripcion_schemas import (
    InscripcionCreate,
    InscripcionUpdate,
)


class CRUDInscripcion(CRUDBase[Inscripcion, InscripcionCreate, InscripcionUpdate]):
    """CRUD para Inscripciones.

    Responsabilidades:
    - Operaciones CRUD básicas
    - Búsquedas y filtros complejos
    - Validaciones de negocio
    - Gestión de estados
    - Reportes y estadísticas
    """

    # ==================== CRUD Básico ====================

    def create(
        self,
        db: Session,
        *,
        obj_in: InscripcionCreate,
        creado_por_id: int | None = None,
    ) -> Inscripcion:
        """Crea una nueva inscripción.

        Genera automáticamente código único.
        """
        obj_in_data = obj_in.model_dump()

        # Generar código único
        codigo = self._generar_codigo_inscripcion(
            db, obj_in.estudiante_id, obj_in.grupo_id
        )
        obj_in_data["codigo_inscripcion"] = codigo

        # Auditoría
        if creado_por_id:
            obj_in_data["creado_por_id"] = creado_por_id

        db_obj = Inscripcion(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Inscripcion,
        obj_in: InscripcionUpdate,
        modificado_por_id: int | None = None,
    ) -> Inscripcion:
        """Actualiza una inscripción existente."""
        update_data = obj_in.model_dump(exclude_unset=True)

        if modificado_por_id:
            update_data["modificado_por_id"] = modificado_por_id

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # ==================== Búsquedas ====================

    def get_by_codigo(self, db: Session, codigo: str) -> Inscripcion | None:
        """Obtiene inscripción por código."""
        return (
            db.query(Inscripcion)
            .filter(Inscripcion.codigo_inscripcion == codigo)
            .first()
        )

    def get_by_estudiante(
        self, db: Session, estudiante_id: int, *, skip: int = 0, limit: int = 100
    ) -> list[Inscripcion]:
        """Obtiene inscripciones de un estudiante."""
        return (
            db.query(Inscripcion)
            .filter(Inscripcion.estudiante_id == estudiante_id)
            .order_by(desc(Inscripcion.fecha_creacion))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_grupo(
        self, db: Session, grupo_id: int, *, skip: int = 0, limit: int = 100
    ) -> list[Inscripcion]:
        """Obtiene inscripciones de un grupo."""
        return (
            db.query(Inscripcion)
            .filter(Inscripcion.grupo_id == grupo_id)
            .order_by(Inscripcion.numero_lista, Inscripcion.fecha_creacion)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_periodo(
        self, db: Session, periodo_academico_id: int, *, skip: int = 0, limit: int = 100
    ) -> list[Inscripcion]:
        """Obtiene inscripciones de un período."""
        return (
            db.query(Inscripcion)
            .filter(Inscripcion.periodo_academico_id == periodo_academico_id)
            .order_by(desc(Inscripcion.fecha_creacion))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_programa(
        self, db: Session, programa_id: int, *, skip: int = 0, limit: int = 100
    ) -> list[Inscripcion]:
        """Obtiene inscripciones de un programa."""
        return (
            db.query(Inscripcion)
            .filter(Inscripcion.programa_id == programa_id)
            .order_by(desc(Inscripcion.fecha_creacion))
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ==================== Búsquedas por Estado ====================

    def get_activas(
        self,
        db: Session,
        *,
        grupo_id: int | None = None,
        periodo_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Inscripcion]:
        """Obtiene inscripciones activas."""
        query = db.query(Inscripcion).filter(
            and_(
                Inscripcion.activo,
                Inscripcion.estado.in_(
                    [
                        EstadoInscripcion.aprobada,
                        EstadoInscripcion.confirmada,
                        EstadoInscripcion.activa,
                    ]
                ),
            )
        )

        if grupo_id:
            query = query.filter(Inscripcion.grupo_id == grupo_id)
        if periodo_id:
            query = query.filter(Inscripcion.periodo_academico_id == periodo_id)

        return (
            query.order_by(desc(Inscripcion.fecha_creacion))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pendientes(
        self,
        db: Session,
        *,
        tipo_pendiente: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Inscripcion]:
        """Obtiene inscripciones pendientes.

        tipo_pendiente puede ser: 'pago', 'documentos', 'aprobacion'
        """
        if tipo_pendiente == "pago":
            estado = EstadoInscripcion.pendiente_pago
        elif tipo_pendiente == "documentos":
            estado = EstadoInscripcion.pendiente_documentos
        elif tipo_pendiente == "aprobacion":
            estado = EstadoInscripcion.pendiente_aprobacion
        else:
            # Todos los pendientes
            query = db.query(Inscripcion).filter(
                Inscripcion.estado.in_(
                    [
                        EstadoInscripcion.pre_inscrita,
                        EstadoInscripcion.pendiente_pago,
                        EstadoInscripcion.pendiente_documentos,
                        EstadoInscripcion.pendiente_aprobacion,
                    ]
                )
            )
            return (
                query.order_by(Inscripcion.fecha_solicitud)
                .offset(skip)
                .limit(limit)
                .all()
            )

        return (
            db.query(Inscripcion)
            .filter(Inscripcion.estado == estado)
            .order_by(Inscripcion.fecha_solicitud)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_lista_espera(self, db: Session, grupo_id: int) -> list[Inscripcion]:
        """Obtiene lista de espera de un grupo ordenada por posición."""
        return (
            db.query(Inscripcion)
            .filter(
                and_(
                    Inscripcion.grupo_id == grupo_id,
                    Inscripcion.en_lista_espera,
                    Inscripcion.estado == EstadoInscripcion.en_lista_espera,
                )
            )
            .order_by(Inscripcion.posicion_lista_espera)
            .all()
        )

    # ==================== Validaciones ====================

    def existe_inscripcion(
        self,
        db: Session,
        estudiante_id: int,
        grupo_id: int,
        excluir_id: int | None = None,
    ) -> bool:
        """Verifica si ya existe una inscripción activa."""
        query = db.query(Inscripcion).filter(
            and_(
                Inscripcion.estudiante_id == estudiante_id,
                Inscripcion.grupo_id == grupo_id,
                Inscripcion.activo,
                Inscripcion.estado.notin_(
                    [
                        EstadoInscripcion.cancelada,
                        EstadoInscripcion.rechazada,
                        EstadoInscripcion.retirada,
                    ]
                ),
            )
        )

        if excluir_id:
            query = query.filter(Inscripcion.id != excluir_id)

        return query.first() is not None

    def contar_inscripciones_activas_grupo(self, db: Session, grupo_id: int) -> int:
        """Cuenta inscripciones activas en un grupo."""
        return (
            db.query(Inscripcion)
            .filter(
                and_(
                    Inscripcion.grupo_id == grupo_id,
                    Inscripcion.activo,
                    Inscripcion.estado.in_(
                        [
                            EstadoInscripcion.aprobada,
                            EstadoInscripcion.confirmada,
                            EstadoInscripcion.activa,
                        ]
                    ),
                )
            )
            .count()
        )

    def contar_inscripciones_estudiante_periodo(
        self, db: Session, estudiante_id: int, periodo_id: int
    ) -> int:
        """Cuenta inscripciones de un estudiante en un período."""
        return (
            db.query(Inscripcion)
            .filter(
                and_(
                    Inscripcion.estudiante_id == estudiante_id,
                    Inscripcion.periodo_academico_id == periodo_id,
                    Inscripcion.activo,
                )
            )
            .count()
        )

    def contar_creditos_inscritos_periodo(
        self, db: Session, estudiante_id: int, periodo_id: int
    ) -> int:
        """Suma créditos inscritos de un estudiante en un período."""
        result = (
            db.query(func.sum(Inscripcion.creditos_inscritos))
            .filter(
                and_(
                    Inscripcion.estudiante_id == estudiante_id,
                    Inscripcion.periodo_academico_id == periodo_id,
                    Inscripcion.activo,
                    Inscripcion.estado.in_(
                        [
                            EstadoInscripcion.aprobada,
                            EstadoInscripcion.confirmada,
                            EstadoInscripcion.activa,
                        ]
                    ),
                )
            )
            .scalar()
        )

        return result or 0

    # ==================== Filtros Avanzados ====================

    def get_by_filtros(
        self,
        db: Session,
        *,
        estudiante_id: int | None = None,
        grupo_id: int | None = None,
        periodo_academico_id: int | None = None,
        programa_id: int | None = None,
        estado: EstadoInscripcion | None = None,
        tipo_inscripcion: TipoInscripcion | None = None,
        esta_pagado: bool | None = None,
        esta_aprobada: bool | None = None,
        activo: bool | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Inscripcion], int]:
        """Búsqueda con múltiples filtros.

        Returns:
            Tupla (lista_inscripciones, total_count)
        """
        query = db.query(Inscripcion)

        # Aplicar filtros
        if estudiante_id:
            query = query.filter(Inscripcion.estudiante_id == estudiante_id)
        if grupo_id:
            query = query.filter(Inscripcion.grupo_id == grupo_id)
        if periodo_academico_id:
            query = query.filter(
                Inscripcion.periodo_academico_id == periodo_academico_id
            )
        if programa_id:
            query = query.filter(Inscripcion.programa_id == programa_id)
        if estado:
            query = query.filter(Inscripcion.estado == estado)
        if tipo_inscripcion:
            query = query.filter(Inscripcion.tipo_inscripcion == tipo_inscripcion)
        if esta_pagado is not None:
            query = query.filter(Inscripcion.esta_pagado == esta_pagado)
        if esta_aprobada is not None:
            query = query.filter(Inscripcion.esta_aprobada == esta_aprobada)
        if activo is not None:
            query = query.filter(Inscripcion.activo == activo)

        # Filtro por fechas
        if fecha_desde:
            query = query.filter(Inscripcion.fecha_solicitud >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Inscripcion.fecha_solicitud <= fecha_hasta)

        # Contar total
        total = query.count()

        # Ordenar y paginar
        inscripciones = (
            query.order_by(desc(Inscripcion.fecha_creacion))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return inscripciones, total

    # ==================== Operaciones de Estado ====================

    def aprobar(
        self,
        db: Session,
        inscripcion_id: int,
        aprobado_por_id: int,
        comentarios: str | None = None,
    ) -> Inscripcion | None:
        """Aprueba una inscripción."""
        inscripcion = self.get(db, inscripcion_id)
        if not inscripcion:
            return None

        estado_anterior = inscripcion.estado
        inscripcion.aprobar(aprobado_por_id, comentarios)
        inscripcion.registrar_cambio_estado(
            estado_anterior, inscripcion.estado, aprobado_por_id
        )

        db.add(inscripcion)
        db.commit()
        db.refresh(inscripcion)
        return inscripcion

    def rechazar(
        self,
        db: Session,
        inscripcion_id: int,
        motivo: MotivoRechazo,
        descripcion: str,
        rechazado_por_id: int,
    ) -> Inscripcion | None:
        """Rechaza una inscripción."""
        inscripcion = self.get(db, inscripcion_id)
        if not inscripcion:
            return None

        estado_anterior = inscripcion.estado
        inscripcion.rechazar(motivo, descripcion, rechazado_por_id)
        inscripcion.registrar_cambio_estado(
            estado_anterior, inscripcion.estado, rechazado_por_id
        )

        db.add(inscripcion)
        db.commit()
        db.refresh(inscripcion)
        return inscripcion

    def confirmar(
        self, db: Session, inscripcion_id: int, usuario_id: int
    ) -> Inscripcion | None:
        """Confirma una inscripción."""
        inscripcion = self.get(db, inscripcion_id)
        if not inscripcion:
            return None

        estado_anterior = inscripcion.estado
        inscripcion.confirmar()
        inscripcion.registrar_cambio_estado(
            estado_anterior, inscripcion.estado, usuario_id
        )

        db.add(inscripcion)
        db.commit()
        db.refresh(inscripcion)
        return inscripcion

    def activar(
        self, db: Session, inscripcion_id: int, usuario_id: int
    ) -> Inscripcion | None:
        """Activa una inscripción."""
        inscripcion = self.get(db, inscripcion_id)
        if not inscripcion:
            return None

        estado_anterior = inscripcion.estado
        inscripcion.activar()
        inscripcion.registrar_cambio_estado(
            estado_anterior, inscripcion.estado, usuario_id
        )

        db.add(inscripcion)
        db.commit()
        db.refresh(inscripcion)
        return inscripcion

    def retirar(
        self,
        db: Session,
        inscripcion_id: int,
        motivo: MotivoRetiro,
        descripcion: str,
        es_voluntario: bool,
        usuario_id: int,
    ) -> Inscripcion | None:
        """Retira una inscripción."""
        inscripcion = self.get(db, inscripcion_id)
        if not inscripcion:
            return None

        estado_anterior = inscripcion.estado
        inscripcion.retirar(motivo, descripcion, es_voluntario)
        inscripcion.registrar_cambio_estado(
            estado_anterior, inscripcion.estado, usuario_id
        )

        db.add(inscripcion)
        db.commit()
        db.refresh(inscripcion)
        return inscripcion

    def completar(
        self,
        db: Session,
        inscripcion_id: int,
        calificacion: Decimal | None,
        aprobo: bool | None,
        usuario_id: int,
    ) -> Inscripcion | None:
        """Completa una inscripción con calificación."""
        inscripcion = self.get(db, inscripcion_id)
        if not inscripcion:
            return None

        estado_anterior = inscripcion.estado
        inscripcion.completar(calificacion, aprobo)
        inscripcion.registrar_cambio_estado(
            estado_anterior, inscripcion.estado, usuario_id
        )

        db.add(inscripcion)
        db.commit()
        db.refresh(inscripcion)
        return inscripcion

    # ==================== Estadísticas ====================

    def get_estadisticas_periodo(
        self, db: Session, periodo_academico_id: int
    ) -> dict[str, Any]:
        """Obtiene estadísticas de inscripciones de un período."""
        # Total de inscripciones
        total = (
            db.query(Inscripcion)
            .filter(Inscripcion.periodo_academico_id == periodo_academico_id)
            .count()
        )

        # Por estado
        por_estado = {}
        for estado in EstadoInscripcion:
            count = (
                db.query(Inscripcion)
                .filter(
                    and_(
                        Inscripcion.periodo_academico_id == periodo_academico_id,
                        Inscripcion.estado == estado,
                    )
                )
                .count()
            )
            por_estado[estado.value] = count

        # Pagadas
        total_pagadas = (
            db.query(Inscripcion)
            .filter(
                and_(
                    Inscripcion.periodo_academico_id == periodo_academico_id,
                    Inscripcion.esta_pagado,
                )
            )
            .count()
        )

        # Monto recaudado
        monto_total = (
            db.query(func.sum(Inscripcion.monto_final))
            .filter(
                and_(
                    Inscripcion.periodo_academico_id == periodo_academico_id,
                    Inscripcion.esta_pagado,
                )
            )
            .scalar()
            or 0
        )

        # Promedio de calificación
        promedio_calificacion = (
            db.query(func.avg(Inscripcion.calificacion_final))
            .filter(
                and_(
                    Inscripcion.periodo_academico_id == periodo_academico_id,
                    Inscripcion.calificacion_final.isnot(None),
                )
            )
            .scalar()
        )

        return {
            "total_inscripciones": total,
            "por_estado": por_estado,
            "total_pagadas": total_pagadas,
            "total_pendientes_pago": total - total_pagadas,
            "monto_total_recaudado": float(monto_total),
            "promedio_calificacion": (
                float(promedio_calificacion) if promedio_calificacion else None
            ),
        }

    # ==================== Utilidades Privadas ====================

    def _generar_codigo_inscripcion(
        self, db: Session, estudiante_id: int, grupo_id: int
    ) -> str:
        """Genera código único de inscripción."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        codigo_base = f"INS-{estudiante_id}-{grupo_id}-{timestamp}"

        # Verificar que sea único
        contador = 1
        codigo = codigo_base
        while self.get_by_codigo(db, codigo):
            codigo = f"{codigo_base}-{contador}"
            contador += 1

        return codigo


# Instancia singleton
inscripcion_crud = CRUDInscripcion(Inscripcion)
