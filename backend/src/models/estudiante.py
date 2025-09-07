from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, ENUM, DATE, SMALLINT
from sqlalchemy import Column, ForeignKey, DECIMAL
from src.enums.estudiante_enums import EtapaFormativaEstudiante
from sqlalchemy.orm import relationship


class Estudiante(Base):
    __tablename__ = "Estudiante"

    estudiante_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.usuario_id", ondelete="CASCADE"),
        primary_key=True,
    )

    programa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("programa.programa_id", ondelete="SET NULL"),
    )

    fecha_ingreso = Column(DATE, nullable=False)
    creditos_aprobados = Column(SMALLINT)
    etapa_formativa = Column(
        ENUM(
            EtapaFormativaEstudiante,
            name="etapa_formativa_estudiante",
            create_type=False,
        ),
        nullable=False,
        default=EtapaFormativaEstudiante.i,
    )
    promedio_acumulado = Column(DECIMAL(3, 2))

    usuario = relationship("usuario", back_populates="estudiante", passive_deletes=True)
    programa = relationship(
        "programa", back_populates="estudiante", passive_deletes=True
    )
