from src.db.base_class import Base
from sqlalchemy import Column, text, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, TEXT, BOOLEAN
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Tarea(Base):
    __tablename__ = "Tarea"

    tarea_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_default()"))
    docente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Docente.docente_id", ondelete="SET NULL"),
        nullable=True,
    )
    clase_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Clase.clase_id", ondelete="CASCADE"),
        nullable=False,
    )
    titulo = Column(String(50), nullable=False)
    descripcion = Column(TEXT)
    fecha_asignacion = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    fecha_limite = Column(TIMESTAMP(timezone=True))
    archivo_adjunto = Column(TEXT)
    permite_entregas_tardias = Column(BOOLEAN, nullable=False)
    
    entrega_tareas = relationship("EntregarTarea", backref="tarea", passive_deletes=True)
