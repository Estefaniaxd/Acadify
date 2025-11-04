from ...db.base_class import Base
from sqlalchemy import Column, text, ForeignKey, String, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM, TIMESTAMP, TEXT, INTEGER
from ...enums.academic.clase_enums import EstadoClase, TipoClase, EstadoCodigoAcceso
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import secrets
import string


class Clase(Base):
    __tablename__ = "Clase"
    
    __table_args__ = (
        Index("idx_clase_docente_grupo", "docente_id", "grupo_id"),
        Index("idx_clase_fecha", "fecha_inicio"),
        Index("idx_clase_codigo_acceso", "codigo_acceso"),
    )

    clase_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )

    grupo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Grupo.grupo_id", ondelete="CASCADE"),
        nullable=False,
    )

    docente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Docente.docente_id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Campos adicionales de organización
    grupo_curso_id = Column(
        UUID(as_uuid=True),
        ForeignKey("GrupoCurso.grupo_curso_id", ondelete="SET NULL"),
        nullable=True,
    )
    
    plataforma_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Plataforma.plataforma_id", ondelete="SET NULL"),
        nullable=True,
    )

    titulo = Column(String(150), nullable=False)
    descripcion = Column(TEXT)
    
    tipo_clase = Column(
        ENUM(TipoClase, name="tipo_clase", create_type=False),
        nullable=False,
        default=TipoClase.teorica,
    )

    estado = Column(
        ENUM(EstadoClase, name="estado_clase", create_type=False),
        nullable=False,
        default=EstadoClase.programada,
        server_default=text("'programada'"),
    )

    # Campos de fecha y horario
    fecha_inicio = Column(TIMESTAMP(timezone=True), nullable=False)
    fecha_fin = Column(TIMESTAMP(timezone=True))
    hora_inicio = Column(TIMESTAMP(timezone=True), nullable=True)
    duracion = Column(INTEGER, nullable=True)  # Duración en minutos
    duracion_estimada = Column(INTEGER)  # En minutos
    
    # Videollamada
    link_videollamada = Column(String(500), nullable=True)

    # Sistema de código de acceso
    codigo_acceso = Column(String(10), unique=True, nullable=False)
    estado_codigo = Column(
        ENUM(EstadoCodigoAcceso, name="estado_codigo_acceso", create_type=False),
        nullable=False,
        default=EstadoCodigoAcceso.activo,
        server_default=text("'activo'"),
    )
    fecha_vencimiento_codigo = Column(TIMESTAMP(timezone=True))
    max_estudiantes = Column(INTEGER)
    
    # Campos de auditoría
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # Relaciones
    grupo = relationship("Grupo", backref="clases")
    docente = relationship("Docente", backref="clases_impartidas")
    material_clases = relationship("MaterialClase", backref="clase", cascade="all, delete-orphan")
    historial_accesos = relationship("HistorialAccesoClase", backref="clase", cascade="all, delete-orphan")

    def generar_codigo_acceso(self) -> str:
        """Genera un código de acceso único para la clase"""
        # Formato: 4 letras + 4 números (ej: MATH2025)
        letras = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(4))
        numeros = ''.join(secrets.choice(string.digits) for _ in range(4))
        return f"{letras}{numeros}"

    def regenerar_codigo_acceso(self) -> str:
        """Regenera el código de acceso"""
        self.codigo_acceso = self.generar_codigo_acceso()
        self.estado_codigo = EstadoCodigoAcceso.activo
        return self.codigo_acceso

    @property
    def codigo_activo(self) -> bool:
        """Verifica si el código de acceso está activo y no ha vencido"""
        if self.estado_codigo != EstadoCodigoAcceso.activo:
            return False
        if self.fecha_vencimiento_codigo and func.now() > self.fecha_vencimiento_codigo:
            return False
        return True


class HistorialAccesoClase(Base):
    __tablename__ = "HistorialAccesoClase"
    
    __table_args__ = (
        Index("idx_historial_clase_estudiante", "clase_id", "estudiante_id"),
        Index("idx_historial_fecha_acceso", "fecha_acceso"),
    )

    historial_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )

    clase_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Clase.clase_id", ondelete="CASCADE"),
        nullable=False,
    )

    estudiante_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Estudiante.estudiante_id", ondelete="CASCADE"),
        nullable=False,
    )

    fecha_acceso = Column(TIMESTAMP(timezone=True), server_default=func.now())
    codigo_usado = Column(String(10), nullable=False)
    ip_acceso = Column(String(45))  # Soporta IPv4 e IPv6
    user_agent = Column(String(500))

    # Relaciones
    estudiante = relationship("Estudiante", backref="historial_accesos_clases")