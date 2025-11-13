from sqlalchemy import Column, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import ARRAY, BOOLEAN, ENUM, JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base
from src.enums.academic.institucion_enums import (
    NivelEducativoInstitucion,
    SectorInstitucion,
    TipoInstitucion,
)


class Institucion(Base):
    """Modelo de Institución Educativa.

    Representa una institución educativa completa con:
    - Información básica y contacto
    - Configuración académica
    - Personalización visual (logo, colores)
    - Acreditaciones y capacidades
    - Dominios y redes sociales
    """

    __tablename__ = "Institucion"

    # ============================================
    # IDENTIFICACIÓN Y ADMINISTRACIÓN
    # ============================================
    institucion_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    administrador_id_creador = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="SET NULL"),
    )

    # ============================================
    # INFORMACIÓN BÁSICA
    # ============================================
    nombre = Column(String(150), unique=True, nullable=False)
    sigla = Column(String(20), unique=True)
    lema = Column(String(255))

    # ============================================
    # CLASIFICACIÓN INSTITUCIONAL
    # ============================================
    tipo_institucion = Column(
        ENUM(TipoInstitucion, name="tipo_institucion", create_type=False),
        nullable=False,
    )
    usa_programas = Column(BOOLEAN, nullable=False)
    nivel_educativo = Column(
        ENUM(
            NivelEducativoInstitucion,
            name="nivel_educativo_institucion",
            create_type=False,
        ),
        nullable=False,
    )
    sector = Column(
        ENUM(SectorInstitucion, name="sector_institucion", create_type=False),
        nullable=False,
    )

    # ============================================
    # UBICACIÓN Y CONTACTO
    # ============================================
    direccion = Column(String(255))
    ciudad = Column(String(100))
    pais = Column(String(100), nullable=False)
    correo_institucional = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(30), nullable=False)
    nit = Column(String(20), unique=True)
    website = Column(String(255), nullable=True)
    redes_sociales = Column(
        JSONB, nullable=True
    )  # {facebook, twitter, instagram, etc.}

    # ============================================
    # PERSONALIZACIÓN VISUAL
    # ============================================
    logo_url = Column(String(500), nullable=False, server_default="")
    color_primario = Column(String(7), nullable=True)  # Formato HEX: #RRGGBB
    color_secundario = Column(String(7), nullable=True)  # Formato HEX: #RRGGBB

    # ============================================
    # CONFIGURACIÓN ACADÉMICA
    # ============================================
    modalidad_ensenanza = Column(
        String(10), nullable=False, server_default="presencial"
    )
    tipo_calendario = Column(String(13), nullable=True)  # semestral, trimestral, etc.
    jornadas = Column(ARRAY(String), nullable=True)  # [mañana, tarde, noche, etc.]

    # ============================================
    # DOMINIOS Y ACCESO
    # ============================================
    dominio_principal = Column(String(100), nullable=True)  # example.edu.co
    dominios_adicionales = Column(ARRAY(String), nullable=True)  # dominios alternativos

    # ============================================
    # ACREDITACIÓN Y CERTIFICACIONES
    # ============================================
    acreditacion_nacional = Column(String(150), nullable=True)
    acreditacion_internacional = Column(String(150), nullable=True)
    fecha_acreditacion = Column(TIMESTAMP(timezone=True), nullable=True)

    # ============================================
    # CAPACIDADES Y ESTADÍSTICAS
    # ============================================
    capacidad_estudiantes = Column(Integer, nullable=True)
    numero_estudiantes_actual = Column(Integer, nullable=True, server_default="0")
    numero_docentes = Column(Integer, nullable=True, server_default="0")
    numero_programas_activos = Column(Integer, nullable=True, server_default="0")

    # ============================================
    # CONFIGURACIÓN AVANZADA
    # ============================================
    configuracion_regional = Column(
        JSONB, nullable=True
    )  # Zona horaria, idioma, moneda
    campos_personalizados = Column(
        JSONB, nullable=True
    )  # Campos custom por institución

    # ============================================
    # ESTADO Y FECHAS
    # ============================================
    estado = Column(
        ENUM(
            "pendiente", "activa", "suspendida", "inactiva", name="estado_institucion"
        ),
        nullable=False,
        server_default="pendiente",
    )
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    fecha_activacion = Column(TIMESTAMP(timezone=True), nullable=True)

    escalas = relationship(
        "EscalaCalificacion", backref="institucion", passive_deletes=True
    )
    programas = relationship("Programa", back_populates="institucion")

    institucion_coordinadores = relationship(
        "InstitucionCoordinador", back_populates="institucion"
    )
