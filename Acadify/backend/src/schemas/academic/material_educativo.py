from pydantic import BaseModel, Field, validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from ...enums.academic.material_educativo_enums import TipoMaterialEducativo, CarpetaMaterial, EstadoMaterial


class MaterialEducativoBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=150)
    descripcion: Optional[str] = None
    tipo_material: TipoMaterialEducativo
    carpeta: CarpetaMaterial = CarpetaMaterial.otros
    url_archivo: str = Field(..., max_length=500)
    formato_archivo: str = Field(..., max_length=20)
    tags: Optional[str] = Field(None, max_length=500)


class MaterialEducativoCreate(MaterialEducativoBase):
    autor_id: Optional[UUID] = None
    tamano_archivo: Optional[int] = None
    hash_archivo: Optional[str] = None


class MaterialEducativoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=150)
    descripcion: Optional[str] = None
    tipo_material: Optional[TipoMaterialEducativo] = None
    carpeta: Optional[CarpetaMaterial] = None
    estado: Optional[EstadoMaterial] = None
    url_archivo: Optional[str] = Field(None, max_length=500)
    formato_archivo: Optional[str] = Field(None, max_length=20)
    tags: Optional[str] = Field(None, max_length=500)


class MaterialEducativoSubirVersion(BaseModel):
    url_archivo: str = Field(..., max_length=500)
    formato_archivo: str = Field(..., max_length=20)
    tamano_archivo: Optional[int] = None
    hash_archivo: Optional[str] = None
    descripcion_cambios: Optional[str] = None


class MaterialEducativoInDBBase(MaterialEducativoBase):
    material_id: UUID
    version: int
    material_original_id: Optional[UUID]
    es_version_actual: bool
    autor_id: Optional[UUID]
    tamano_archivo: Optional[int]
    hash_archivo: Optional[str]
    estado: EstadoMaterial
    numero_descargas: int
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    fecha_ultimo_acceso: Optional[datetime]

    class Config:
        from_attributes = True


class MaterialEducativo(MaterialEducativoInDBBase):
    pass


class MaterialEducativoDetallado(MaterialEducativoInDBBase):
    # Información del autor
    autor_nombre: Optional[str] = None
    autor_apellido: Optional[str] = None
    # Información adicional
    tamano_legible: str = "Desconocido"
    total_versiones: int = 1

    class Config:
        from_attributes = True


class MaterialEducativoConVersiones(MaterialEducativoInDBBase):
    versiones_anteriores: List['MaterialEducativo'] = []

    class Config:
        from_attributes = True


class FiltrosMaterial(BaseModel):
    carpeta: Optional[CarpetaMaterial] = None
    tipo_material: Optional[TipoMaterialEducativo] = None
    estado: Optional[EstadoMaterial] = EstadoMaterial.activo
    autor_id: Optional[UUID] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    busqueda: Optional[str] = None


class EstadisticasMaterial(BaseModel):
    total_materiales: int
    por_carpeta: dict
    por_tipo: dict
    total_descargas: int
    material_mas_popular: Optional[MaterialEducativo]

    class Config:
        from_attributes = True


# Google Drive Integration
class ConfiguracionGoogleDrive(BaseModel):
    habilitar_sync: bool = False
    carpeta_base_id: Optional[str] = None
    auto_sync: bool = False


class SincronizacionDrive(BaseModel):
    material_id: UUID
    google_drive_id: Optional[str] = None
    google_drive_url: Optional[str] = None
