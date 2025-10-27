from ...db.base_class import Base
from sqlalchemy import Column, text, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from ...enums.academic.grupo_enums import JornadaGrupo
from sqlalchemy.orm import relationship

class Grupo(Base):
    __tablename__ = "Grupo"

    grupo_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
    server_default=text('gen_random_uuid()'),
    )

    programa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Programa.programa_id", ondelete="CASCADE"),
        nullable=True,
    )

    docente_tutor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Docente.docente_id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )

    nombre = Column(String(50), nullable=False)
    jornada = Column(
        ENUM(JornadaGrupo, name="jornada_grupo", create_type=False),
        nullable=False,
        default=JornadaGrupo.manana,
        server_default=text("'manana'"),
    )

    estudiante_grupos = relationship("EstudianteGrupo", back_populates="grupo")
    grupo_cursos = relationship("GrupoCurso", back_populates="grupo")
    chat_grupos = relationship("ChatGrupo", backref="grupo")
    tareas = relationship("src.models.academic.tarea.Tarea", back_populates="grupo")
