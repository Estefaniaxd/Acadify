from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import BOOLEAN, ENUM, TEXT, UUID

from src.db.base_class import Base
from src.enums.academic.plataforma_enums import TipoIntegracionPlataforma


class Plataforma(Base):
    __tablename__ = "Plataforma"

    plataforma_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    nombre = Column(String(50), nullable=False, unique=True)
    url_base = Column(TEXT, nullable=False)
    tipo_integracion = Column(
        ENUM(
            TipoIntegracionPlataforma,
            name="tipo_integracion_plataforma",
            create_type=False,
        ),
        nullable=False,
    )
    requiere_cuenta = Column(BOOLEAN, nullable=False)
    es_gratuita = Column(BOOLEAN)
