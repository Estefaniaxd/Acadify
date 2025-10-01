from ...db.base_class import Base
from sqlalchemy import Column, String, text, ForeignKey, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID, TEXT, ENUM, TIMESTAMP, INTEGER, BIGINT
from ...enums.academic.material_educativo_enums import TipoMaterialEducativo, CarpetaMaterial, EstadoMaterial
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class MaterialEducativo(Base):
    __tablename__ = "MaterialEducativo"
    
    __table_args__ = (
        Index("idx_material_carpeta", "carpeta"),
        Index("idx_material_estado", "estado"),
        Index("idx_material_fecha", "fecha_creacion"),
        Index("idx_material_original", "material_original_id"),
    )

    material_id = Column(
        UUID(as_uuid=True), 
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )
    
    # Información básica
    titulo = Column(String(150), nullable=False)
    descripcion = Column(TEXT)
    tipo_material = Column(
        ENUM(TipoMaterialEducativo, name="tipo_material_educativo", create_type=False),
        nullable=False,
    )
    
    # Organización
    carpeta = Column(
        ENUM(CarpetaMaterial, name="carpeta_material", create_type=False),
        nullable=False,
        default=CarpetaMaterial.otros,
    )
    
    estado = Column(
        ENUM(EstadoMaterial, name="estado_material", create_type=False),
        nullable=False,
        default=EstadoMaterial.activo,
        server_default=text("'activo'"),
    )
    
    # Archivo
    url_archivo = Column(String(500), nullable=False)
    formato_archivo = Column(String(20), nullable=False)
    tamano_archivo = Column(BIGINT)  # En bytes
    hash_archivo = Column(String(64))  # SHA-256 para detectar duplicados
    
    # Versionamiento
    version = Column(INTEGER, nullable=False, default=1)
    material_original_id = Column(
        UUID(as_uuid=True),
        ForeignKey("MaterialEducativo.material_id", ondelete="SET NULL"),
        nullable=True,
    )
    es_version_actual = Column(Boolean, default=True, nullable=False)
    
    # Metadatos adicionales
    autor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="SET NULL"),
    )
    tags = Column(String(500))  # Tags separados por comas
    
    # Google Drive Integration (opcional)
    google_drive_id = Column(String(50))
    google_drive_url = Column(String(500))
    sincronizado_drive = Column(Boolean, default=False)
    fecha_ultima_sync = Column(TIMESTAMP(timezone=True))
    
    # Estadísticas
    numero_descargas = Column(INTEGER, default=0)
    fecha_ultimo_acceso = Column(TIMESTAMP(timezone=True))
    
    # Auditoría
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # Relaciones
    material_clases = relationship("MaterialClase", backref="material_educativo", cascade="all, delete-orphan")
    material_cursos = relationship("MaterialCurso", backref="material_educativo", cascade="all, delete-orphan")
    autor = relationship("Usuario", backref="materiales_creados")
    
    # Versioning relationships
    versiones_anteriores = relationship(
        "MaterialEducativo",
        backref="version_actual",
        remote_side=[material_id],
        single_parent=True
    )

    @property
    def tamano_legible(self) -> str:
        """Convierte el tamaño en bytes a formato legible"""
        if not self.tamano_archivo:
            return "Desconocido"
        
        for unidad in ['B', 'KB', 'MB', 'GB']:
            if self.tamano_archivo < 1024.0:
                return f"{self.tamano_archivo:.1f} {unidad}"
            self.tamano_archivo /= 1024.0
        return f"{self.tamano_archivo:.1f} TB"