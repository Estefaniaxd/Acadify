from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, ENUM, DATE, SMALLINT
from sqlalchemy import Column, String, ForeignKey
from src.enums.docente_enums import TipoVinculacionDocente
from sqlalchemy.orm import relationship


class Docente(Base):
    __tablename__ = "Docente"

    docente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.usuario_id", ondelete="CASCADE"),
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
    )
    titulo_academico = Column(String(50))
    horas_semanales = Column(SMALLINT)

    usuario = relationship("usuario", back_populates="docente", passive_deletes=True)
