from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime
from ...enums.academic.institucion_enums import (
    TipoInstitucion,
    NivelEducativoInstitucion,
    SectorInstitucion,
    ModalidadEnsenanza,
    TipoCalendario,
)
import re


class InstitucionBase(BaseModel):
    """
    Schema base para Institución con todos los campos nuevos.
    Aplica principio de Open/Closed: abierto para extensión, cerrado para modificación.
    """
    # ============================================
    # IDENTIFICACIÓN BÁSICA
    # ============================================
    nombre: str = Field(..., min_length=3, max_length=150)
    sigla: Optional[str] = Field(None, max_length=20)
    lema: Optional[str] = Field(None, max_length=255)

    # ============================================
    # IDENTIDAD VISUAL
    # ============================================
    logo_url: Optional[str] = Field(
        None,
        min_length=10,
        max_length=500,
        description="URL del logo institucional (Opcional - se asigna default si no se proporciona)"
    )
    color_primario: Optional[str] = Field(
        None, 
        pattern=r'^#[0-9A-Fa-f]{6}$',
        description="Color primario en formato hexadecimal #RRGGBB"
    )
    color_secundario: Optional[str] = Field(
        None,
        pattern=r'^#[0-9A-Fa-f]{6}$',
        description="Color secundario en formato hexadecimal #RRGGBB"
    )

    # ============================================
    # CLASIFICACIÓN ACADÉMICA
    # ============================================
    tipo_institucion: TipoInstitucion
    usa_programas: bool = Field(
        ...,
        description="TRUE: Universidad/Instituto con programas. FALSE: Colegio sin programas"
    )
    nivel_educativo: NivelEducativoInstitucion
    sector: SectorInstitucion
    modalidad_ensenanza: ModalidadEnsenanza = Field(
        default=ModalidadEnsenanza.presencial,
        description="Modalidad: presencial, virtual, híbrida o dual"
    )

    # ============================================
    # CALENDARIO Y ORGANIZACIÓN TEMPORAL
    # ============================================
    tipo_calendario: Optional[TipoCalendario] = Field(
        None,
        description="Tipo de calendario académico"
    )
    jornadas: Optional[List[str]] = Field(
        None,
        description='Jornadas disponibles: ["mañana", "tarde", "noche", "fines_de_semana"]'
    )

    # ============================================
    # UBICACIÓN
    # ============================================
    direccion: Optional[str] = Field(None, max_length=255)
    ciudad: Optional[str] = Field(None, max_length=100)
    pais: str = Field(..., min_length=2, max_length=100)

    # ============================================
    # CONTACTO Y DOMINIOS
    # ============================================
    correo_institucional: EmailStr = Field(
        ...,
        description="Correo principal para contacto y envío de invitaciones"
    )
    telefono: str = Field(..., min_length=7, max_length=30)
    nit: Optional[str] = Field(None, max_length=20)
    
    dominio_principal: Optional[str] = Field(
        None,
        max_length=100,
        description="Dominio principal sin @ (ej: arp.edu.co) para registro automático"
    )
    dominios_adicionales: Optional[List[str]] = Field(
        None,
        description="Dominios secundarios para registro automático"
    )

    # ============================================
    # PRESENCIA DIGITAL
    # ============================================
    website: Optional[str] = Field(None, max_length=255)
    redes_sociales: Optional[Dict[str, str]] = Field(
        None,
        description='Links a redes sociales: {"facebook": "url", "instagram": "url"}'
    )

    # ============================================
    # ACREDITACIÓN Y CERTIFICACIÓN
    # ============================================
    acreditacion_nacional: Optional[str] = Field(None, max_length=150)
    acreditacion_internacional: Optional[str] = Field(None, max_length=150)
    fecha_acreditacion: Optional[datetime] = None

    # ============================================
    # CAPACIDAD Y ESTADÍSTICAS
    # ============================================
    capacidad_estudiantes: Optional[int] = Field(None, ge=0)
    numero_estudiantes_actual: Optional[int] = Field(0, ge=0)
    numero_docentes: Optional[int] = Field(0, ge=0)
    numero_programas_activos: Optional[int] = Field(0, ge=0)

    # ============================================
    # CONFIGURACIÓN REGIONAL
    # ============================================
    configuracion_regional: Optional[Dict[str, Any]] = Field(
        None,
        description='Configuración: {"idioma": "es", "zona_horaria": "America/Bogota"}'
    )

    # ============================================
    # CAMPOS PERSONALIZADOS (evitamos 'metadata' - reservado)
    # ============================================
    campos_personalizados: Optional[Dict[str, Any]] = Field(
        None,
        description="Campos personalizados específicos de la institución"
    )

    @field_validator('jornadas')
    @classmethod
    def validar_jornadas(cls, v):
        """Valida que las jornadas sean válidas"""
        if v is None:
            return v
        
        jornadas_validas = {'mañana', 'tarde', 'noche', 'fines_de_semana', 'completa'}
        for jornada in v:
            if jornada.lower() not in jornadas_validas:
                raise ValueError(f"Jornada '{jornada}' no válida. Opciones: {jornadas_validas}")
        return v

    @field_validator('dominio_principal', 'dominios_adicionales')
    @classmethod
    def validar_dominios(cls, v, info):
        """Valida que los dominios no contengan @ y tengan formato correcto"""
        if v is None:
            return v
        
        # Si es un string (dominio_principal)
        if isinstance(v, str):
            if '@' in v:
                raise ValueError("El dominio no debe contener '@'. Usar solo: arp.edu.co")
            if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', v):
                raise ValueError(f"Formato de dominio inválido: {v}")
            return v.lower()
        
        # Si es una lista (dominios_adicionales)
        if isinstance(v, list):
            dominios_limpios = []
            for dominio in v:
                if '@' in dominio:
                    raise ValueError(f"El dominio '{dominio}' no debe contener '@'")
                if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', dominio):
                    raise ValueError(f"Formato de dominio inválido: {dominio}")
                dominios_limpios.append(dominio.lower())
            return dominios_limpios
        
        return v


class InstitucionCreate(InstitucionBase):
    """
    Schema para crear una institución.
    El logo_url es opcional - se asignará un logo por defecto si no se proporciona.
    El coordinador puede actualizarlo después en el proceso de onboarding.
    """
    administrador_id_creador: Optional[UUID] = None


class InstitucionUpdate(BaseModel):
    """
    Schema para actualizar una institución.
    Todos los campos son opcionales (principio de flexibilidad).
    """
    nombre: Optional[str] = Field(None, min_length=3, max_length=150)
    sigla: Optional[str] = Field(None, max_length=20)
    lema: Optional[str] = Field(None, max_length=255)
    
    logo_url: Optional[str] = Field(None, min_length=10, max_length=500)
    color_primario: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    color_secundario: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    
    tipo_institucion: Optional[TipoInstitucion] = None
    usa_programas: Optional[bool] = None
    nivel_educativo: Optional[NivelEducativoInstitucion] = None
    sector: Optional[SectorInstitucion] = None
    modalidad_ensenanza: Optional[ModalidadEnsenanza] = None
    
    tipo_calendario: Optional[TipoCalendario] = None
    jornadas: Optional[List[str]] = None
    
    direccion: Optional[str] = Field(None, max_length=255)
    ciudad: Optional[str] = Field(None, max_length=100)
    pais: Optional[str] = Field(None, min_length=2, max_length=100)
    
    correo_institucional: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, min_length=7, max_length=30)
    nit: Optional[str] = Field(None, max_length=20)
    
    dominio_principal: Optional[str] = Field(None, max_length=100)
    dominios_adicionales: Optional[List[str]] = None
    
    website: Optional[str] = Field(None, max_length=255)
    redes_sociales: Optional[Dict[str, str]] = None
    
    acreditacion_nacional: Optional[str] = Field(None, max_length=150)
    acreditacion_internacional: Optional[str] = Field(None, max_length=150)
    fecha_acreditacion: Optional[datetime] = None
    
    capacidad_estudiantes: Optional[int] = Field(None, ge=0)
    numero_estudiantes_actual: Optional[int] = Field(None, ge=0)
    numero_docentes: Optional[int] = Field(None, ge=0)
    numero_programas_activos: Optional[int] = Field(None, ge=0)
    
    configuracion_regional: Optional[Dict[str, Any]] = None
    campos_personalizados: Optional[Dict[str, Any]] = None

    @field_validator('jornadas')
    @classmethod
    def validar_jornadas(cls, v):
        if v is None:
            return v
        jornadas_validas = {'mañana', 'tarde', 'noche', 'fines_de_semana', 'completa'}
        for jornada in v:
            if jornada.lower() not in jornadas_validas:
                raise ValueError(f"Jornada '{jornada}' no válida. Opciones: {jornadas_validas}")
        return v

    @field_validator('dominio_principal', 'dominios_adicionales')
    @classmethod
    def validar_dominios(cls, v, info):
        if v is None:
            return v
        
        if isinstance(v, str):
            if '@' in v:
                raise ValueError("El dominio no debe contener '@'")
            if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', v):
                raise ValueError(f"Formato de dominio inválido: {v}")
            return v.lower()
        
        if isinstance(v, list):
            dominios_limpios = []
            for dominio in v:
                if '@' in dominio:
                    raise ValueError(f"El dominio '{dominio}' no debe contener '@'")
                if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', dominio):
                    raise ValueError(f"Formato de dominio inválido: {dominio}")
                dominios_limpios.append(dominio.lower())
            return dominios_limpios
        
        return v


class InstitucionInDBBase(InstitucionBase):
    """
    Schema base para institución en base de datos.
    Incluye campos de estado y timestamps.
    """
    institucion_id: UUID
    administrador_id_creador: Optional[UUID] = None
    estado: str  # pendiente, activa, suspendida, inactiva
    fecha_creacion: datetime
    fecha_activacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class Institucion(InstitucionInDBBase):
    """
    Schema completo de respuesta con toda la información de la institución.
    """
    pass


class InstitucionResponse(BaseModel):
    """
    Schema simplificado para listados y respuestas rápidas.
    Solo información esencial (Principio de Responsabilidad Única).
    """
    institucion_id: UUID
    nombre: str
    sigla: Optional[str] = None
    logo_url: str
    tipo_institucion: TipoInstitucion
    nivel_educativo: NivelEducativoInstitucion
    modalidad_ensenanza: ModalidadEnsenanza
    ciudad: Optional[str] = None
    pais: str
    estado: str
    numero_estudiantes_actual: Optional[int] = 0
    numero_docentes: Optional[int] = 0

    class Config:
        from_attributes = True
