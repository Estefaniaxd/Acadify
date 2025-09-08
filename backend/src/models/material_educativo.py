from src.db.base_class import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID, TEXT, ENUM
from src.enums.material_educativo_enums import TipoMaterialEducativo
from sqlalchemy.orm import relationship


class MaterialEducativo(Base):
    __tablename__ = "MaterialEducativo"

    material_id = Column(UUID(as_uuid=True), primary_key=True)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(TEXT)
    tipo_material = Column(
        ENUM(TipoMaterialEducativo, name="tipo_material_educativo", create_type=False),
        nullable=False,
    )
    url_archivo = Column(String(255), nullable=False)
    formato_archivo = Column(String(10), nullable=False)

    material_clase = relationship("MaterialClase", backref="material_educativo")
    material_curso = relationship("MaterialCurso", backref="material_educativo")
    