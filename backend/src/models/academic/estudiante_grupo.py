from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import DATE, UUID
from sqlalchemy.orm import relationship

from src.db.base_class import Base


class EstudianteGrupo(Base):
    __tablename__ = "EstudianteGrupo"

    grupo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Grupo.grupo_id", ondelete="CASCADE"),
        primary_key=True,
    )

    estudiante_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Estudiante.estudiante_id", ondelete="CASCADE"),
        primary_key=True,
    )

    fecha_vinculacion = Column(DATE, nullable=False)

    estudiante = relationship("Estudiante", back_populates="estudiante_grupos")
    grupo = relationship("Grupo", back_populates="estudiante_grupos")
