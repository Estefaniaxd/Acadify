from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, ENUM, TEXT, BOOLEAN
from sqlalchemy import Column, String
from src.enums.platafroma_enums import TipoIntegracionPlataforma


class Platafroma(Base):
    __tablename__ = "Platafroma"

    plataforma_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()"
    )
    nombre = Column(String(50), nullable=False, unique=True)
    url_base = Column(TEXT, nullable=False)
    tipo_integracion = Column(
        ENUM(TipoIntegracionPlataforma, name="tipo_integracion_plataforma"),
        nullable=False,
    )
    requiere_cuenta = Column(BOOLEAN, nullable=False)
    es_gratuita = Column(BOOLEAN)
