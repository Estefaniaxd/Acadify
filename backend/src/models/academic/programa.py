from src.db.base_class import Base
from sqlalchemy import Column, text, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM, TEXT
from src.enums.academic.programa_enums import NivelPrograma, TipoPrograma
from sqlalchemy.orm import relationship


class Programa(Base):
    __tablename__ = "Programa"

    __table_args__ = (
        UniqueConstraint("institucion_id", "nombre", name="uq_programa_nombre"),
    )

    programa_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Institucion.institucion_id", ondelete="CASCADE"),
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

    estudiantes = relationship("Estudiante", backref="programa", passive_deletes=True)

    grupos = relationship("Grupo", backref="programa")
