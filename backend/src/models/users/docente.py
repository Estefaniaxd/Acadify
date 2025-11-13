from sqlalchemy import Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import DATE, ENUM, SMALLINT, UUID
from sqlalchemy.orm import relationship

from src.db.base_class import Base
from src.enums.users.docente_enums import TipoVinculacionDocente


class Docente(Base):
    __tablename__ = "Docente"

    docente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        primary_key=True,
    )
    area_conocimiento = Column(String(50), nullable=False)
    fecha_vinculacion = Column(DATE, nullable=False)
    tipo_vinculacion = Column(
        ENUM(
            TipoVinculacionDocente,
            name="tipo_vinculacion_institucion",
            create_type=False,
        ),
        nullable=False,
        default=TipoVinculacionDocente.planta,
        server_default=text("'planta'"),
    )
    titulo_academico = Column(String(50))
    horas_semanales = Column(SMALLINT)

    curso_docentes = relationship("CursoDocente", back_populates="docente")
    grupos = relationship("Grupo", backref="docente")
    # tareas = relationship("src.models.academic.tarea.Tarea", primaryjoin="Docente.docente_id == foreign(src.models.academic.tarea.Tarea.docente_id)", backref="docente")
