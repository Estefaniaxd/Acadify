from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, INTERVAL, TEXT
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func


class Clase(Base):
    __tablename__ = "Clase"

    clase_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()"
    )
    grupo_curso_id = Column(
        UUID(as_uuid=True),
        ForeignKey("grupo_curso.grupo_curso_id", ondelete="CASCADE"),
        nullable=False,
    )
    plataforma_id = Column(
        UUID(as_uuid=True), ForeignKey("plataforma.grupo_curso_id", ondelete="SET NULL")
    )
    titulo = Column(TEXT, nullable=False)
    descripcion = Column(TEXT)
    hora_inicio = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    duracion = Column(INTERVAL(), nullable=False)
    link_videollamada = Column(TEXT)
