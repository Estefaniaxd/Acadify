from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, ENUM, DATE, TEXT
from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from src.enums.curso_enums import ModalidadCurso


class Curso(Base):
    __tablename__ = "Curso"

    __table_args__ = (
        UniqueConstraint("institucion_id", "nombre", name="uq_programa_nombre"),
    )

    curso_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    institucion_id = Column(
        ForeignKey("institucion.insititucion_id", ondelete="CASCADE"), nullable=False
    )
    coordinador_id = Column(
        ForeignKey("coordinador.coordinador_id", ondelete="SET NULL")
    )
    programa_id = Column(
        ForeignKey("programa.programa_id", ondelete="CASCADE"), nullable=True
    )
    nombre = Column(String(50), nullable=False)
    descripcion = Column(TEXT)
    modalidad = Column(
        ENUM(ModalidadCurso, name="modalidad_curso", create_type=False), nullable=False
    )
    fecha_inicio = Column(DATE)
    fecha_fin = Column(DATE)
