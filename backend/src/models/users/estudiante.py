from ...db.base_class import Base
from sqlalchemy import Column, CheckConstraint, ForeignKey, DECIMAL, text
from sqlalchemy.dialects.postgresql import UUID, ENUM, DATE, SMALLINT
from src.enums.users.estudiante_enums import EtapaFormativaEstudiante
from sqlalchemy.orm import relationship


class Estudiante(Base):
    __tablename__ = "Estudiante"

    __table_args__ = (
        CheckConstraint(
            "0 <= promedio_acumulado <= 9.99", name="check_promedio_acumulado_positivo"
        ),
    )

    estudiante_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        primary_key=True,
    )

    programa_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        ForeignKey("Programa.programa_id", ondelete="SET NULL"),
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
        server_default=text("'i'"),
    )
    promedio_acumulado = Column(DECIMAL(3, 2))

    estudiante_grupos = relationship("EstudianteGrupo", back_populates="estudiante")
    entregas_tareas = relationship(
        "EntregarTarea", backref="estudiante", passive_deletes=True
    )
    asistencias = relationship("Asistencia", backref="estudiante", passive_deletes=True)
