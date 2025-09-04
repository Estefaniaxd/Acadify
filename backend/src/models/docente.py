import uuid
from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Date, Enum, SmallInteger, ForeignKey
from src.enums.docente_enums import TipoVinculacionDocente
from sqlalchemy.orm import relationship 


class Docente(Base):
    __tablename__ = "Docente"

    docente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id"),
        primary_key=True,
        default=uuid.uuid4,
    )
    area_conocimiento = Column(String(50), nullable=False)
    fecha_vinculacion = Column(Date, nullable=False)
    tipo_vinculacion = Column(
        Enum(TipoVinculacionDocente, name="tipo_vinculacion_institucion"),
        nullable=False,
        default=TipoVinculacionDocente.planta,
    )
    titulo_academico = Column(String(50), nullable=True)
    horas_semanales = Column(SmallInteger, nullable=True)
    
    usuario = relationship("Usuario", back_populates="docente")
