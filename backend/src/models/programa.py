from sqlalchemy import Column, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from src.db.base_class import Base
from src.enums.programa_enums import NivelPrograma, TipoPrograma


class Programa(Base):
    __tablename__ = "Programa"

    programa_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Institucion.institucion_id", ondelete="CASCADE"),
        nullable=False,
    )
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    nivel = Column(
        ENUM(NivelPrograma, name="nivel_programa", create_type=False),
        nullable=False,
    )
    tipo = Column(
        ENUM(TipoPrograma, name="tipo_programa", create_type=False),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("institucion_id", "nombre", name="uq_programa_nombre"),
    )

    institucion = relationship("Institucion", back_populates="programas")
    estudiantes = relationship("Estudiante", back_populates="programa", cascade="all, delete")