from src.db.base_class import Base
from sqlalchemy import Column, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, INTERVAL, TEXT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Clase(Base):
    __tablename__ = "Clase"

    clase_id = Column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    grupo_curso_id = Column(
        UUID(as_uuid=True),
        ForeignKey("GrupoCurso.grupo_curso_id", ondelete="CASCADE"),
        nullable=False,
    )

    plataforma_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("Plataforma.plataforma_id", ondelete="SET NULL")
    )

    titulo = Column(TEXT, nullable=False)
    descripcion = Column(TEXT)
    hora_inicio = Column(
        TIMESTAMP(timezone=True), nullable=False,
        server_default=func.now()
    )
    duracion = Column(INTERVAL(), nullable=False)
    link_videollamada = Column(TEXT, nullable=False)

    grupo_curso = relationship("GrupoCurso", backref="clases", passive_deletes=True)
    plataforma = relationship("Plataforma", backref="clases", passive_deletes=True)
    asistencias = relationship("Asistencia", backref="clase", passive_deletes=True)