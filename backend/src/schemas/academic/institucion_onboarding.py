"""Schemas específicos para el proceso de onboarding de instituciones.

Estos schemas son utilizados por el coordinador después de aceptar la invitación
para completar y personalizar su institución.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, List


class InstitucionBrandingUpdate(BaseModel):
    """Schema para actualizar branding visual de la institución.
    
    Usado por coordinadores para personalizar colores corporativos y logo.
    """
    logo_url: Optional[str] = Field(
        None,
        min_length=10,
        max_length=500,
        description="URL del logo institucional"
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
    
    class Config:
        json_schema_extra = {
            "example": {
                "logo_url": "https://cdn.example.com/logos/universidad.png",
                "color_primario": "#003366",
                "color_secundario": "#FFD700"
            }
        }


class InstitucionOnboardingComplete(BaseModel):
    """Schema para completar el onboarding inicial de una institución.
    
    Permite al coordinador completar toda la información básica en un solo paso.
    Combina datos de contacto, ubicación, branding y configuración académica.
    """
    # Branding
    logo_url: Optional[str] = Field(None, max_length=500)
    color_primario: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    color_secundario: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    
    # Contacto y ubicación
    direccion: Optional[str] = Field(None, max_length=255)
    ciudad: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=30)
    website: Optional[str] = Field(None, max_length=255)
    
    # Redes sociales
    redes_sociales: Optional[Dict[str, str]] = Field(
        None,
        description='Links a redes: {"facebook": "url", "instagram": "url", "linkedin": "url"}'
    )
    
    # Configuración académica
    jornadas: Optional[List[str]] = Field(
        None,
        description='Jornadas: ["mañana", "tarde", "noche", "fines_de_semana"]'
    )
    
    # Dominios adicionales
    dominios_adicionales: Optional[List[str]] = Field(
        None,
        description="Dominios secundarios para registro automático"
    )
    
    # Configuración regional
    configuracion_regional: Optional[Dict[str, str]] = Field(
        None,
        description='Config: {"idioma": "es", "zona_horaria": "America/Bogota", "moneda": "COP"}'
    )
    
    # Acreditación
    acreditacion_nacional: Optional[str] = Field(None, max_length=150)
    acreditacion_internacional: Optional[str] = Field(None, max_length=150)
    
    class Config:
        json_schema_extra = {
            "example": {
                "logo_url": "https://cdn.example.com/logos/universidad.png",
                "color_primario": "#003366",
                "color_secundario": "#FFD700",
                "direccion": "Calle 123 #45-67",
                "ciudad": "Bogotá",
                "telefono": "+57 1 234 5678",
                "website": "https://www.universidad.edu.co",
                "redes_sociales": {
                    "facebook": "https://facebook.com/universidad",
                    "instagram": "https://instagram.com/universidad",
                    "linkedin": "https://linkedin.com/company/universidad"
                },
                "jornadas": ["mañana", "tarde", "noche"],
                "dominios_adicionales": ["universidad.edu", "univ.edu.co"],
                "configuracion_regional": {
                    "idioma": "es",
                    "zona_horaria": "America/Bogota",
                    "moneda": "COP"
                },
                "acreditacion_nacional": "Acreditación de Alta Calidad - MEN"
            }
        }


class InstitucionDominioAdd(BaseModel):
    """Schema para agregar un dominio adicional a la institución.
    
    Permite configurar dominios secundarios para registro automático de usuarios.
    """
    dominio: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Dominio sin @ (ej: secundaria.edu.co)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "dominio": "secundaria.edu.co"
            }
        }


class InstitucionOnboardingStatus(BaseModel):
    """Schema de respuesta con el estado del onboarding.
    
    Indica qué pasos del onboarding han sido completados.
    """
    onboarding_completo: bool
    pasos_completados: Dict[str, bool]
    pasos_faltantes: List[str]
    porcentaje_completado: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "onboarding_completo": False,
                "pasos_completados": {
                    "informacion_basica": True,
                    "branding": True,
                    "contacto": True,
                    "redes_sociales": False,
                    "dominios": False,
                    "acreditacion": False
                },
                "pasos_faltantes": [
                    "redes_sociales",
                    "dominios",
                    "acreditacion"
                ],
                "porcentaje_completado": 50
            }
        }
