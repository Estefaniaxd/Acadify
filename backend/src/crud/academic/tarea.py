from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, asc, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from src.crud.base import CRUDBase
from src.enums.academic.tareas import EstadoEntrega, EstadoTarea
from src.models.academic.tarea import EntregaTarea, Rubrica, Tarea
from src.schemas.academic.tarea_schemas import (
    CalificarEntrega,
    EntregaTareaCreate,
    EntregaTareaUpdate,
    FiltrosEntrega,
    FiltrosTarea,
    RubricaCreate,
    RubricaUpdate,
    TareaCreate,
    TareaUpdate,
)


class CRUDTarea(CRUDBase[Tarea, TareaCreate, TareaUpdate]):

    def crear_tarea(
        self, db: Session, *, tarea_data: TareaCreate, creado_por: str
    ) -> Tarea:
        """Crear una nueva tarea."""
        tarea_dict = tarea_data.dict()
        tarea_dict["creado_por"] = creado_por

        tarea = Tarea(**tarea_dict)
        db.add(tarea)
        db.commit()
        db.refresh(tarea)
        return tarea

    def obtener_tareas_por_grupo(
        self,
        db: Session,
        *,
        grupo_id: str,
        filtros: FiltrosTarea | None = None,
        usuario_id: str | None = None,
    ) -> list[Tarea]:
        """Obtener todas las tareas de un grupo con filtros opcionales."""
        query = db.query(Tarea).filter(Tarea.grupo_id == grupo_id)

        if filtros:
            if filtros.solo_activas:
                query = query.filter(Tarea.activa)

            if filtros.estado:
                query = query.filter(Tarea.estado == filtros.estado)

            if filtros.tipo_tarea:
                query = query.filter(Tarea.tipo_tarea == filtros.tipo_tarea)

            if filtros.prioridad:
                query = query.filter(Tarea.prioridad == filtros.prioridad)

            if filtros.es_grupal is not None:
                query = query.filter(Tarea.es_grupal == filtros.es_grupal)

            if filtros.docente_id:
                query = query.filter(Tarea.docente_id == filtros.docente_id)

            if filtros.fecha_desde:
                query = query.filter(Tarea.fecha_limite >= filtros.fecha_desde)

            if filtros.fecha_hasta:
                query = query.filter(Tarea.fecha_limite <= filtros.fecha_hasta)

            if filtros.busqueda:
                search_term = f"%{filtros.busqueda}%"
                query = query.filter(
                    or_(
                        Tarea.titulo.ilike(search_term),
                        Tarea.descripcion.ilike(search_term),
                        Tarea.categoria.ilike(search_term),
                        Tarea.tags.ilike(search_term),
                    )
                )

            # Ordenamiento
            if filtros.ordenar_por == "fecha_limite":
                order_field = Tarea.fecha_limite
            elif filtros.ordenar_por == "fecha_creacion":
                order_field = Tarea.fecha_creacion
            elif filtros.ordenar_por == "titulo":
                order_field = Tarea.titulo
            elif filtros.ordenar_por == "prioridad":
                # Ordenar por prioridad: urgente -> alta -> media -> baja
                order_field = case(
                    (Tarea.prioridad == "urgente", 1),
                    (Tarea.prioridad == "alta", 2),
                    (Tarea.prioridad == "media", 3),
                    (Tarea.prioridad == "baja", 4),
                    else_=5,
                )
            else:
                order_field = Tarea.fecha_creacion

            if filtros.orden_desc:
                query = query.order_by(desc(order_field))
            else:
                query = query.order_by(asc(order_field))

            # Paginación
            offset = (filtros.pagina - 1) * filtros.tamaño_pagina
            query = query.offset(offset).limit(filtros.tamaño_pagina)

        return query.all()

    def obtener_tareas_por_docente(
        self, db: Session, *, docente_id: str, filtros: FiltrosTarea | None = None
    ) -> list[Tarea]:
        """Obtener todas las tareas creadas por un docente."""
        query = db.query(Tarea).filter(Tarea.docente_id == docente_id)

        if filtros and filtros.solo_activas:
            query = query.filter(Tarea.activa)

        return query.all()

    def obtener_tarea_detallada(self, db: Session, tarea_id: str) -> Tarea | None:
        """Obtener una tarea con toda su información relacionada."""
        return (
            db.query(Tarea)
            .options(
                joinedload(Tarea.docente),
                joinedload(Tarea.grupo),
                joinedload(Tarea.rubrica_obj),
                joinedload(Tarea.entregas),
            )
            .filter(Tarea.tarea_id == tarea_id)
            .first()
        )

    def actualizar_estado_tarea(
        self,
        db: Session,
        *,
        tarea_id: str,
        nuevo_estado: EstadoTarea,
        actualizado_por: str,
    ) -> Tarea | None:
        """Actualizar solo el estado de una tarea."""
        tarea = self.get(db, id=tarea_id)
        if tarea:
            tarea.estado = nuevo_estado
            tarea.actualizado_por = actualizado_por
            tarea.fecha_actualizacion = datetime.utcnow()
            db.commit()
            db.refresh(tarea)
        return tarea

    def marcar_tareas_vencidas(self, db: Session) -> int:
        """Marcar automáticamente las tareas vencidas."""
        ahora = datetime.utcnow()
        tareas_vencidas = (
            db.query(Tarea)
            .filter(
                and_(
                    Tarea.fecha_limite < ahora,
                    Tarea.estado.in_([EstadoTarea.ASIGNADA, EstadoTarea.EN_PROGRESO]),
                    Tarea.activa,
                )
            )
            .update({"estado": EstadoTarea.VENCIDA, "fecha_actualizacion": ahora})
        )

        db.commit()
        return tareas_vencidas

    def obtener_estadisticas_tarea(self, db: Session, tarea_id: str) -> dict[str, Any]:
        """Obtener estadísticas detalladas de una tarea."""
        tarea = self.get(db, id=tarea_id)
        if not tarea:
            return {}

        entregas = (
            db.query(EntregaTarea).filter(EntregaTarea.tarea_id == tarea_id).all()
        )

        total_entregas = len(
            [e for e in entregas if e.estado != EstadoEntrega.BORRADOR]
        )
        entregas_calificadas = len([e for e in entregas if e.calificacion is not None])
        entregas_tardias = len([e for e in entregas if e.es_entrega_tardia])

        calificaciones = [
            e.calificacion for e in entregas if e.calificacion is not None
        ]
        promedio_calificaciones = (
            sum(calificaciones) / len(calificaciones) if calificaciones else 0
        )

        return {
            "tarea_id": tarea_id,
            "titulo": tarea.titulo,
            "total_entregas": total_entregas,
            "entregas_calificadas": entregas_calificadas,
            "entregas_pendientes": total_entregas - entregas_calificadas,
            "entregas_tardias": entregas_tardias,
            "promedio_calificaciones": promedio_calificaciones,
            "porcentaje_completitud": (
                (entregas_calificadas / total_entregas * 100)
                if total_entregas > 0
                else 0
            ),
            "esta_vencida": tarea.esta_vencida,
        }


class CRUDEntregaTarea(CRUDBase[EntregaTarea, EntregaTareaCreate, EntregaTareaUpdate]):

    def crear_entrega(
        self, db: Session, *, entrega_data: EntregaTareaCreate
    ) -> EntregaTarea:
        """Crear una nueva entrega de tarea."""
        # Verificar si ya existe una entrega para esta tarea y estudiante
        entrega_existente = (
            db.query(EntregaTarea)
            .filter(
                and_(
                    EntregaTarea.tarea_id == entrega_data.tarea_id,
                    EntregaTarea.estudiante_id == entrega_data.estudiante_id,
                )
            )
            .order_by(EntregaTarea.fecha_creacion.desc())  # Get the latest submission
            .first()
        )

        if entrega_existente:
            # Si existe, incrementar el número de intento
            numero_intento = entrega_existente.numero_intento + 1
        else:
            numero_intento = 1

        # Verificar si la entrega es tardía
        tarea = db.query(Tarea).filter(Tarea.tarea_id == entrega_data.tarea_id).first()
        es_tardia = datetime.utcnow() > tarea.fecha_limite if tarea else False

        entrega_dict = entrega_data.dict()
        entrega_dict.update(
            {
                "numero_intento": numero_intento,
                "es_entrega_tardia": es_tardia,
                "fecha_limite_original": tarea.fecha_limite if tarea else None,
            }
        )
        
        # ✨ PRESERVE archivo_url and archivos_adicionales from previous submission if not provided
        # This ensures students don't lose their uploaded files on re-submission
        if entrega_existente:
            if not entrega_dict.get("archivo_url") and entrega_existente.archivo_url:
                entrega_dict["archivo_url"] = entrega_existente.archivo_url
                
            if not entrega_dict.get("archivos_adicionales") and entrega_existente.archivos_adicionales:
                entrega_dict["archivos_adicionales"] = entrega_existente.archivos_adicionales

        entrega = EntregaTarea(**entrega_dict)
        db.add(entrega)
        db.commit()
        db.refresh(entrega)

        return entrega

    def entregar_tarea(self, db: Session, *, entrega_id: str) -> EntregaTarea | None:
        """Marcar una entrega como entregada (cambiar de borrador a entregada)."""
        entrega = self.get(db, id=entrega_id)
        if entrega and entrega.estado == EstadoEntrega.BORRADOR:
            entrega.estado = EstadoEntrega.ENTREGADA
            entrega.fecha_entrega = datetime.utcnow()
            entrega.es_final = True

            db.commit()
            db.refresh(entrega)

        return entrega

    def calificar_entrega(
        self,
        db: Session,
        *,
        entrega_id: str,
        calificacion_data: CalificarEntrega,
        calificado_por: str,
    ) -> EntregaTarea | None:
        """Calificar una entrega."""
        entrega = self.get(db, id=entrega_id)
        if not entrega:
            return None

        # Validar que la calificación no exceda el máximo de la tarea
        tarea = db.query(Tarea).filter(Tarea.tarea_id == entrega.tarea_id).first()
        if tarea and calificacion_data.calificacion > tarea.puntuacion_maxima:
            msg = f"La calificación no puede exceder {tarea.puntuacion_maxima} puntos"
            raise ValueError(msg)

        entrega.calificacion = calificacion_data.calificacion
        entrega.calificacion_letras = calificacion_data.calificacion_letras
        entrega.comentarios_docente = calificacion_data.comentarios_docente
        entrega.rubrica_calificacion = calificacion_data.rubrica_calificacion
        entrega.requiere_revision = calificacion_data.requiere_revision
        entrega.estado = (
            EstadoEntrega.DEVUELTA
            if calificacion_data.requiere_revision
            else EstadoEntrega.CALIFICADA
        )
        entrega.calificado_por = calificado_por
        entrega.fecha_calificacion = datetime.utcnow()

        db.commit()
        db.refresh(entrega)

        return entrega

    def calificar_entrega_con_puntos(
        self,
        db: Session,
        *,
        entrega_id: str,
        calificacion_data: CalificarEntrega,
        calificado_por: str,
        puntos_service=None,
    ) -> dict[str, Any]:
        """Calificar una entrega e integrar puntos de gamificación.

        Este método mejorado:
        1. Valida la calificación contra puntuación máxima
        2. Actualiza campos de calificación en BD
        3. Calcula puntos usando fórmula de gamificación
        4. Almacena puntos en la BD (puntos_otorgados field)
        5. Registra los datos para procesamiento asíncrono de puntos

        Args:
            db: Sesión de base de datos síncrona
            entrega_id: ID de la entrega
            calificacion_data: Datos de calificación
            calificado_por: UUID del docente calificador
            puntos_service: Instancia de PuntosService (opcional, para logging)

        Returns:
            Dict con:
            {
                "entrega": EntregaTarea (actualizada),
                "puntos_otorgados": int (calculados pero no otorgados aún),
                "formula_aplicada": str (para auditoría)
            }

        Note:
            Los puntos se almacenan en entregas_tareas.puntos_otorgados
            pero NO se actualizan las tablas UsuarioPuntos y HistorialPuntos
            aún. Eso debe hacerse en un background job o celery task.

        Raises:
            ValueError: Si calificación excede puntuación máxima
            Exception: Si entrega no existe
        """
        import logging

        logger = logging.getLogger(__name__)

        # 1. Obtener entrega y tarea
        entrega = self.get(db, id=entrega_id)
        if not entrega:
            raise ValueError(f"Entrega no encontrada: {entrega_id}")

        tarea = db.query(Tarea).filter(Tarea.tarea_id == entrega.tarea_id).first()

        # 2. Validar calificación
        if tarea and calificacion_data.calificacion > tarea.puntuacion_maxima:
            msg = f"La calificación no puede exceder {tarea.puntuacion_maxima} puntos"
            raise ValueError(msg)

        # 3. Actualizar campos de calificación
        entrega.calificacion = calificacion_data.calificacion
        entrega.calificacion_letras = calificacion_data.calificacion_letras
        entrega.comentarios_docente = calificacion_data.comentarios_docente
        entrega.rubrica_calificacion = calificacion_data.rubrica_calificacion
        entrega.requiere_revision = calificacion_data.requiere_revision
        entrega.estado = (
            EstadoEntrega.DEVUELTA
            if calificacion_data.requiere_revision
            else EstadoEntrega.CALIFICADA
        )
        entrega.calificado_por = calificado_por
        entrega.fecha_calificacion = datetime.utcnow()

        # 4. Calcular puntos - FORMULA SINCRÓNICA
        puntos_resultado = {
            "puntos_otorgados": 0,
            "formula_aplicada": "Sin cálculo (tarea sin configuración de puntos)",
        }

        if tarea and tarea.puntos_base is not None:
            try:
                # FÓRMULA COMPLETA (sincrónica - copiada de PuntosService)
                # =========================================================

                # Puntos base de la tarea
                puntos_base = tarea.puntos_base if tarea.puntos_base else 50

                # Bonificación por excelencia (calificación >= 4.5)
                puntos_bonificacion = 0
                if (
                    calificacion_data.calificacion >= 4.5
                    and tarea.puntos_bonificacion
                ):
                    puntos_bonificacion = tarea.puntos_bonificacion

                # Penalización por entrega tardía (-30%)
                penalizacion_tardia = 0
                if tarea.fecha_limite and entrega.fecha_entrega > tarea.fecha_limite:
                    penalizacion_tardia = int(puntos_base * 0.30)

                # Penalización por intentos adicionales (-10% por intento extra, max 2)
                entregas_previas = (
                    db.query(EntregaTarea)
                    .filter(
                        and_(
                            EntregaTarea.tarea_id == tarea.tarea_id,
                            EntregaTarea.estudiante_id == entrega.estudiante_id,
                            EntregaTarea.entrega_id != entrega_id,
                        )
                    )
                    .count()
                )

                penalizacion_intentos = 0
                if entregas_previas > 0:
                    intentos_extra = min(entregas_previas, 2)  # Máximo 2 intentos extra
                    penalizacion_intentos = int(puntos_base * 0.10 * intentos_extra)

                # Calcular total
                puntos_totales = (
                    puntos_base
                    + puntos_bonificacion
                    - penalizacion_tardia
                    - penalizacion_intentos
                )

                # Asegurar que no sean negativos
                puntos_totales = max(0, puntos_totales)

                # Desglose para auditoría
                desglose_partes = [f"{puntos_base} (base)"]
                if puntos_bonificacion > 0:
                    desglose_partes.append(f"+ {puntos_bonificacion} (bonus)")
                if penalizacion_tardia > 0:
                    desglose_partes.append(f"- {penalizacion_tardia} (tardía)")
                if penalizacion_intentos > 0:
                    desglose_partes.append(
                        f"- {penalizacion_intentos} ({entregas_previas} intento(s))"
                    )

                desglose = " ".join(desglose_partes)

                # Guardar en la entrega
                entrega.puntos_otorgados = puntos_totales

                puntos_resultado = {
                    "puntos_otorgados": puntos_totales,
                    "formula_aplicada": desglose,
                }

                logger.info(
                    f"Puntos calculados: entrega_id={entrega_id}, "
                    f"estudiante_id={entrega.estudiante_id}, "
                    f"puntos={puntos_totales}, fórmula: {desglose}"
                )

            except Exception as e:
                logger.exception(
                    f"Error al calcular puntos en calificación: {e!s}. "
                    f"La entrega será calificada pero sin puntos."
                )
                entrega.puntos_otorgados = 0

        # 5. Guardar cambios
        db.add(entrega)
        db.commit()
        db.refresh(entrega)

        logger.info(
            f"Entrega calificada: entrega_id={entrega_id}, "
            f"calificacion={calificacion_data.calificacion}, "
            f"puntos={entrega.puntos_otorgados}"
        )

        return {
            "entrega": entrega,
            **puntos_resultado,
        }

    def obtener_entregas_por_tarea(
        self, db: Session, *, tarea_id: str, filtros: FiltrosEntrega | None = None
    ) -> list[EntregaTarea]:
        """Obtener todas las entregas de una tarea + estudiantes sin entregas."""
        
        # 1. Obtener la tarea para saber el grupo
        tarea = db.query(Tarea).filter(Tarea.tarea_id == tarea_id).first()
        if not tarea:
            return []
        
        # 2. Obtener TODOS los estudiantes del grupo
        from src.models.academic.estudiante_grupo import EstudianteGrupo
        from src.models.users.usuario import Usuario
        from src.models.users.estudiante import Estudiante
        
        estudiantes = (
            db.query(Usuario)
            .join(Estudiante, Usuario.usuario_id == Estudiante.estudiante_id)
            .join(EstudianteGrupo, Estudiante.estudiante_id == EstudianteGrupo.estudiante_id)
            .filter(EstudianteGrupo.grupo_id == tarea.grupo_id)
            .all()
        )
        
        # 3. Query de entregas existentes
        query = (
            db.query(EntregaTarea)
            .options(joinedload(EntregaTarea.estudiante))
            .filter(EntregaTarea.tarea_id == tarea_id)
        )

        # Aplicar filtros si existen
        if filtros:
            if filtros.estado:
                query = query.filter(EntregaTarea.estado == filtros.estado)
            
            if filtros.estudiante_id:
                query = query.filter(EntregaTarea.estudiante_id == filtros.estudiante_id)

        todas_entregas = query.all()

        # 4. Filtrar solo la última entrega por estudiante
        latest_entregas_map = {}
        for entrega in todas_entregas:
            est_id = str(entrega.estudiante_id)
            if est_id not in latest_entregas_map:
                latest_entregas_map[est_id] = entrega
            else:
                existing = latest_entregas_map[est_id]
                if (entrega.numero_intento or 0) > (existing.numero_intento or 0):
                    latest_entregas_map[est_id] = entrega
                elif (entrega.numero_intento or 0) == (existing.numero_intento or 0):
                    if entrega.fecha_creacion and existing.fecha_creacion and entrega.fecha_creacion > existing.fecha_creacion:
                        latest_entregas_map[est_id] = entrega

        # 5. Combinar estudiantes con entregas
        resultado = []
        for estudiante in estudiantes:
            est_id = str(estudiante.usuario_id)
            if est_id in latest_entregas_map:
                resultado.append(latest_entregas_map[est_id])
            else:
                # Crear dummy para estudiante sin entrega
                dummy = EntregaTarea(
                    entrega_id=f"dummy_{est_id}",
                    tarea_id=tarea_id,
                    estudiante_id=est_id,
                    estudiante=estudiante,
                    estado="asignada",
                    fecha_entrega=None,
                    fecha_creacion=datetime.now(),  # Fecha válida requerida por schema
                    calificacion=None,
                    calificado_por=None,  # Evitar UUID serialization error
                    numero_intento=0
                )
                resultado.append(dummy)
        
        # 6. Si hay filtro de estado, excluir dummies que no cumplan
        if filtros and filtros.estado:
            resultado = [e for e in resultado if e.estado == filtros.estado]

        return resultado

    def obtener_entregas_por_estudiante(
        self, db: Session, *, estudiante_id: str, grupo_id: str | None = None
    ) -> list[EntregaTarea]:
        """Obtener todas las entregas de un estudiante."""
        query = db.query(EntregaTarea).filter(
            EntregaTarea.estudiante_id == estudiante_id
        )

        if grupo_id:
            query = query.join(Tarea).filter(Tarea.grupo_id == grupo_id)

        return query.all()

    def get_by_tarea_and_estudiante(
        self, db: Session, *, tarea_id: str, estudiante_id: str
    ) -> EntregaTarea | None:
        """Obtener la entrega de un estudiante para una tarea específica."""
        return (
            db.query(EntregaTarea)
            .filter(
                and_(
                    EntregaTarea.tarea_id == tarea_id,
                    EntregaTarea.estudiante_id == estudiante_id,
                )
            )
            .order_by(desc(EntregaTarea.fecha_creacion))
            .first()
        )

    def obtener_entrega_detallada(
        self, db: Session, entrega_id: str
    ) -> EntregaTarea | None:
        """Obtener una entrega con toda su información relacionada."""
        return (
            db.query(EntregaTarea)
            .options(
                joinedload(EntregaTarea.tarea),
                joinedload(EntregaTarea.estudiante),
                joinedload(EntregaTarea.calificador),
            )
            .filter(EntregaTarea.entrega_id == entrega_id)
            .first()
        )


class CRUDRubrica(CRUDBase[Rubrica, RubricaCreate, RubricaUpdate]):

    def obtener_rubricas_por_docente(
        self, db: Session, *, docente_id: str, incluir_publicas: bool = True
    ) -> list[Rubrica]:
        """Obtener todas las rúbricas de un docente."""
        query = db.query(Rubrica)

        if incluir_publicas:
            query = query.filter(
                or_(Rubrica.creado_por == docente_id, Rubrica.es_publica)
            )
        else:
            query = query.filter(Rubrica.creado_por == docente_id)

        return query.filter(Rubrica.activa).all()

    def obtener_rubricas_publicas(self, db: Session) -> list[Rubrica]:
        """Obtener todas las rúbricas públicas."""
        return db.query(Rubrica).filter(and_(Rubrica.es_publica, Rubrica.activa)).all()

    def obtener_plantillas_rubrica(self, db: Session) -> list[Rubrica]:
        """Obtener todas las plantillas de rúbricas."""
        return (
            db.query(Rubrica).filter(and_(Rubrica.es_plantilla, Rubrica.activa)).all()
        )

    def duplicar_rubrica(
        self, db: Session, *, rubrica_id: str, nuevo_nombre: str, creado_por: str
    ) -> Rubrica | None:
        """Duplicar una rúbrica existente."""
        rubrica_original = self.get(db, id=rubrica_id)
        if not rubrica_original:
            return None

        nueva_rubrica = Rubrica(
            nombre=nuevo_nombre,
            descripcion=rubrica_original.descripcion,
            criterios=rubrica_original.criterios,
            puntuacion_total=rubrica_original.puntuacion_total,
            es_publica=False,  # Por defecto, las copias son privadas
            es_plantilla=False,
            creado_por=creado_por,
        )

        db.add(nueva_rubrica)
        db.commit()
        db.refresh(nueva_rubrica)

        return nueva_rubrica


# Instancias de los CRUDs
crud_tarea = CRUDTarea(Tarea)
crud_entrega_tarea = CRUDEntregaTarea(EntregaTarea, id_field="entrega_id")
crud_rubrica = CRUDRubrica(Rubrica)
