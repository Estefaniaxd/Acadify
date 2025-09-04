import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.base_class import Base
from src.enums.institucion_enums import TipoInstitucion, NivelEducativoInstitucion, SectorInstitucion

class Institucion(Base):
    __tablename__ = "Institucion"

    institucion_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    administrador_id = Column(UUID(as_uuid=True), ForeignKey("AdministradorSistema.administrador_id", ondelete="SET NULL"))

    nombre = Column(String(150), unique=True, nullable=False)
    sigla = Column(String(20), unique=True, nullable=True)
    lema = Column(String(255), nullable=True)

    tipo_institucion = Column(Enum(TipoInstitucion, name="tipo_institucion"), nullable=False)
    usa_programas = Column(Boolean, nullable=False)
    nivel_educativo = Column(Enum(NivelEducativoInstitucion, name="nivel_educativo_institucion"), nullable=False)
    sector = Column(Enum(SectorInstitucion, name="sector_institucion"), nullable=False)

    direccion = Column(String(255), nullable=True)
    ciudad = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=False)

    correo_institucional = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20), unique=True, nullable=False)
    nit = Column(String(20), unique=True, nullable=True)

    administrador = relationship("AdministradorSistema", back_populates="instituciones")
    coordinadores = relationship("Coordinador", back_populates="institucion", cascade="all, delete-orphan")
    programas = relationship("Programa", back_populates="institucion", cascade="all, delete")