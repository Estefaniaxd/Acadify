from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, ENUM, BOOLEAN
from sqlalchemy import Column, String, ForeignKey
from src.enums.institucion_enums import (
    TipoInstitucion,
    NivelEducativoInstitucion,
    SectorInstitucion,
)
from sqlalchemy.orm import relationship


class Institucion(Base):
    __tablename__ = "Institucion"

    institucion_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()"
    )
    administrador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("administrador_sistema.administrador_id", ondelete="SET NULL"),
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
    telefono = Column(String(20), unique=True, nullable=False)
    nit = Column(String(20), unique=True)

    administrador = relationship(
        "administrador_sistema", back_populates="institucion", passive_deletes=True
    )
    coordinadores = relationship(
        "coordinador", back_populates="institucion", passive_deletes=True
    )
    programas = relationship(
        "programa", back_populates="institucion", passive_deletes=True
    )
