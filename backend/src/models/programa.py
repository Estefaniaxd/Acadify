from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, ENUM, TEXT
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from src.enums.programa_enums import NivelPrograma, TipoPrograma
from sqlalchemy.orm import relationship


class Programa(Base):
    __tablename__ = "Programa"

    __table_args__ = (
        UniqueConstraint("institucion_id", "nombre", name="uq_programa_nombre"),
    )

    programa_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("institucion.institucion_id", ondelete="CASCADE"),
        nullable=False,
    )
    nombre = Column(String(100), nullable=False)
    descripcion = Column(TEXT)
    nivel = Column(
        ENUM(NivelPrograma, name="nivel_programa", create_type=False),
        nullable=False,
    )
    tipo = Column(
        ENUM(TipoPrograma, name="tipo_programa", create_type=False),
        nullable=False,
    )

    institucion = relationship(
        "institucion", back_populates="programa", passive_deletes=True
    )
    estudiantes = relationship(
        "estudiante", back_populates="programa", passive_deletes=True
    )
