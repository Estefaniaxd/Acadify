from ...db.base_class import Base
from sqlalchemy import Column, text, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID, ENUM, BOOLEAN, TIMESTAMP
from ...enums.academic.institucion_enums import (
    TipoInstitucion,
    NivelEducativoInstitucion,
    SectorInstitucion,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Institucion(Base):
    __tablename__ = "Institucion"

    institucion_id = Column(
    UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')
    )
    administrador_id_creador = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="SET NULL"),
    )

    nombre = Column(String(150), unique=True, nullable=False)
    sigla = Column(String(20), unique=True)
    lema = Column(String(255))

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

    direccion = Column(String(255))
    ciudad = Column(String(100))
    pais = Column(String(100), nullable=False)

    correo_institucional = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(30), nullable=False)
    nit = Column(String(20), unique=True)

    # Campos de estado y fechas
    estado = Column(
        ENUM(
            "pendiente",
            "activa", 
            "suspendida", 
            "inactiva", 
            name="estado_institucion"
        ),
        nullable=False,
        server_default="pendiente"
    )
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    fecha_activacion = Column(TIMESTAMP(timezone=True), nullable=True)

    escalas = relationship(
        "EscalaCalificacion", backref="institucion", passive_deletes=True
    )
    programas = relationship("Programa", backref="institucion")

    institucion_coordinadores = relationship(
        "InstitucionCoordinador", back_populates="institucion"
    )
