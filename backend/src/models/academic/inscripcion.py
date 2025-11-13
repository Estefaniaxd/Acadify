"""Modelo de Inscripción.

Define el registro de un estudiante en una sección/grupo de un curso.
Reemplaza y mejora EstudianteGrupo con workflow completo de estados.

Este es el modelo central del flujo académico:
Institución → Período → Programa → Curso → Sección → Inscripción
"""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base
from src.enums.academic import (
    EstadoInscripcion,
    FormaPago,
    MotivoRechazo,
    MotivoRetiro,
)


class Inscripcion(Base):
    """Inscripción de un estudiante en una sección de curso.

    Representa el proceso completo desde pre-inscripción hasta finalización.
    Incluye estados, pagos, documentos, calificaciones y auditoría completa.

    Universal para:
    - Universidades: Inscripción formal con requisitos
    - SENA: Proceso de ficha y convocatoria
    - Escuelas de idiomas: Matrícula en módulos
    - Colegios: Matrícula anual o por período
    """

    __tablename__ = "inscripciones"

    # ==================== Identificación ====================
    id = Column(Integer, primary_key=True, index=True)

    # Relaciones principales
    estudiante_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False, index=True
    )
    grupo_id = Column(
        UUID(as_uuid=True), ForeignKey("Grupo.grupo_id"), nullable=False, index=True
    )
    periodo_academico_id = Column(
        Integer, ForeignKey("periodos_academicos.id"), nullable=False, index=True
    )
    programa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Programa.programa_id"),
        nullable=True,
        index=True,
    )

    # Código único de inscripción
    codigo_inscripcion = Column(String(50), unique=True, nullable=False, index=True)

    # ==================== Tipo y Estado ====================
    tipo_inscripcion = Column(
        String(50), nullable=False, default="regular"
    )  # TipoInscripcion enum
    estado = Column(
        String(50), nullable=False, default="pre_inscrita", index=True
    )  # EstadoInscripcion enum

    # ==================== Fechas del Proceso ====================
    # Proceso de inscripción
    fecha_solicitud = Column(DateTime, nullable=False, server_default=func.now())
    fecha_preinscripcion = Column(
        DateTime, nullable=True
    )  # ⚠️ Sin guión bajo (sync con BD)
    fecha_inscripcion = Column(DateTime, nullable=True)
    fecha_confirmacion = Column(DateTime, nullable=True)
    fecha_inicio_clases = Column(Date, nullable=True)

    # Finalización
    fecha_finalizacion = Column(DateTime, nullable=True)
    fecha_retiro = Column(DateTime, nullable=True)
    fecha_cancelacion = Column(DateTime, nullable=True)

    # Fechas límite
    fecha_limite_pago = Column(Date, nullable=True)
    fecha_limite_documentos = Column(Date, nullable=True)
    fecha_limite_confirmacion = Column(Date, nullable=True)

    # ==================== Información Académica ====================
    # Carga académica
    creditos_inscritos = Column(Integer, nullable=True, default=0)
    horas_semanales = Column(Integer, nullable=True, default=0)

    # Prioridad y orden
    numero_lista = Column(Integer, nullable=True)  # Número en lista (si aplica)
    prioridad = Column(Integer, nullable=True, default=0)  # Mayor = más prioridad

    # Convalidaciones y homologaciones
    tiene_convalidacion = Column(Boolean, default=False, nullable=False)
    creditos_convalidados = Column(Integer, nullable=True, default=0)
    tiene_homologacion = Column(Boolean, default=False, nullable=False)

    # Requisitos cumplidos
    cumple_prerequisitos = Column(Boolean, default=False, nullable=False)
    prerequisitos_verificados = Column(Boolean, default=False, nullable=False)
    fecha_verificacion_prerequisitos = Column(DateTime, nullable=True)

    # ==================== Información Financiera ====================
    # Costos
    costo_total = Column(Numeric(10, 2), nullable=True, default=0)
    costo_matricula = Column(Numeric(10, 2), nullable=True, default=0)
    costo_curso = Column(Numeric(10, 2), nullable=True, default=0)
    otros_costos = Column(Numeric(10, 2), nullable=True, default=0)
    descuentos = Column(Numeric(10, 2), nullable=True, default=0)
    monto_final = Column(Numeric(10, 2), nullable=True, default=0)

    # Pagos
    forma_pago = Column(String(50), nullable=True)  # FormaPago enum
    esta_pagado = Column(Boolean, default=False, nullable=False)
    fecha_pago = Column(DateTime, nullable=True)
    referencia_pago = Column(String(100), nullable=True)

    # Beca/Financiamiento
    tiene_beca = Column(Boolean, default=False, nullable=False)
    porcentaje_beca = Column(Numeric(5, 2), nullable=True, default=0)
    tipo_beca = Column(String(100), nullable=True)
    tiene_credito = Column(Boolean, default=False, nullable=False)
    entidad_credito = Column(String(200), nullable=True)

    # ==================== Documentación ====================
    documentos_completos = Column(Boolean, default=False, nullable=False)
    documentos_requeridos = Column(
        JSON, nullable=True
    )  # Lista de documentos necesarios
    documentos_entregados = Column(JSON, nullable=True)  # Lista de documentos recibidos
    documentos_pendientes = Column(JSON, nullable=True)  # Lista de documentos faltantes
    fecha_entrega_documentos = Column(DateTime, nullable=True)

    # ==================== Aprobaciones y Validaciones ====================
    requiere_aprobacion = Column(Boolean, default=False, nullable=False)
    esta_aprobada = Column(Boolean, default=False, nullable=False)
    aprobada_por_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=True
    )
    fecha_aprobacion = Column(DateTime, nullable=True)
    comentarios_aprobacion = Column(Text, nullable=True)

    # ==================== Rechazo y Cancelación ====================
    fue_rechazada = Column(Boolean, default=False, nullable=False)
    motivo_rechazo = Column(String(50), nullable=True)  # MotivoRechazo enum
    descripcion_rechazo = Column(Text, nullable=True)
    rechazada_por_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=True
    )
    fecha_rechazo = Column(DateTime, nullable=True)

    # Retiro
    fue_retirada = Column(Boolean, default=False, nullable=False)
    motivo_retiro = Column(String(50), nullable=True)  # MotivoRetiro enum
    descripcion_retiro = Column(Text, nullable=True)
    fue_retiro_voluntario = Column(Boolean, nullable=True)
    permite_reingreso = Column(Boolean, default=True, nullable=False)

    # ==================== Calificaciones y Resultado ====================
    # Nota final
    calificacion_final = Column(Numeric(5, 2), nullable=True)
    calificacion_literal = Column(String(10), nullable=True)  # A, B, C, etc.
    aprobo_curso = Column(Boolean, nullable=True)

    # Asistencia
    porcentaje_asistencia = Column(Numeric(5, 2), nullable=True)
    cumple_asistencia_minima = Column(Boolean, nullable=True)

    # Certificación
    genera_certificado = Column(Boolean, default=True, nullable=False)
    certificado_emitido = Column(Boolean, default=False, nullable=False)
    fecha_emision_certificado = Column(DateTime, nullable=True)
    codigo_certificado = Column(String(100), nullable=True)

    # ==================== Lista de Espera ====================
    en_lista_espera = Column(Boolean, default=False, nullable=False)
    posicion_lista_espera = Column(Integer, nullable=True)
    fecha_entrada_lista_espera = Column(DateTime, nullable=True)
    fecha_salida_lista_espera = Column(DateTime, nullable=True)
    notificado_cupo_disponible = Column(Boolean, default=False, nullable=False)
    fecha_notificacion_cupo = Column(DateTime, nullable=True)

    # ==================== Configuración ====================
    # Permisos especiales
    puede_cancelar = Column(Boolean, default=True, nullable=False)
    puede_retirar = Column(Boolean, default=True, nullable=False)
    permite_ajustes = Column(Boolean, default=True, nullable=False)

    # Alertas y notificaciones
    requiere_atencion = Column(Boolean, default=False, nullable=False)
    motivo_atencion = Column(Text, nullable=True)
    tiene_observaciones = Column(Boolean, default=False, nullable=False)
    observaciones = Column(Text, nullable=True)

    # ==================== Metadata ====================
    metadata_adicional = Column(
        JSON, nullable=True
    )  # Datos específicos por institución
    notas_internas = Column(Text, nullable=True)  # Notas solo para administradores
    historial_cambios = Column(JSON, nullable=True)  # Log de cambios de estado

    # ==================== Auditoría ====================
    creado_por_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=True
    )
    modificado_por_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=True
    )
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_actualizacion = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Soft delete
    activo = Column(Boolean, default=True, nullable=False, index=True)

    # ==================== Relaciones ====================
    estudiante = relationship(
        "Usuario", foreign_keys=[estudiante_id], backref="inscripciones"
    )
    grupo = relationship("Grupo", foreign_keys=[grupo_id], backref="inscripciones")
    periodo_academico = relationship(
        "PeriodoAcademico", foreign_keys=[periodo_academico_id]
    )
    programa = relationship("Programa", foreign_keys=[programa_id])

    aprobada_por = relationship("Usuario", foreign_keys=[aprobada_por_id])
    rechazada_por = relationship("Usuario", foreign_keys=[rechazada_por_id])
    creado_por = relationship("Usuario", foreign_keys=[creado_por_id])
    modificado_por = relationship("Usuario", foreign_keys=[modificado_por_id])

    # ==================== Constraints ====================
    __table_args__ = (
        CheckConstraint(
            "calificacion_final >= 0 AND calificacion_final <= 5",
            name="check_calificacion_rango",
        ),
        CheckConstraint(
            "porcentaje_asistencia >= 0 AND porcentaje_asistencia <= 100",
            name="check_asistencia_rango",
        ),
        CheckConstraint(
            "porcentaje_beca >= 0 AND porcentaje_beca <= 100", name="check_beca_rango"
        ),
        CheckConstraint("creditos_inscritos >= 0", name="check_creditos_positivos"),
        CheckConstraint("monto_final >= 0", name="check_monto_positivo"),
    )

    # ==================== Properties ====================

    @property
    def nombre_completo_estudiante(self) -> str:
        """Nombre completo del estudiante."""
        if self.estudiante:
            return f"{self.estudiante.nombres} {self.estudiante.apellidos}"
        return "Estudiante no disponible"

    @property
    def esta_activa(self) -> bool:
        """Verifica si la inscripción está activa."""
        return self.activo and self.estado in [
            EstadoInscripcion.aprobada,
            EstadoInscripcion.confirmada,
            EstadoInscripcion.activa,
        ]

    @property
    def esta_pendiente(self) -> bool:
        """Verifica si la inscripción está pendiente de algo."""
        return self.estado in [
            EstadoInscripcion.pre_inscrita,
            EstadoInscripcion.pendiente_pago,
            EstadoInscripcion.pendiente_documentos,
            EstadoInscripcion.pendiente_aprobacion,
        ]

    @property
    def puede_asistir_clases(self) -> bool:
        """Verifica si el estudiante puede asistir a clases."""
        return self.esta_activa and self.esta_pagado and self.documentos_completos

    @property
    def tiene_deuda(self) -> bool:
        """Verifica si tiene deuda pendiente."""
        if not self.monto_final or self.monto_final == 0:
            return False
        return not self.esta_pagado

    @property
    def dias_desde_solicitud(self) -> int | None:
        """Días desde la solicitud."""
        if not self.fecha_solicitud:
            return None
        return (datetime.now(UTC) - self.fecha_solicitud).days

    @property
    def esta_vencida(self) -> bool:
        """Verifica si la inscripción está vencida (no confirmó a tiempo)."""
        if self.estado == EstadoInscripcion.expirada:
            return True

        return bool(
            (
                self.fecha_limite_confirmacion
                and datetime.now(UTC).date() > self.fecha_limite_confirmacion
            )
            and self.estado
            in [EstadoInscripcion.pre_inscrita, EstadoInscripcion.aprobada]
        )

    @property
    def progreso_documentos(self) -> dict[str, any]:
        """Calcula progreso de entrega de documentos."""
        if not self.documentos_requeridos:
            return {"total": 0, "entregados": 0, "porcentaje": 100.0}

        total = (
            len(self.documentos_requeridos)
            if isinstance(self.documentos_requeridos, list)
            else 0
        )
        entregados = (
            len(self.documentos_entregados)
            if isinstance(self.documentos_entregados, list)
            else 0
        )

        porcentaje = (entregados / total * 100) if total > 0 else 0

        return {
            "total": total,
            "entregados": entregados,
            "pendientes": total - entregados,
            "porcentaje": round(porcentaje, 2),
        }

    @property
    def info_financiera(self) -> dict[str, any]:
        """Resume información financiera."""
        return {
            "costo_total": float(self.costo_total) if self.costo_total else 0.0,
            "descuentos": float(self.descuentos) if self.descuentos else 0.0,
            "monto_final": float(self.monto_final) if self.monto_final else 0.0,
            "esta_pagado": self.esta_pagado,
            "tiene_beca": self.tiene_beca,
            "porcentaje_beca": (
                float(self.porcentaje_beca) if self.porcentaje_beca else 0.0
            ),
            "forma_pago": self.forma_pago,
        }

    # ==================== Métodos de Negocio ====================

    def pre_inscribir(self) -> None:
        """Marca la inscripción como pre-inscrita."""
        self.estado = EstadoInscripcion.pre_inscrita
        self.fecha_preinscripcion = datetime.now(UTC)

    def aprobar(self, aprobado_por_id: int, comentarios: str | None = None) -> None:
        """Aprueba la inscripción."""
        self.estado = EstadoInscripcion.aprobada
        self.esta_aprobada = True
        self.aprobada_por_id = aprobado_por_id
        self.fecha_aprobacion = datetime.now(UTC)
        if comentarios:
            self.comentarios_aprobacion = comentarios

    def rechazar(
        self, motivo: MotivoRechazo, descripcion: str, rechazado_por_id: int
    ) -> None:
        """Rechaza la inscripción."""
        self.estado = EstadoInscripcion.rechazada
        self.fue_rechazada = True
        self.motivo_rechazo = motivo
        self.descripcion_rechazo = descripcion
        self.rechazada_por_id = rechazado_por_id
        self.fecha_rechazo = datetime.now(UTC)

    def confirmar(self) -> None:
        """Confirma la inscripción (estudiante acepta)."""
        self.estado = EstadoInscripcion.confirmada
        self.fecha_confirmacion = datetime.now(UTC)

    def activar(self) -> None:
        """Activa la inscripción (puede asistir a clases)."""
        self.estado = EstadoInscripcion.activa
        if not self.fecha_inicio_clases:
            self.fecha_inicio_clases = datetime.now(UTC).date()

    def completar(
        self, calificacion: Decimal | None = None, aprobo: bool | None = None
    ) -> None:
        """Completa la inscripción."""
        self.estado = EstadoInscripcion.completada
        self.fecha_finalizacion = datetime.now(UTC)
        if calificacion is not None:
            self.calificacion_final = calificacion
        if aprobo is not None:
            self.aprobo_curso = aprobo

    def retirar(
        self, motivo: MotivoRetiro, descripcion: str, es_voluntario: bool = True
    ) -> None:
        """Retira al estudiante del curso."""
        self.estado = EstadoInscripcion.retirada
        self.fue_retirada = True
        self.motivo_retiro = motivo
        self.descripcion_retiro = descripcion
        self.fue_retiro_voluntario = es_voluntario
        self.fecha_retiro = datetime.now(UTC)

    def cancelar(self, motivo: str) -> None:
        """Cancela la inscripción."""
        self.estado = EstadoInscripcion.cancelada
        self.fecha_cancelacion = datetime.now(UTC)
        if self.notas_internas:
            self.notas_internas += f"\n[CANCELACIÓN] {motivo}"
        else:
            self.notas_internas = f"[CANCELACIÓN] {motivo}"

    def registrar_pago(
        self,
        monto: Decimal,
        referencia: str | None = None,
        forma_pago: FormaPago | None = None,
    ) -> None:
        """Registra el pago de la inscripción."""
        # Validar monto
        if monto <= 0:
            msg = "El monto debe ser mayor a cero"
            raise ValueError(msg)
        
        self.esta_pagado = True
        self.fecha_pago = datetime.now(UTC)
        if referencia:
            self.referencia_pago = referencia
        if forma_pago:
            self.forma_pago = forma_pago

        # Cambiar estado si estaba pendiente de pago
        if self.estado == EstadoInscripcion.pendiente_pago:
            if self.documentos_completos:
                self.estado = EstadoInscripcion.aprobada
            else:
                self.estado = EstadoInscripcion.pendiente_documentos

    def agregar_a_lista_espera(self, posicion: int) -> None:
        """Agrega a lista de espera."""
        self.estado = EstadoInscripcion.en_lista_espera
        self.en_lista_espera = True
        self.posicion_lista_espera = posicion
        self.fecha_entrada_lista_espera = datetime.now(UTC)

    def salir_lista_espera(self) -> None:
        """Sale de lista de espera."""
        self.en_lista_espera = False
        self.fecha_salida_lista_espera = datetime.now(UTC)
        self.estado = EstadoInscripcion.aprobada

    def registrar_cambio_estado(
        self, estado_anterior: str, estado_nuevo: str, usuario_id: int | None
    ) -> None:
        """Registra cambio de estado en el historial.

        Args:
            estado_anterior: Estado anterior
            estado_nuevo: Estado nuevo
            usuario_id: ID del usuario (UUID o int) - se convierte a string para JSON
        """
        # Convertir usuario_id a string si es UUID para serialización JSON
        usuario_id_str = str(usuario_id) if usuario_id else None

        cambio = {
            "fecha": datetime.now(UTC).isoformat(),
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_nuevo,
            "usuario_id": usuario_id_str,
        }

        if not self.historial_cambios:
            self.historial_cambios = []

        if isinstance(self.historial_cambios, list):
            self.historial_cambios.append(cambio)
        else:
            self.historial_cambios = [cambio]

    def __repr__(self) -> str:
        """Representación en string de la inscripción."""
        return (
            f"<Inscripcion(id={self.id}, codigo='{self.codigo_inscripcion}', "
            f"estudiante_id={self.estudiante_id}, estado='{self.estado}')>"
        )
