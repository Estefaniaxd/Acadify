# src/models/estudiante.py
from sqlalchemy import Column, Date, SmallInteger, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from src.db.base_class import Base
from src.enums.estudiante_enums import EtapaFormativaEstudiante


class Estudiante(Base):
    __tablename__ = "Estudiante"

    estudiante_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id"),
        primary_key=True
    )

    programa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Programa.programa_id"),
        nullable=False
    )

    fecha_ingreso = Column(Date, nullable=False)
    creditos_aprobados = Column(SmallInteger, nullable=True)
    etapa_formativa = Column(
        ENUM(EtapaFormativaEstudiante, name="etapa_formativa_estudiante", create_type=False),
        nullable=False,
        default=EtapaFormativaEstudiante.i
    )
    promedio_acumulado = Column(DECIMAL(3, 2), nullable=True)

    usuario = relationship("Usuario", back_populates="estudiante")
    programa = relationship("Programa", back_populates="estudiantes")
