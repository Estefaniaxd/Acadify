from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy import Column, String, ForeignKey
from src.enums.grupo_enums import JornadaGrupo
from sqlalchemy.orm import relationship


class Grupo(Base):
    __tablename__ = "Grupo"

    grupo_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid",
    )
    programa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("programa.programa_id", ondelete="CASCADE"),
        nullable=False,
    )
    docente_tutor = Column(
        UUID(as_uuid=True),
        ForeignKey("docente.docente_id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )
    nombre = Column(String(50), nullable=False)

    jornada = Column(
        ENUM(JornadaGrupo, name="jornada_grupo", create_type=False),
        nullable=False,
        default=JornadaGrupo.manana,
    )

    programa = relationship("programa", back_populates="grupo", passive_deletes=True)

    estudiantes = relationship(
        "estudiante", back_populates="grupo", passive_deletes=True
    )
