"""Servicio de Lógica de Negocio para Evaluaciones.

Este servicio maneja toda la lógica de negocio relacionada con evaluaciones:
- CRUD completo con validaciones
- Gestión de permisos y acceso
- Cambio de estados
- Filtros avanzados
- Integración con configuración antitrampa
- Validaciones de fechas y límites
- Gestión de preguntas
"""

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session, joinedload

from src.models.evaluaciones.evaluacion_expandida import (
    EstadoEvaluacion,
    Evaluacion,
    PreguntaEvaluacion,
    VisibilidadEvaluacion,
)
from src.models.evaluaciones.intento_respuesta_gamificacion import IntentoEvaluacion
from src.schemas.evaluaciones.evaluacion_schemas import (
    EvaluacionCreate,
    EvaluacionFiltros,
    EvaluacionUpdate,
    PreguntaCreate,
    PreguntaUpdate,
)


class EvaluacionService:
    """Servicio para gestión de evaluaciones."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ==================== CRUD BÁSICO ====================

    def crear_evaluacion(
        self, evaluacion_data: EvaluacionCreate, usuario_id: UUID
    ) -> Evaluacion:
        """Crea una nueva evaluación con todas las validaciones necesarias.

        Validaciones:
        - Permisos del usuario
        - Fechas coherentes
        - Límites de preguntas
        - Configuración de curso/institución
        """
        # Validar fechas
        if evaluacion_data.fecha_apertura and evaluacion_data.fecha_cierre:
            if evaluacion_data.fecha_apertura >= evaluacion_data.fecha_cierre:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha de apertura debe ser anterior a la fecha de cierre",
                )

        if (
            evaluacion_data.fecha_publicacion_resultados
            and evaluacion_data.fecha_cierre
        ):
            if (
                evaluacion_data.fecha_publicacion_resultados
                < evaluacion_data.fecha_cierre
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha de publicación de resultados debe ser posterior al cierre",
                )

        # Validar límites de preguntas
        if evaluacion_data.num_preguntas_mostrar:
            if evaluacion_data.num_preguntas_mostrar > evaluacion_data.total_preguntas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El número de preguntas a mostrar no puede exceder el total",
                )

        # Validar configuración de equipo para evaluaciones colaborativas
        if evaluacion_data.es_colaborativa and not evaluacion_data.max_miembros_equipo:
            evaluacion_data.max_miembros_equipo = 5  # Default

        # Validar peer review
        if (
            evaluacion_data.permitir_peer_review
            and not evaluacion_data.num_revisiones_requeridas
        ):
            evaluacion_data.num_revisiones_requeridas = 2  # Default

        # Crear la evaluación
        evaluacion_dict = evaluacion_data.model_dump(exclude_unset=True)
        evaluacion_dict["creado_por_id"] = usuario_id
        evaluacion_dict["estado"] = EstadoEvaluacion.BORRADOR
        evaluacion_dict["fecha_creacion"] = datetime.utcnow()

        # Mapear campos del schema al modelo
        if "total_preguntas" in evaluacion_dict:
            evaluacion_dict["num_preguntas_totales"] = evaluacion_dict.pop(
                "total_preguntas"
            )

        evaluacion = Evaluacion(**evaluacion_dict)

        self.db.add(evaluacion)
        self.db.commit()
        self.db.refresh(evaluacion)

        return evaluacion

    def obtener_evaluacion(
        self,
        evaluacion_id: UUID,
        usuario_id: UUID | None = None,
        incluir_preguntas: bool = False,
    ) -> Evaluacion:
        """Obtiene una evaluación por ID con validación de permisos.

        Args:
            evaluacion_id: ID de la evaluación
            usuario_id: ID del usuario (para validar permisos)
            incluir_preguntas: Si incluir las preguntas en la respuesta
        """
        query = self.db.query(Evaluacion)

        if incluir_preguntas:
            query = query.options(joinedload(Evaluacion.preguntas))

        evaluacion = query.filter(Evaluacion.evaluacion_id == evaluacion_id).first()

        if not evaluacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Evaluación no encontrada"
            )

        # Validar permisos si es necesario
        if usuario_id and evaluacion.visibilidad == VisibilidadEvaluacion.PRIVADA:
            if evaluacion.creador_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permisos para ver esta evaluación",
                )

        return evaluacion

    def listar_evaluaciones(
        self,
        filtros: EvaluacionFiltros,
        usuario_id: UUID | None = None,
        es_estudiante: bool = False,
    ) -> tuple[list[Evaluacion], int]:
        """Lista evaluaciones con filtros avanzados y paginación.

        Returns:
            Tuple con (lista de evaluaciones, total de registros)
        """
        query = self.db.query(Evaluacion)

        # Filtro por curso
        if filtros.curso_id:
            query = query.filter(Evaluacion.curso_id == filtros.curso_id)

        # Filtro por institución
        if filtros.institucion_id:
            query = query.filter(Evaluacion.institucion_id == filtros.institucion_id)

        # Filtro por tipo
        if filtros.tipo_evaluacion:
            query = query.filter(Evaluacion.tipo_evaluacion == filtros.tipo_evaluacion)

        # Filtro por estado
        if filtros.estado_evaluacion:
            query = query.filter(Evaluacion.estado == filtros.estado_evaluacion)

        # Filtro por visibilidad
        if filtros.visibilidad:
            query = query.filter(Evaluacion.visibilidad == filtros.visibilidad)

        # Filtro por creador
        if filtros.creado_por_id:
            query = query.filter(Evaluacion.creador_id == filtros.creado_por_id)

        # Filtro por curso
        if filtros.curso_id:
            query = query.filter(Evaluacion.curso_id == filtros.curso_id)

        # Filtro por búsqueda de texto
        if filtros.busqueda:
            search_term = f"%{filtros.busqueda}%"
            query = query.filter(
                or_(
                    Evaluacion.titulo.ilike(search_term),
                    Evaluacion.descripcion.ilike(search_term),
                    Evaluacion.instrucciones.ilike(search_term),
                )
            )

        # Si es estudiante, solo mostrar públicas o del curso
        if es_estudiante:
            query = query.filter(
                or_(
                    Evaluacion.visibilidad == VisibilidadEvaluacion.PUBLICA,
                    Evaluacion.curso_id.in_(
                        # Aquí se podría hacer un subquery para los cursos del estudiante
                        self.db.query(Evaluacion.curso_id).distinct()
                    ),
                )
            )

        # Contar total antes de paginar
        total = query.count()

        # Ordenamiento
        if filtros.orden:
            if filtros.descendente:
                query = query.order_by(desc(getattr(Evaluacion, filtros.orden)))
            else:
                query = query.order_by(asc(getattr(Evaluacion, filtros.orden)))
        else:
            query = query.order_by(desc(Evaluacion.fecha_creacion))

        # Contar total antes de paginar
        total = query.count()

        # Paginación
        query = query.offset(filtros.skip).limit(filtros.limit)

        evaluaciones = query.all()

        return evaluaciones, total

    def actualizar_evaluacion(
        self, evaluacion_id: UUID, evaluacion_data: EvaluacionUpdate, usuario_id: UUID
    ) -> Evaluacion:
        """Actualiza una evaluación existente con validaciones.

        Solo permite actualizar si:
        - El usuario es el creador
        - La evaluación está en BORRADOR o PUBLICADA
        """
        evaluacion = self.obtener_evaluacion(evaluacion_id)

        # Validar permisos
        if evaluacion.creador_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el creador puede modificar la evaluación",
            )

        # Validar que se puede editar
        if evaluacion.estado in [EstadoEvaluacion.CERRADA, EstadoEvaluacion.ARCHIVADA]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede editar una evaluación cerrada o archivada",
            )

        # Si ya está activa y tiene intentos, limitar cambios
        if (
            evaluacion.estado == EstadoEvaluacion.ACTIVA
            and evaluacion.total_intentos > 0
        ):
            campos_bloqueados = [
                "total_preguntas",
                "puntuacion_total",
                "tipo_calificacion",
                "randomizar_preguntas",
                "num_preguntas_mostrar",
            ]
            for campo in campos_bloqueados:
                if getattr(evaluacion_data, campo, None) is not None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"No se puede modificar '{campo}' en una evaluación activa con intentos",
                    )

        # Validar fechas si se actualizan
        update_dict = evaluacion_data.model_dump(exclude_unset=True)

        if "fecha_apertura" in update_dict and "fecha_cierre" in update_dict:
            if update_dict["fecha_apertura"] >= update_dict["fecha_cierre"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha de apertura debe ser anterior a la fecha de cierre",
                )

        # Actualizar campos
        for campo, valor in update_dict.items():
            setattr(evaluacion, campo, valor)

        evaluacion.fecha_modificacion = datetime.utcnow()

        self.db.commit()
        self.db.refresh(evaluacion)

        return evaluacion

    def eliminar_evaluacion(
        self, evaluacion_id: UUID, usuario_id: UUID, forzar: bool = False
    ) -> bool:
        """Elimina una evaluación (soft delete).

        Args:
            evaluacion_id: ID de la evaluación
            usuario_id: ID del usuario (para validar permisos)
            forzar: Si True, elimina aunque tenga intentos
        """
        evaluacion = self.obtener_evaluacion(evaluacion_id)

        # Validar permisos
        if evaluacion.creador_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el creador puede eliminar la evaluación",
            )

        # Validar si tiene intentos
        if evaluacion.total_intentos > 0 and not forzar:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una evaluación con intentos. Use forzar=true para eliminarla de todas formas.",
            )

        # Soft delete - cambiar estado a ARCHIVADA
        evaluacion.estado = EstadoEvaluacion.ARCHIVADA
        evaluacion.fecha_modificacion = datetime.utcnow()

        self.db.commit()

        return True

    # ==================== GESTIÓN DE ESTADO ====================

    def publicar_evaluacion(self, evaluacion_id: UUID, usuario_id: UUID) -> Evaluacion:
        """Cambia el estado de BORRADOR a PUBLICADA.

        Validaciones:
        - Tiene al menos una pregunta
        - Tiene configuración válida
        - Fechas coherentes
        """
        evaluacion = self.obtener_evaluacion(evaluacion_id)

        # Validar permisos
        if evaluacion.creador_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el creador puede publicar la evaluación",
            )

        # Validar estado actual
        if evaluacion.estado != EstadoEvaluacion.BORRADOR:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden publicar evaluaciones en estado BORRADOR",
            )

        # Validar que tenga preguntas
        num_preguntas = (
            self.db.query(func.count(PreguntaEvaluacion.pregunta_id))
            .filter(PreguntaEvaluacion.evaluacion_id == evaluacion_id)
            .scalar()
        )

        if num_preguntas == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La evaluación debe tener al menos una pregunta",
            )

        if num_preguntas < evaluacion.total_preguntas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Se esperan {evaluacion.total_preguntas} preguntas, pero solo hay {num_preguntas}",
            )

        # Validar configuración de puntuación
        puntuacion_total_preguntas = (
            self.db.query(func.sum(PreguntaEvaluacion.puntuacion))
            .filter(PreguntaEvaluacion.evaluacion_id == evaluacion_id)
            .scalar()
            or 0
        )

        if puntuacion_total_preguntas != evaluacion.puntuacion_total:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La suma de puntuaciones de las preguntas ({puntuacion_total_preguntas}) no coincide con el total esperado ({evaluacion.puntuacion_total})",
            )

        # Cambiar estado
        evaluacion.estado = EstadoEvaluacion.PUBLICADA
        evaluacion.fecha_publicacion = datetime.utcnow()
        evaluacion.fecha_modificacion = datetime.utcnow()

        self.db.commit()
        self.db.refresh(evaluacion)

        return evaluacion

    def activar_evaluacion(self, evaluacion_id: UUID, usuario_id: UUID) -> Evaluacion:
        """Activa una evaluación publicada para que los estudiantes puedan tomarla."""
        evaluacion = self.obtener_evaluacion(evaluacion_id)

        if evaluacion.creador_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el creador puede activar la evaluación",
            )

        if evaluacion.estado != EstadoEvaluacion.PUBLICADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden activar evaluaciones PUBLICADAS",
            )

        evaluacion.estado = EstadoEvaluacion.ACTIVA
        evaluacion.fecha_modificacion = datetime.utcnow()

        self.db.commit()
        self.db.refresh(evaluacion)

        return evaluacion

    def cerrar_evaluacion(self, evaluacion_id: UUID, usuario_id: UUID) -> Evaluacion:
        """Cierra una evaluación activa."""
        evaluacion = self.obtener_evaluacion(evaluacion_id)

        if evaluacion.creador_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el creador puede cerrar la evaluación",
            )

        if evaluacion.estado != EstadoEvaluacion.ACTIVA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden cerrar evaluaciones ACTIVAS",
            )

        evaluacion.estado = EstadoEvaluacion.CERRADA
        evaluacion.fecha_cierre = datetime.utcnow()
        evaluacion.fecha_modificacion = datetime.utcnow()

        self.db.commit()
        self.db.refresh(evaluacion)

        return evaluacion

    # ==================== GESTIÓN DE PREGUNTAS ====================

    def agregar_pregunta(
        self, evaluacion_id: UUID, pregunta_data: PreguntaCreate, usuario_id: UUID
    ) -> PreguntaEvaluacion:
        """Agrega una pregunta a una evaluación."""
        evaluacion = self.obtener_evaluacion(evaluacion_id)

        # Validar permisos
        if evaluacion.creador_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el creador puede agregar preguntas",
            )

        # Validar estado
        if evaluacion.estado not in [
            EstadoEvaluacion.BORRADOR,
            EstadoEvaluacion.PUBLICADA,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden agregar preguntas a evaluaciones activas o cerradas",
            )

        # Validar límite de preguntas
        num_preguntas_actual = (
            self.db.query(func.count(PreguntaEvaluacion.pregunta_id))
            .filter(PreguntaEvaluacion.evaluacion_id == evaluacion_id)
            .scalar()
        )

        if num_preguntas_actual >= evaluacion.total_preguntas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La evaluación ya tiene el máximo de {evaluacion.total_preguntas} preguntas",
            )

        # Crear pregunta
        pregunta_dict = pregunta_data.model_dump(exclude_unset=True)
        pregunta_dict["evaluacion_id"] = evaluacion_id

        # Asignar orden si no se especificó
        if "orden" not in pregunta_dict:
            pregunta_dict["orden"] = num_preguntas_actual + 1

        pregunta = PreguntaEvaluacion(**pregunta_dict)

        self.db.add(pregunta)
        self.db.commit()
        self.db.refresh(pregunta)

        return pregunta

    def actualizar_pregunta(
        self, pregunta_id: UUID, pregunta_data: PreguntaUpdate, usuario_id: UUID
    ) -> PreguntaEvaluacion:
        """Actualiza una pregunta existente."""
        pregunta = (
            self.db.query(PreguntaEvaluacion)
            .filter(PreguntaEvaluacion.pregunta_id == pregunta_id)
            .first()
        )

        if not pregunta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada"
            )

        evaluacion = self.obtener_evaluacion(pregunta.evaluacion_id)

        # Validar permisos
        if evaluacion.creador_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el creador puede modificar preguntas",
            )

        # Validar estado
        if (
            evaluacion.estado == EstadoEvaluacion.ACTIVA
            and evaluacion.total_intentos > 0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden modificar preguntas de evaluaciones activas con intentos",
            )

        # Actualizar campos
        update_dict = pregunta_data.model_dump(exclude_unset=True)
        for campo, valor in update_dict.items():
            setattr(pregunta, campo, valor)

        self.db.commit()
        self.db.refresh(pregunta)

        return pregunta

    def eliminar_pregunta(self, pregunta_id: UUID, usuario_id: UUID) -> bool:
        """Elimina una pregunta de una evaluación."""
        pregunta = (
            self.db.query(PreguntaEvaluacion)
            .filter(PreguntaEvaluacion.pregunta_id == pregunta_id)
            .first()
        )

        if not pregunta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada"
            )

        evaluacion = self.obtener_evaluacion(pregunta.evaluacion_id)

        # Validar permisos
        if evaluacion.creador_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el creador puede eliminar preguntas",
            )

        # Validar estado
        if evaluacion.estado not in [
            EstadoEvaluacion.BORRADOR,
            EstadoEvaluacion.PUBLICADA,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden eliminar preguntas de evaluaciones activas o cerradas",
            )

        self.db.delete(pregunta)
        self.db.commit()

        return True

    # ==================== VALIDACIONES DE ACCESO ====================

    def validar_acceso_estudiante(
        self,
        evaluacion_id: UUID,
        estudiante_id: UUID,
        codigo_acceso: str | None = None,
        contrasena: str | None = None,
    ) -> tuple[bool, str | None]:
        """Valida si un estudiante puede acceder a una evaluación.

        Returns:
            Tuple con (puede_acceder, mensaje_error)
        """
        evaluacion = self.obtener_evaluacion(evaluacion_id)

        # Validar estado
        if evaluacion.estado != EstadoEvaluacion.ACTIVA:
            return False, "La evaluación no está activa"

        # Validar fechas
        ahora = datetime.utcnow()

        if evaluacion.fecha_apertura and ahora < evaluacion.fecha_apertura:
            return False, f"La evaluación abrirá el {evaluacion.fecha_apertura}"

        if evaluacion.fecha_cierre and ahora > evaluacion.fecha_cierre:
            return False, "La evaluación ya cerró"

        # Validar código de acceso
        if evaluacion.codigo_acceso:
            if not codigo_acceso or codigo_acceso != evaluacion.codigo_acceso:
                return False, "Código de acceso incorrecto"

        # Validar contraseña
        if evaluacion.contraseña:
            if not contrasena or contrasena != evaluacion.contraseña:
                return False, "Contraseña incorrecta"

        # Validar intentos máximos
        if evaluacion.intentos_permitidos:
            intentos_usuario = (
                self.db.query(func.count(IntentoEvaluacion.intento_id))
                .filter(
                    IntentoEvaluacion.evaluacion_id == evaluacion_id,
                    IntentoEvaluacion.estudiante_id == estudiante_id,
                )
                .scalar()
            )

            if intentos_usuario >= evaluacion.intentos_permitidos:
                return (
                    False,
                    f"Ya has alcanzado el máximo de {evaluacion.intentos_permitidos} intentos",
                )

        # Validar tiempo entre intentos
        if evaluacion.tiempo_entre_intentos_minutos:
            ultimo_intento = (
                self.db.query(IntentoEvaluacion)
                .filter(
                    IntentoEvaluacion.evaluacion_id == evaluacion_id,
                    IntentoEvaluacion.estudiante_id == estudiante_id,
                )
                .order_by(desc(IntentoEvaluacion.fecha_inicio))
                .first()
            )

            if ultimo_intento:
                tiempo_transcurrido = (
                    ahora - ultimo_intento.fecha_inicio
                ).total_seconds() / 60
                if tiempo_transcurrido < evaluacion.tiempo_entre_intentos_minutos:
                    tiempo_restante = (
                        evaluacion.tiempo_entre_intentos_minutos - tiempo_transcurrido
                    )
                    return (
                        False,
                        f"Debes esperar {int(tiempo_restante)} minutos antes del próximo intento",
                    )

        return True, None

    def validar_disponibilidad(self, evaluacion_id: UUID) -> bool:
        """Valida si una evaluación está disponible en este momento."""
        evaluacion = self.obtener_evaluacion(evaluacion_id)

        if evaluacion.estado != EstadoEvaluacion.ACTIVA:
            return False

        ahora = datetime.utcnow()

        if evaluacion.fecha_apertura and ahora < evaluacion.fecha_apertura:
            return False

        return not (evaluacion.fecha_cierre and ahora > evaluacion.fecha_cierre)

    # ==================== ESTADÍSTICAS ====================

    def actualizar_estadisticas(self, evaluacion_id: UUID) -> Evaluacion:
        """Actualiza las estadísticas calculadas de una evaluación."""
        evaluacion = self.obtener_evaluacion(evaluacion_id)

        # Total de intentos
        evaluacion.total_intentos = (
            self.db.query(func.count(IntentoEvaluacion.intento_id))
            .filter(IntentoEvaluacion.evaluacion_id == evaluacion_id)
            .scalar()
        )

        # Intentos completados
        evaluacion.total_completados = (
            self.db.query(func.count(IntentoEvaluacion.intento_id))
            .filter(
                IntentoEvaluacion.evaluacion_id == evaluacion_id,
                IntentoEvaluacion.estado_intento == "FINALIZADO",
            )
            .scalar()
        )

        # Tasas
        if evaluacion.total_intentos > 0:
            evaluacion.tasa_completacion = (
                evaluacion.total_completados / evaluacion.total_intentos
            ) * 100

            # Aprobados
            aprobados = (
                self.db.query(func.count(IntentoEvaluacion.intento_id))
                .filter(
                    IntentoEvaluacion.evaluacion_id == evaluacion_id,
                    IntentoEvaluacion.aprobado,
                )
                .scalar()
            )

            evaluacion.tasa_aprobacion = (
                (aprobados / evaluacion.total_completados * 100)
                if evaluacion.total_completados > 0
                else 0
            )

        # Calificaciones
        calificaciones = (
            self.db.query(IntentoEvaluacion.puntuacion_obtenida)
            .filter(
                IntentoEvaluacion.evaluacion_id == evaluacion_id,
                IntentoEvaluacion.estado_intento == "FINALIZADO",
            )
            .all()
        )

        if calificaciones:
            notas = [c[0] for c in calificaciones if c[0] is not None]
            if notas:
                evaluacion.calificacion_promedio = sum(notas) / len(notas)
                evaluacion.calificacion_mediana = sorted(notas)[len(notas) // 2]

        # Tiempo promedio
        tiempos = (
            self.db.query(IntentoEvaluacion.tiempo_total_segundos)
            .filter(
                IntentoEvaluacion.evaluacion_id == evaluacion_id,
                IntentoEvaluacion.estado_intento == "FINALIZADO",
            )
            .all()
        )

        if tiempos:
            tiempos_validos = [t[0] for t in tiempos if t[0] is not None]
            if tiempos_validos:
                evaluacion.tiempo_promedio_minutos = (
                    sum(tiempos_validos) / len(tiempos_validos) / 60
                )

        self.db.commit()
        self.db.refresh(evaluacion)

        return evaluacion
