"""Service para gestión de Inscripciones Académicas.

Contiene toda la lógica de negocio del sistema de inscripciones.
Implementa validaciones complejas, workflow de estados, verificación de cupos.

Principios SOLID:
- Single Responsibility: Cada método una responsabilidad
- Open/Closed: Extensible sin modificar
- Liskov Substitution: Interfaces consistentes
- Interface Segregation: Métodos específicos
- Dependency Inversion: Depende de abstracciones

Clean Code:
- Nombres descriptivos y claros
- Métodos pequeños y enfocados
- Documentación exhaustiva
- Manejo de errores explícito
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
import logging
import secrets
import string
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.redis_manager import RedisManager
from src.crud.academic.crud_inscripcion import inscripcion_crud
from src.crud.academic.crud_periodo_academico import periodo_academico_crud
from src.enums.academic import (
    EstadoInscripcion,
    MotivoRechazo,
    MotivoRetiro,
)
from src.models.academic.grupo import Grupo
from src.models.academic.inscripcion import Inscripcion
from src.models.users.usuario import Usuario
from src.schemas.academic.inscripcion_schemas import (
    InscripcionCreate,
    InscripcionFiltros,
)


logger = logging.getLogger(__name__)


class InscripcionAcademicaService:
    """Servicio principal para gestión de inscripciones académicas.

    Responsabilidades:
    - Validaciones de negocio complejas
    - Workflow de estados (17 estados posibles)
    - Verificación de cupos y requisitos
    - Gestión de lista de espera
    - Cálculos financieros
    - Cache de inscripciones con Redis
    - Validación de permisos por rol
    """

    CACHE_PREFIX = "inscripcion"
    CACHE_TTL_INSCRIPCION = 1800  # 30 minutos
    CACHE_TTL_CUPOS = 120  # 2 minutos

    def __init__(self, redis_manager: RedisManager | None = None) -> None:
        self.redis = redis_manager

    # ==================== Creación de Inscripciones ====================

    def crear_inscripcion(
        self, db: Session, inscripcion_in: InscripcionCreate, usuario: Usuario
    ) -> Inscripcion:
        """Crea una nueva inscripción con validaciones completas.

        Flujo de validaciones:
        1. Período académico activo y permite inscripciones
        2. Grupo existe y tiene cupos disponibles
        3. No existe inscripción duplicada
        4. Cumple límites de créditos del período
        5. Cumple prerequisitos del curso (si aplica)
        6. Calcula costos con descuentos y becas
        7. Determina estado inicial según flujo

        Args:
            db: Sesión de base de datos
            inscripcion_in: Datos de la inscripción
            usuario: Usuario que crea (estudiante o coordinador)

        Returns:
            Inscripción creada con estado inicial

        Raises:
            HTTPException: Si falla alguna validación
        """
        try:
            # 1. Validar período académico
            periodo = periodo_academico_crud.get(
                db, inscripcion_in.periodo_academico_id
            )
            if not periodo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Período académico {inscripcion_in.periodo_academico_id} no encontrado",
                )

            if not periodo.permite_inscribirse_ahora:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El período '{periodo.nombre}' no está aceptando inscripciones. "
                    f"Inscripciones abiertas: {periodo.fecha_inicio_inscripciones} - "
                    f"{periodo.fecha_fin_inscripciones}",
                )

            # 2. Validar grupo
            grupo = (
                db.query(Grupo)
                .filter(Grupo.grupo_id == inscripcion_in.grupo_id)
                .first()
            )
            if not grupo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Grupo {inscripcion_in.grupo_id} no encontrado",
                )

            # 3. Verificar cupos disponibles
            cupos_disponibles = self._verificar_cupos_disponibles(db, grupo)
            if cupos_disponibles <= 0:
                # Agregar a lista de espera si está habilitado
                if grupo.permite_lista_espera:
                    logger.info(
                        f"Grupo {grupo.grupo_id} sin cupos. "
                        f"Agregando a lista de espera"
                    )
                    return self._crear_inscripcion_lista_espera(
                        db, inscripcion_in, usuario, grupo
                    )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El grupo '{grupo.nombre}' no tiene cupos disponibles. "
                    f"Capacidad máxima: {grupo.capacidad_maxima}",
                )

            # 4. Validar inscripción duplicada
            if inscripcion_crud.existe_inscripcion(
                db, inscripcion_in.estudiante_id, inscripcion_in.grupo_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe una inscripción activa para este estudiante en este grupo",
                )

            # 5. Validar límites de créditos del período
            self._validar_limites_creditos(
                db,
                inscripcion_in.estudiante_id,
                inscripcion_in.periodo_academico_id,
                inscripcion_in.creditos_inscritos or 0,
                periodo,
            )

            # 6. Validar prerequisitos (si aplica)
            # TODO: Implementar cuando exista tabla de prerequisitos de curso
            # self._validar_prerequisitos(db, inscripcion_in.estudiante_id, grupo.curso_id)

            # 7. Calcular costos
            costos = self._calcular_costos(db, inscripcion_in, grupo, periodo)

            # 8. Crear inscripción en base de datos
            inscripcion = inscripcion_crud.create(
                db, obj_in=inscripcion_in, creado_por_id=usuario.usuario_id
            )

            # 9. Asignar costos calculados
            inscripcion.costo_total = costos["costo_total"]
            inscripcion.costo_matricula = costos.get("costo_matricula")
            inscripcion.costo_curso = costos.get("costo_curso")
            inscripcion.otros_costos = costos.get("otros_costos")
            inscripcion.descuentos = costos["descuentos"]
            inscripcion.monto_final = costos["monto_final"]

            # 10. Determinar estado inicial según flujo de negocio
            inscripcion.estado = self._determinar_estado_inicial(inscripcion, costos)
            inscripcion.fecha_solicitud = datetime.now(UTC)

            db.add(inscripcion)
            db.commit()
            db.refresh(inscripcion)

            # 11. Invalidar cache
            self._invalidar_cache_grupo(inscripcion.grupo_id)
            self._invalidar_cache_estudiante(inscripcion.estudiante_id)

            logger.info(
                f"Inscripción {inscripcion.codigo_inscripcion} creada exitosamente. "
                f"Estudiante: {inscripcion_in.estudiante_id}, "
                f"Grupo: {inscripcion_in.grupo_id}, "
                f"Estado: {inscripcion.estado}"
            )

            return inscripcion

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creando inscripción: {e!s}", exc_info=True)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno al crear inscripción: {e!s}",
            ) from e

    # ==================== Consultas ====================

    def obtener_inscripcion(
        self, db: Session, inscripcion_id: int, usuario: Usuario
    ) -> Inscripcion:
        """Obtiene una inscripción con validación de permisos.

        Validaciones de permisos:
        - Estudiante: solo puede ver sus propias inscripciones
        - Docente: puede ver inscripciones de sus grupos
        - Coordinador: puede ver todas de su institución
        - Superadmin: puede ver todas
        """
        inscripcion = inscripcion_crud.get(db, inscripcion_id)
        if not inscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inscripción {inscripcion_id} no encontrada",
            )

        # Validar permisos
        self._validar_permisos_lectura(usuario, inscripcion)

        return inscripcion

    def listar_inscripciones_estudiante(
        self,
        db: Session,
        estudiante_id: int,
        usuario: Usuario,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Inscripcion], int]:
        """Lista inscripciones de un estudiante.

        Returns:
            Tuple con (lista_inscripciones, total)
        """
        # Validar permisos
        if usuario.rol == "estudiante" and usuario.usuario_id != estudiante_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver inscripciones de otro estudiante",
            )

        inscripciones = inscripcion_crud.get_by_estudiante(
            db, estudiante_id, skip=skip, limit=limit
        )

        # Contar total
        total = len(inscripcion_crud.get_by_estudiante(db, estudiante_id))

        return inscripciones, total

    def listar_inscripciones_grupo(
        self,
        db: Session,
        grupo_id: int,
        usuario: Usuario,
        *,
        solo_activas: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Inscripcion], int]:
        """Lista inscripciones de un grupo.

        Args:
            solo_activas: Si True, solo retorna inscripciones activas
        """
        # Validar permisos
        if usuario.rol not in ["docente", "coordinador", "superadmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver inscripciones del grupo",
            )

        if solo_activas:
            inscripciones = inscripcion_crud.get_activas(
                db, grupo_id=grupo_id, skip=skip, limit=limit
            )
        else:
            inscripciones = inscripcion_crud.get_by_grupo(
                db, grupo_id, skip=skip, limit=limit
            )

        # Contar total
        total = len(inscripcion_crud.get_by_grupo(db, grupo_id))

        return inscripciones, total

    def listar_con_filtros(
        self,
        db: Session,
        filtros: InscripcionFiltros,
        usuario: Usuario,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Inscripcion], int]:
        """Lista inscripciones con filtros avanzados."""
        # Aplicar filtros según rol
        if usuario.rol == "estudiante":
            filtros.estudiante_id = usuario.usuario_id

        return inscripcion_crud.get_by_filtros(
            db,
            estudiante_id=filtros.estudiante_id,
            grupo_id=filtros.grupo_id,
            periodo_id=filtros.periodo_id,
            programa_id=filtros.programa_id,
            estado=filtros.estado,
            tipo=filtros.tipo,
            esta_pagado=filtros.esta_pagado,
            esta_aprobada=filtros.esta_aprobada,
            en_lista_espera=filtros.en_lista_espera,
            fecha_desde=filtros.fecha_desde,
            fecha_hasta=filtros.fecha_hasta,
            activo=filtros.activo,
            skip=skip,
            limit=limit,
        )

    # ==================== Operaciones de Estado ====================

    def aprobar_inscripcion(
        self,
        db: Session,
        inscripcion_id: int,
        usuario: Usuario,
        comentarios: str | None = None,
    ) -> Inscripcion:
        """Aprueba una inscripción pendiente.

        Solo coordinadores y superadmin pueden aprobar.
        """
        # Validar permisos
        if usuario.rol not in ["coordinador", "superadmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo coordinadores pueden aprobar inscripciones",
            )

        inscripcion = inscripcion_crud.get(db, inscripcion_id)
        if not inscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inscripción {inscripcion_id} no encontrada",
            )

        # Validar estado actual
        if inscripcion.estado != EstadoInscripcion.pendiente_aprobacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La inscripción no está pendiente de aprobación. "
                f"Estado actual: {inscripcion.estado}",
            )

        # Aprobar
        inscripcion_aprobada = inscripcion_crud.aprobar(
            db, inscripcion_id, usuario.usuario_id, comentarios
        )

        # Invalidar cache
        self._invalidar_cache_inscripcion(inscripcion_id)

        logger.info(
            f"Inscripción {inscripcion_id} aprobada por usuario {usuario.usuario_id}"
        )

        return inscripcion_aprobada

    def rechazar_inscripcion(
        self,
        db: Session,
        inscripcion_id: int,
        motivo: MotivoRechazo,
        descripcion: str,
        usuario: Usuario,
    ) -> Inscripcion:
        """Rechaza una inscripción."""
        if usuario.rol not in ["coordinador", "superadmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo coordinadores pueden rechazar inscripciones",
            )

        inscripcion = inscripcion_crud.get(db, inscripcion_id)
        if not inscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inscripción {inscripcion_id} no encontrada",
            )

        # Rechazar
        inscripcion_rechazada = inscripcion_crud.rechazar(
            db, inscripcion_id, motivo, descripcion, usuario.usuario_id
        )

        # Liberar cupo si ocupaba uno
        if inscripcion.estado in [
            EstadoInscripcion.aprobada,
            EstadoInscripcion.confirmada,
            EstadoInscripcion.activa,
        ]:
            self._liberar_cupo_y_procesar_lista_espera(db, inscripcion.grupo_id)

        self._invalidar_cache_inscripcion(inscripcion_id)

        logger.warning(
            f"Inscripción {inscripcion_id} rechazada por usuario {usuario.usuario_id}. "
            f"Motivo: {motivo.value}"
        )

        return inscripcion_rechazada

    def confirmar_inscripcion(
        self, db: Session, inscripcion_id: int, usuario: Usuario
    ) -> Inscripcion:
        """Confirma una inscripción (estudiante acepta asistir).

        Solo el estudiante dueño puede confirmar.
        """
        inscripcion = inscripcion_crud.get(db, inscripcion_id)
        if not inscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inscripción {inscripcion_id} no encontrada",
            )

        # Validar que sea el estudiante o admin
        if (
            usuario.rol == "estudiante"
            and usuario.usuario_id != inscripcion.estudiante_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el estudiante puede confirmar su inscripción",
            )

        # Validar que esté aprobada
        if inscripcion.estado != EstadoInscripcion.aprobada:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La inscripción no está aprobada. "
                f"Estado actual: {inscripcion.estado}",
            )

        # Validar pago si es requerido
        if inscripcion.monto_final and inscripcion.monto_final > 0:
            if not inscripcion.esta_pagado:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Debe completar el pago (${inscripcion.monto_final}) "
                    "antes de confirmar la inscripción",
                )

        # Validar documentos si son requeridos
        if inscripcion.documentos_requeridos and not inscripcion.documentos_completos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe completar la documentación requerida antes de confirmar",
            )

        # Confirmar
        inscripcion_confirmada = inscripcion_crud.confirmar(
            db, inscripcion_id, usuario.usuario_id
        )

        self._invalidar_cache_inscripcion(inscripcion_id)

        logger.info(
            f"Inscripción {inscripcion_id} confirmada por estudiante {usuario.usuario_id}"
        )

        return inscripcion_confirmada

    def retirar_inscripcion(
        self,
        db: Session,
        inscripcion_id: int,
        motivo: MotivoRetiro,
        descripcion: str,
        usuario: Usuario,
        es_voluntario: bool = True,
    ) -> Inscripcion:
        """Retira una inscripción.

        Args:
            es_voluntario: Si True, es retiro voluntario del estudiante.
                          Si False, es retiro forzado (académico/administrativo)
        """
        inscripcion = inscripcion_crud.get(db, inscripcion_id)
        if not inscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inscripción {inscripcion_id} no encontrada",
            )

        # Validar permisos
        if usuario.rol == "estudiante":
            if usuario.usuario_id != inscripcion.estudiante_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No puede retirar inscripción de otro estudiante",
                )
            if not inscripcion.puede_retirar:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Esta inscripción no permite retiro",
                )

        # Retirar
        inscripcion_retirada = inscripcion_crud.retirar(
            db, inscripcion_id, motivo, descripcion, es_voluntario, usuario.usuario_id
        )

        # Liberar cupo y procesar lista de espera
        self._liberar_cupo_y_procesar_lista_espera(db, inscripcion.grupo_id)

        self._invalidar_cache_inscripcion(inscripcion_id)

        logger.info(
            f"Inscripción {inscripcion_id} retirada. "
            f"Motivo: {motivo.value}, Voluntario: {es_voluntario}"
        )

        return inscripcion_retirada

    def activar_inscripcion(
        self, db: Session, inscripcion_id: int, usuario: Usuario
    ) -> Inscripcion:
        """Activa una inscripción (estudiante puede asistir a clases).

        Solo coordinadores pueden activar.
        """
        if usuario.rol not in ["coordinador", "superadmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo coordinadores pueden activar inscripciones",
            )

        inscripcion = inscripcion_crud.get(db, inscripcion_id)
        if not inscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inscripción {inscripcion_id} no encontrada",
            )

        # Validar que esté confirmada
        if inscripcion.estado != EstadoInscripcion.confirmada:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se pueden activar inscripciones confirmadas. "
                f"Estado actual: {inscripcion.estado}",
            )

        # Activar
        inscripcion_activa = inscripcion_crud.activar(
            db, inscripcion_id, usuario.usuario_id
        )

        self._invalidar_cache_inscripcion(inscripcion_id)

        logger.info(f"Inscripción {inscripcion_id} activada")

        return inscripcion_activa

    def registrar_pago(
        self,
        db: Session,
        inscripcion_id: int,
        monto: Decimal,
        referencia: str | None,
        forma_pago: str,
        usuario: Usuario,
    ) -> Inscripcion:
        """Registra el pago de una inscripción.

        Al registrar pago exitoso, puede cambiar estado automáticamente.
        """
        inscripcion = inscripcion_crud.get(db, inscripcion_id)
        if not inscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inscripción {inscripcion_id} no encontrada",
            )

        # Validar que requiera pago
        if not inscripcion.monto_final or inscripcion.monto_final <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta inscripción no requiere pago",
            )

        # Validar monto
        if monto < inscripcion.monto_final:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El monto pagado (${monto}) es menor al requerido "
                f"(${inscripcion.monto_final})",
            )

        # Registrar pago
        inscripcion.registrar_pago(monto, referencia, forma_pago)
        inscripcion.modificado_por_id = usuario.usuario_id

        # Cambio de estado automático si estaba pendiente de pago
        if inscripcion.estado == EstadoInscripcion.pendiente_pago and (
            inscripcion.documentos_completos or not inscripcion.documentos_requeridos
        ):
            inscripcion.estado = EstadoInscripcion.aprobada
            logger.info(f"Inscripción {inscripcion_id} cambió a APROBADA tras pago")

        db.add(inscripcion)
        db.commit()
        db.refresh(inscripcion)

        self._invalidar_cache_inscripcion(inscripcion_id)

        logger.info(
            f"Pago registrado para inscripción {inscripcion_id}. "
            f"Monto: ${monto}, Referencia: {referencia}, Forma: {forma_pago}"
        )

        return inscripcion

    # ==================== Estadísticas ====================

    def obtener_estadisticas_grupo(
        self, db: Session, grupo_id: int, usuario: Usuario
    ) -> dict[str, Any]:
        """Obtiene estadísticas completas de inscripciones de un grupo.

        Returns:
            Dict con:
            - total_inscritos
            - cupos_disponibles
            - porcentaje_ocupacion
            - en_lista_espera
            - estadisticas_por_estado
            - estadisticas_financieras
        """
        if usuario.rol not in ["docente", "coordinador", "superadmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver estadísticas",
            )

        grupo = db.query(Grupo).filter(Grupo.grupo_id == grupo_id).first()
        if not grupo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grupo {grupo_id} no encontrado",
            )

        # Cupos
        total_inscritos = inscripcion_crud.contar_inscripciones_activas_grupo(
            db, grupo_id
        )
        cupos_disponibles = self._verificar_cupos_disponibles(db, grupo)

        # Lista de espera
        lista_espera = inscripcion_crud.get_lista_espera(db, grupo_id)

        # Inscripciones por estado
        todas = inscripcion_crud.get_by_grupo(db, grupo_id)
        por_estado = {}
        for inscripcion in todas:
            estado = inscripcion.estado
            por_estado[estado] = por_estado.get(estado, 0) + 1

        return {
            "grupo_id": grupo_id,
            "nombre_grupo": grupo.nombre,
            "cupo_maximo": grupo.capacidad_maxima,
            "total_inscritos": total_inscritos,
            "cupos_disponibles": cupos_disponibles,
            "porcentaje_ocupacion": round(
                (
                    (total_inscritos / grupo.capacidad_maxima * 100)
                    if grupo.capacidad_maxima > 0
                    else 0
                ),
                2,
            ),
            "en_lista_espera": len(lista_espera),
            "esta_lleno": cupos_disponibles <= 0,
            "inscripciones_por_estado": por_estado,
        }

    def obtener_estadisticas_periodo(
        self, db: Session, periodo_id: int, usuario: Usuario
    ) -> dict[str, Any]:
        """Obtiene estadísticas de inscripciones de un período."""
        if usuario.rol not in ["coordinador", "superadmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver estadísticas de período",
            )

        return inscripcion_crud.get_estadisticas_periodo(db, periodo_id)

    # ==================== Métodos Privados ====================

    def _verificar_cupos_disponibles(self, db: Session, grupo: Grupo) -> int:
        """Verifica cuántos cupos quedan disponibles en un grupo.

        Returns:
            Número de cupos disponibles (999 si no hay límite)
        """
        if not grupo.capacidad_maxima or grupo.capacidad_maxima <= 0:
            return 999  # Sin límite

        inscritos = inscripcion_crud.contar_inscripciones_activas_grupo(
            db, grupo.grupo_id
        )
        return max(0, grupo.capacidad_maxima - inscritos)

    def _validar_limites_creditos(
        self,
        db: Session,
        estudiante_id: int,
        periodo_id: int,
        creditos_nuevos: int,
        periodo,
    ) -> None:
        """Valida que no se excedan los límites de créditos del período.

        Raises:
            HTTPException: Si excede el límite
        """
        if not creditos_nuevos or creditos_nuevos == 0:
            return

        creditos_actuales = inscripcion_crud.contar_creditos_inscritos_periodo(
            db, estudiante_id, periodo_id
        )

        total_creditos = creditos_actuales + creditos_nuevos

        # Validar máximo
        if periodo.creditos_maximos and total_creditos > periodo.creditos_maximos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Excede el límite de créditos del período. "
                    f"Máximo permitido: {periodo.creditos_maximos}, "
                    f"Ya inscritos: {creditos_actuales}, "
                    f"Intentando agregar: {creditos_nuevos}, "
                    f"Total resultante: {total_creditos}"
                ),
            )

        # Validar mínimo
        if periodo.creditos_minimos and total_creditos < periodo.creditos_minimos:
            logger.warning(
                f"Estudiante {estudiante_id} tiene menos créditos que el mínimo. "
                f"Mínimo: {periodo.creditos_minimos}, Total: {total_creditos}"
            )

    def _calcular_costos(
        self, db: Session, inscripcion_in: InscripcionCreate, grupo: Grupo, periodo
    ) -> dict[str, Decimal]:
        """Calcula costos de la inscripción con descuentos y becas.

        Returns:
            Dict con costo_total, costo_matricula, costo_curso,
            otros_costos, descuentos, monto_final
        """
        # Costo de matrícula del período
        costo_matricula = Decimal(periodo.costo_matricula or 0)

        # Costo del curso (si tiene)
        # TODO: Obtener costo del curso desde modelo Curso
        costo_curso = Decimal(0)

        # Otros costos
        otros_costos = Decimal(0)

        # Total sin descuentos
        costo_total = costo_matricula + costo_curso + otros_costos

        # Aplicar descuentos por beca
        descuentos = Decimal(0)
        if inscripcion_in.tiene_beca and inscripcion_in.porcentaje_beca:
            descuentos = costo_total * (Decimal(inscripcion_in.porcentaje_beca) / 100)

        # Monto final a pagar
        monto_final = max(Decimal(0), costo_total - descuentos)

        return {
            "costo_total": costo_total,
            "costo_matricula": costo_matricula,
            "costo_curso": costo_curso,
            "otros_costos": otros_costos,
            "descuentos": descuentos,
            "monto_final": monto_final,
        }

    def _determinar_estado_inicial(
        self, inscripcion: Inscripcion, costos: dict[str, Decimal]
    ) -> EstadoInscripcion:
        """Determina el estado inicial de una inscripción según el flujo.

        Lógica:
        1. Si requiere aprobación → pendiente_aprobacion
        2. Si requiere documentos → pendiente_documentos
        3. Si requiere pago → pendiente_pago
        4. Sino → aprobada
        """
        if inscripcion.requiere_aprobacion:
            return EstadoInscripcion.pendiente_aprobacion

        if inscripcion.documentos_requeridos and not inscripcion.documentos_completos:
            return EstadoInscripcion.pendiente_documentos

        if costos["monto_final"] > 0:
            return EstadoInscripcion.pendiente_pago

        return EstadoInscripcion.aprobada

    def _crear_inscripcion_lista_espera(
        self,
        db: Session,
        inscripcion_in: InscripcionCreate,
        usuario: Usuario,
        grupo: Grupo,
    ) -> Inscripcion:
        """Crea inscripción en lista de espera cuando no hay cupos.

        Asigna posición automáticamente.
        """
        lista_espera_actual = inscripcion_crud.get_lista_espera(db, grupo.grupo_id)
        posicion = len(lista_espera_actual) + 1

        inscripcion = inscripcion_crud.create(
            db, obj_in=inscripcion_in, creado_por_id=usuario.usuario_id
        )

        inscripcion.agregar_a_lista_espera(posicion)
        inscripcion.estado = EstadoInscripcion.en_lista_espera

        db.add(inscripcion)
        db.commit()
        db.refresh(inscripcion)

        logger.info(
            f"Inscripción {inscripcion.codigo_inscripcion} agregada a lista de espera. "
            f"Posición: {posicion}"
        )

        return inscripcion

    def _liberar_cupo_y_procesar_lista_espera(self, db: Session, grupo_id: int) -> None:
        """Libera un cupo y procesa lista de espera automáticamente.

        Promueve al primero de la lista si hay cupos disponibles.
        """
        lista_espera = inscripcion_crud.get_lista_espera(db, grupo_id)

        if not lista_espera:
            logger.info(
                f"No hay inscripciones en lista de espera para grupo {grupo_id}"
            )
            return

        # Obtener grupo para verificar cupos
        grupo = db.query(Grupo).filter(Grupo.grupo_id == grupo_id).first()
        if not grupo:
            return

        cupos_disponibles = self._verificar_cupos_disponibles(db, grupo)
        if cupos_disponibles <= 0:
            logger.info("No hay cupos disponibles para promover de lista de espera")
            return

        # Promover al primero de la lista
        primera_inscripcion = lista_espera[0]
        primera_inscripcion.salir_lista_espera()
        primera_inscripcion.notificado_cupo_disponible = True
        primera_inscripcion.fecha_notificacion_cupo = datetime.now(UTC)

        db.add(primera_inscripcion)
        db.commit()

        logger.info(
            f"Inscripción {primera_inscripcion.id} promovida de lista de espera. "
            f"Nuevo estado: {primera_inscripcion.estado}"
        )

    def _validar_permisos_lectura(
        self, usuario: Usuario, inscripcion: Inscripcion
    ) -> None:
        """Valida permisos de lectura sobre una inscripción.

        Reglas:
        - Superadmin: puede ver todas
        - Coordinador: puede ver todas de su institución
        - Docente: puede ver las de sus grupos
        - Estudiante: solo las propias

        Raises:
            HTTPException 403: Si no tiene permisos
        """
        if usuario.rol == "superadmin":
            return

        if usuario.rol == "coordinador":
            # TODO: Validar misma institución cuando esté el campo
            return

        if usuario.rol == "docente":
            # TODO: Validar que sea docente del grupo
            return

        if usuario.rol == "estudiante":
            if usuario.usuario_id != inscripcion.estudiante_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para ver esta inscripción",
                )
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a esta inscripción",
        )

    def _invalidar_cache_inscripcion(self, inscripcion_id: int) -> None:
        """Invalida cache de una inscripción específica."""
        if not self.redis:
            return

        try:
            self.redis.delete(f"{self.CACHE_PREFIX}:id:{inscripcion_id}")
        except Exception as e:
            logger.warning(f"Error invalidando cache de inscripción: {e!s}")

    def _invalidar_cache_grupo(self, grupo_id: int) -> None:
        """Invalida cache de un grupo."""
        if not self.redis:
            return

        try:
            pattern = f"{self.CACHE_PREFIX}:grupo:{grupo_id}*"
            self.redis.delete_pattern(pattern)
        except Exception as e:
            logger.warning(f"Error invalidando cache de grupo: {e!s}")

    def _invalidar_cache_estudiante(self, estudiante_id: int) -> None:
        """Invalida cache de un estudiante."""
        if not self.redis:
            return

        try:
            pattern = f"{self.CACHE_PREFIX}:estudiante:{estudiante_id}*"
            self.redis.delete_pattern(pattern)
        except Exception as e:
            logger.warning(f"Error invalidando cache de estudiante: {e!s}")


# ==================== Legacy Service (para códigos de acceso) ====================


class InscripcionService:
    """Service para inscripciones y códigos de acceso."""

    # Constantes
    CODIGO_LENGTH = 8
    CODIGO_EXPIRACION_DIAS = 30

    @staticmethod
    def inscribir_por_codigo(
        db: Session, codigo_acceso: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Inscribe estudiante usando código de acceso del curso."""
        try:
            # Validar rol permitido
            if usuario.rol not in ["estudiante", "docente"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo estudiantes y docentes pueden usar códigos de curso",
                )

            # Buscar curso por código
            curso = InscripcionService._obtener_curso_por_codigo(db, codigo_acceso)

            # Validar institución
            InscripcionService._validar_misma_institucion(
                db, curso["curso_id"], usuario
            )

            # Verificar si ya está inscrito
            if InscripcionService._esta_inscrito(
                db, curso["curso_id"], usuario.usuario_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya estás inscrito en este curso",
                )

            # Diferente lógica según el rol
            if usuario.rol == "docente":
                # Vincular docente al curso
                InscripcionService._vincular_docente_curso(db, usuario.usuario_id, curso["curso_id"])
                logger.info(f"Docente {usuario.usuario_id} asignado a curso {curso['curso_id']}")
                return {
                    "success": True,
                    "message": f"Te has asignado exitosamente como docente de {curso['nombre']}",
                    "data": {
                        "curso_id": curso["curso_id"],
                        "curso_nombre": curso["nombre"],
                    },
                }
            else:
                # Inscribir estudiante: crear grupo si no existe y vincular
                grupo_id = InscripcionService._obtener_o_crear_grupo(db, curso["curso_id"])
                InscripcionService._vincular_estudiante_grupo(
                    db, usuario.usuario_id, grupo_id
                )

                logger.info(
                    f"Estudiante {usuario.usuario_id} inscrito en curso {curso['curso_id']}"
                )

                return {
                    "success": True,
                    "message": f"Te has inscrito exitosamente en {curso['nombre']}",
                    "data": {
                        "curso_id": curso["curso_id"],
                        "curso_nombre": curso["nombre"],
                        "grupo_id": str(grupo_id),
                    },
                }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error en inscripción: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al inscribir: {e!s}",
            ) from e

    @staticmethod
    def generar_codigo_invitacion(
        db: Session, programa_id: str | None, usuario: Usuario, descripcion: str | None = None
    , dias_validez: int = 30
    ) -> dict[str, Any]:
        """Genera código de invitación para un programa o institución."""
        try:
            if usuario.rol != "coordinador":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo coordinadores pueden generar códigos",
                )

            # Obtener institución del coordinador a través de la tabla intermedia
            institucion_query = text(
                """
                SELECT ic.institucion_id 
                FROM "InstitucionCoordinador" ic
                WHERE ic.coordinador_id = :coordinador_id
                LIMIT 1
                """
            )
            institucion_result = db.execute(
                institucion_query, {"coordinador_id": usuario.usuario_id}
            ).fetchone()
            
            if not institucion_result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Coordinador no vinculado a institución",
                )
            
            institucion_id = institucion_result[0]

            # Generar código único
            codigo = InscripcionService._generar_codigo_unico(db)
            fecha_expiracion = datetime.now(UTC) + timedelta(
                days=dias_validez
            )

            # Guardar en BD con institucion_id
            query = text(
                """
                INSERT INTO "InvitationToken" (
                    token, programa_id, institucion_id, created_by, created_at,
                    expires_at, descripcion, is_active
                )
                VALUES (
                    :token, :programa_id, :institucion_id, :created_by, :created_at,
                    :expires_at, :descripcion, true
                )
                RETURNING token_id
            """
            )

            result = db.execute(
                query,
                {
                    "token": codigo,
                    "programa_id": programa_id,
                    "institucion_id": institucion_id,
                    "created_by": usuario.usuario_id,
                    "created_at": datetime.now(UTC),
                    "expires_at": fecha_expiracion,
                    "descripcion": descripcion,
                },
            )

            result.fetchone()[0]
            db.commit()

            logger.info(f"Código de invitación generado: {codigo}")

            return {
                "success": True,
                "message": "Código de invitación generado",
                "data": {
                    "codigo": codigo,
                    "expira_en": fecha_expiracion.isoformat(),
                    "dias_validez": dias_validez,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error generando código: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar código: {e!s}",
            ) from e

    @staticmethod
    def vincular_por_codigo_invitacion(
        db: Session, codigo_invitacion: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Vincula estudiante o docente a programa usando código de invitación."""
        try:
            logger.info(f"Intentando vincular con código: '{codigo_invitacion}' (len={len(codigo_invitacion)})")
            
            if usuario.rol not in ["estudiante", "docente"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo estudiantes y profesores pueden usar códigos de invitación",
                )

            # Validar código
            token = InscripcionService._validar_codigo_invitacion(db, codigo_invitacion)

            # Vincular según el rol del usuario
            if usuario.rol == "estudiante":
                # Actualizar estudiante con el programa
                query = text(
                    """
                    UPDATE "Estudiante"
                    SET programa_id = :programa_id
                    WHERE estudiante_id = :estudiante_id
                """
                )

                db.execute(
                    query,
                    {
                        "programa_id": token["programa_id"],
                        "estudiante_id": usuario.usuario_id,
                    },
                )
            elif usuario.rol == "docente":
                # Vincular docente a institución
                query = text(
                    """
                    UPDATE "Docente"
                    SET institucion_id = :institucion_id
                    WHERE docente_id = :docente_id
                """
                )

                db.execute(
                    query,
                    {
                        "institucion_id": token["institucion_id"],
                        "docente_id": usuario.usuario_id,
                    },
                )

            # Marcar código como usado
            InscripcionService._marcar_codigo_usado(
                db, token["token_id"], usuario.usuario_id
            )

            db.commit()

            rol_texto = "Docente" if usuario.rol == "docente" else "Estudiante"
            logger.info(
                f"{rol_texto} {usuario.usuario_id} vinculado a programa {token['programa_id']}"
            )

            return {
                "success": True,
                "message": "Te has vinculado exitosamente al programa",
                "data": {
                    "programa_id": token["programa_id"],
                    "programa_nombre": token["programa_nombre"],
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error vinculando por código: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al vincular: {e!s}",
            ) from e

    # ========== MÉTODOS PRIVADOS ==========

    @staticmethod
    def _obtener_curso_por_codigo(db: Session, codigo: str) -> dict[str, Any]:
        """Obtiene curso por código de acceso."""
        query = text(
            """
            SELECT c.curso_id, c.nombre, c.descripcion, c.institucion_id
            FROM "Curso" c
            WHERE c.codigo_acceso = :codigo AND c.estado IN ('inscripciones_abiertas', 'en_curso', 'programado')
        """
        )

        result = db.execute(query, {"codigo": codigo}).fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Código de acceso inválido o curso inactivo",
            )

        return dict(result._mapping)

    @staticmethod
    def _validar_misma_institucion(
        db: Session, curso_id: str, usuario: Usuario
    ) -> None:
        """Valida que estudiante/docente y curso sean de la misma institución."""
        
        if usuario.rol == "estudiante":
            query = text(
                """
                SELECT EXISTS(
                    SELECT 1
                    FROM "Estudiante" e
                    JOIN "Programa" p ON e.programa_id = p.programa_id
                    JOIN "Curso" c ON c.institucion_id = p.institucion_id
                    WHERE e.estudiante_id = :usuario_id
                        AND c.curso_id = :curso_id
                )
            """
            )
        elif usuario.rol == "docente":
            query = text(
                """
                SELECT EXISTS(
                    SELECT 1
                    FROM "Docente" d
                    JOIN "Curso" c ON c.institucion_id = d.institucion_id
                    WHERE d.docente_id = :usuario_id
                        AND c.curso_id = :curso_id
                )
            """
            )
        else:
            # Coordinadores u otros roles no necesitan validación
            return

        es_misma_institucion = db.execute(
            query, {"usuario_id": usuario.usuario_id, "curso_id": curso_id}
        ).scalar()

        if not es_misma_institucion:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes inscribirte en cursos de tu institución",
            )

    @staticmethod
    def _esta_inscrito(db: Session, curso_id: str, estudiante_id: UUID) -> bool:
        """Verifica si el estudiante ya está inscrito."""
        query = text(
            """
            SELECT EXISTS(
                SELECT 1 FROM "EstudianteGrupo" eg
                JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
                WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :estudiante_id
            )
        """
        )

        return db.execute(
            query, {"curso_id": curso_id, "estudiante_id": estudiante_id}
        ).scalar()

    @staticmethod
    def _obtener_o_crear_grupo(db: Session, curso_id: str) -> UUID:
        """Obtiene grupo principal del curso o lo crea."""
        # Buscar grupo existente
        query = text(
            """
            SELECT g.grupo_id
            FROM "Grupo" g
            JOIN "GrupoCurso" gc ON g.grupo_id = gc.grupo_id
            WHERE gc.curso_id = :curso_id
            LIMIT 1
        """
        )

        result = db.execute(query, {"curso_id": curso_id}).fetchone()

        if result:
            return result[0]

        # Crear nuevo grupo
        create_grupo = text(
            """
            INSERT INTO "Grupo" (nombre)
            VALUES ('Grupo Principal')
            RETURNING grupo_id
        """
        )

        grupo_id = db.execute(create_grupo).fetchone()[0]

        # Vincular al curso
        vincular = text(
            """
            INSERT INTO "GrupoCurso" (grupo_id, curso_id)
            VALUES (:grupo_id, :curso_id)
        """
        )

        db.execute(vincular, {"grupo_id": grupo_id, "curso_id": curso_id})
        db.commit()

        return grupo_id

    @staticmethod
    def _vincular_estudiante_grupo(
        db: Session, estudiante_id: UUID, grupo_id: UUID
    ) -> None:
        """Vincula estudiante a un grupo."""
        query = text(
            """
            INSERT INTO "EstudianteGrupo" (estudiante_id, grupo_id, fecha_inscripcion)
            VALUES (:estudiante_id, :grupo_id, :fecha_inscripcion)
        """
        )

        db.execute(
            query,
            {
                "estudiante_id": estudiante_id,
                "grupo_id": grupo_id,
                "fecha_inscripcion": datetime.now(UTC),
            },
        )

        db.commit()

    @staticmethod
    def _vincular_docente_curso(
        db: Session, docente_id: UUID, curso_id: str
    ) -> None:
        """Vincula docente a un curso."""
        query = text(
            """
            INSERT INTO "CursoDocente" (curso_id, docente_id, fecha_asignacion)
            VALUES (:curso_id, :docente_id, :fecha_asignacion)
            ON CONFLICT (curso_id, docente_id) DO NOTHING
            """
        )

        db.execute(
            query,
            {
                "curso_id": curso_id,
                "docente_id": docente_id,
                "fecha_asignacion": datetime.now(UTC),
            },
        )

        db.commit()

    @staticmethod
    def _generar_codigo_unico(db: Session) -> str:
        """Genera un código único alfanumérico."""
        caracteres = string.ascii_uppercase + string.digits

        while True:
            codigo = "".join(
                secrets.choice(caracteres)
                for _ in range(InscripcionService.CODIGO_LENGTH)
            )

            # Verificar que sea único
            query = text(
                'SELECT EXISTS(SELECT 1 FROM "InvitationToken" WHERE token = :token)'
            )
            existe = db.execute(query, {"token": codigo}).scalar()

            if not existe:
                return codigo

    @staticmethod
    def _validar_codigo_invitacion(db: Session, codigo: str) -> dict[str, Any]:
        """Valida y obtiene información del código de invitación."""
        logger.info(f"Validando código de invitación: '{codigo}'")
        
        query = text(
            """
            SELECT
                it.token_id,
                it.programa_id,
                p.nombre as programa_nombre,
                it.institucion_id,
                i.nombre as institucion_nombre,
                it.expires_at,
                it.is_active
            FROM "InvitationToken" it
            LEFT JOIN "Programa" p ON it.programa_id = p.programa_id
            LEFT JOIN "Institucion" i ON it.institucion_id = i.institucion_id
            WHERE it.token = :token
        """
        )

        result = db.execute(query, {"token": codigo}).fetchone()
        
        logger.info(f"Resultado de búsqueda: {result}")

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Código de invitación inválido",
            )

        token = dict(result._mapping)

        if not token["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este código ya no está activo",
            )

        if token["expires_at"] < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este código ha expirado",
            )

        return token

    @staticmethod
    def _marcar_codigo_usado(db: Session, token_id: str, usado_por: UUID) -> None:
        """Marca código como usado."""
        query = text(
            """
            UPDATE "InvitationToken"
            SET used_by = :usado_por,
                used_at = :usado_at,
                uses_count = uses_count + 1
            WHERE token_id = :token_id
        """
        )

        db.execute(
            query,
            {
                "token_id": token_id,
                "usado_por": usado_por,
                "usado_at": datetime.now(UTC),
            },
        )

    @staticmethod
    def confirmar_programa_estudiante(
        db: Session, programa_id: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Confirma/actualiza el programa de un estudiante.

        Args:
            db: Sesión de BD
            programa_id: ID del programa
            usuario: Usuario estudiante

        Returns:
            Dict con resultado
        """
        try:
            if usuario.rol != "estudiante":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo estudiantes pueden confirmar programa",
                )

            # Verificar que el programa exista
            query_programa = text(
                """
                SELECT nombre FROM "Programa"
                WHERE programa_id = :programa_id
            """
            )

            programa = db.execute(
                query_programa, {"programa_id": programa_id}
            ).fetchone()

            if not programa:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Programa no encontrado",
                )

            # Actualizar programa del estudiante
            update_query = text(
                """
                UPDATE "Usuario"
                SET programa_id = :programa_id
                WHERE usuario_id = :usuario_id
            """
            )

            db.execute(
                update_query,
                {"programa_id": programa_id, "usuario_id": usuario.usuario_id},
            )
            db.commit()

            logger.info(
                f"Estudiante {usuario.usuario_id} confirmó programa {programa_id}"
            )

            return {
                "success": True,
                "message": f"Programa '{programa[0]}' confirmado exitosamente",
                "data": {"programa_id": programa_id, "programa_nombre": programa[0]},
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error confirmando programa: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al confirmar programa",
            ) from e

    @staticmethod
    def obtener_programas_disponibles(
        db: Session, usuario: Usuario, institucion_id: str | None = None
    ) -> dict[str, Any]:
        """Obtiene programas disponibles de la institución.

        Args:
            db: Sesión de BD
            usuario: Usuario actual
            institucion_id: ID opcional de institución

        Returns:
            Dict con lista de programas
        """
        try:
            # Si no se especifica institución, usar la del usuario
            if not institucion_id:
                query_inst = text(
                    """
                    SELECT institucion_id FROM "Usuario"
                    WHERE usuario_id = :usuario_id
                """
                )

                result = db.execute(
                    query_inst, {"usuario_id": usuario.usuario_id}
                ).fetchone()
                institucion_id = str(result[0]) if result and result[0] else None

            if not institucion_id:
                return {
                    "success": True,
                    "data": [],
                    "message": "No tienes institución asignada",
                }

            # Obtener programas
            query = text(
                """
                SELECT
                    p.programa_id,
                    p.nombre,
                    p.descripcion,
                    p.duracion,
                    COUNT(DISTINCT u.usuario_id) as total_estudiantes
                FROM "Programa" p
                LEFT JOIN "Usuario" u ON p.programa_id = u.programa_id
                WHERE p.institucion_id = :institucion_id
                    AND p.activo = true
                GROUP BY p.programa_id, p.nombre, p.descripcion, p.duracion
                ORDER BY p.nombre
            """
            )

            result = db.execute(query, {"institucion_id": institucion_id}).fetchall()
            programas = [dict(row._mapping) for row in result]

            return {
                "success": True,
                "data": programas,
                "total": len(programas),
                "message": "Programas obtenidos exitosamente",
            }

        except Exception as e:
            logger.exception(f"Error obteniendo programas: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al obtener programas",
            ) from e


# ==================== Instancias Singleton ====================

# Servicio moderno de inscripciones académicas
inscripcion_academica_service = InscripcionAcademicaService()

# Servicio legacy de inscripciones por código (mantener compatibilidad)
inscripcion_service = InscripcionService()
