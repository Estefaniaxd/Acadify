# src/schemas/communication/comentario.py

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID

from src.models.communication.comentario import TipoComentario


# ==================== SCHEMAS BASE ====================

class ComentarioBase(BaseModel):
    """Schema base para comentario"""
    contenido: str = Field(..., min_length=1, max_length=5000, description="Contenido del comentario")
    tipo: TipoComentario = Field(default=TipoComentario.comentario, description="Tipo de comentario")
    archivos_adjuntos: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de archivos adjuntos")

    @validator('contenido')
    def validar_contenido(cls, v):
        if not v or not v.strip():
            raise ValueError('El contenido no puede estar vacío')
        return v.strip()


# ==================== SCHEMAS DE CREACIÓN ====================

class ComentarioCreate(ComentarioBase):
    """Schema para crear comentario"""
    curso_id: UUID = Field(..., description="ID del curso")
    comentario_padre_id: Optional[UUID] = Field(None, description="ID del comentario padre para respuestas")

    @validator('tipo')
    def validar_tipo_creacion(cls, v, values):
        # Si es una respuesta, debe ser de tipo respuesta
        if values.get('comentario_padre_id') and v != TipoComentario.respuesta:
            return TipoComentario.respuesta
        return v


class ComentarioUpdate(BaseModel):
    """Schema para actualizar comentario"""
    contenido: Optional[str] = Field(None, min_length=1, max_length=5000)
    archivos_adjuntos: Optional[List[Dict[str, Any]]] = None

    @validator('contenido')
    def validar_contenido_update(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('El contenido no puede estar vacío')
        return v.strip() if v else v


# ==================== SCHEMAS DE RESPUESTA ====================

class ComentarioAutor(BaseModel):
    """Schema para información del autor del comentario"""
    usuario_id: UUID
    nombre: str
    apellido: str
    email: str
    
    class Config:
        from_attributes = True


class ComentarioRespuesta(BaseModel):
    """Schema para respuestas de comentarios"""
    comentario_id: UUID
    contenido: str
    autor: ComentarioAutor
    fecha_creacion: datetime
    editado: bool
    archivos_adjuntos: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class ComentarioResponse(ComentarioBase):
    """Schema de respuesta para comentario"""
    comentario_id: UUID
    curso_id: UUID
    autor: ComentarioAutor
    comentario_padre_id: Optional[UUID] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    editado: bool
    activo: bool
    
    # Campos computados
    respuestas: Optional[List[ComentarioRespuesta]] = None
    total_respuestas: Optional[int] = None

    class Config:
        from_attributes = True

    @validator('respuestas', pre=True, always=True)
    def set_respuestas(cls, v):
        return v or []

    @validator('total_respuestas', pre=True, always=True)
    def set_total_respuestas(cls, v, values):
        if v is not None:
            return v
        respuestas = values.get('respuestas', [])
        return len(respuestas) if respuestas else 0


class ComentarioDetallado(ComentarioResponse):
    """Schema detallado con información adicional"""
    fecha_eliminacion: Optional[datetime] = None
    esta_eliminado: bool
    
    # Metadatos adicionales
    es_autor: Optional[bool] = None  # Si el usuario actual es el autor
    puede_editar: Optional[bool] = None  # Si el usuario actual puede editar
    puede_eliminar: Optional[bool] = None  # Si el usuario actual puede eliminar


# ==================== SCHEMAS DE LISTADO ====================

class ComentariosList(BaseModel):
    """Schema para listado paginado de comentarios"""
    comentarios: List[ComentarioResponse]
    total: int
    pagina: int
    limite: int
    tiene_siguiente: bool
    tiene_anterior: bool


class ComentariosResumen(BaseModel):
    """Schema para resumen de comentarios de un curso"""
    total_comentarios: int
    total_anuncios: int
    total_preguntas: int
    total_respuestas: int
    preguntas_sin_respuesta: int
    ultimo_comentario: Optional[datetime] = None


# ==================== SCHEMAS DE FILTROS ====================

class ComentariosFiltros(BaseModel):
    """Schema para filtros de búsqueda de comentarios"""
    curso_id: UUID
    tipo: Optional[TipoComentario] = None
    busqueda: Optional[str] = None
    autor_id: Optional[UUID] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    solo_sin_respuesta: bool = False
    incluir_eliminados: bool = False
    ordenar_por: str = "fecha_creacion"
    orden_desc: bool = True
    pagina: int = Field(default=1, ge=1)
    limite: int = Field(default=20, ge=1, le=100)

    @validator('busqueda')
    def validar_busqueda(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('La búsqueda debe tener al menos 2 caracteres')
        return v.strip() if v else None


# ==================== SCHEMAS DE ESTADÍSTICAS ====================

class ComentarioEstadisticas(BaseModel):
    """Schema para estadísticas de comentarios"""
    comentarios_por_dia: Dict[str, int]  # "YYYY-MM-DD": count
    comentarios_por_tipo: Dict[str, int]  # tipo: count
    usuarios_mas_activos: List[Dict[str, Any]]  # [{"usuario": info, "total": count}]
    preguntas_frecuentes: List[str]  # Lista de palabras/temas más frecuentes
    tiempo_promedio_respuesta: Optional[float] = None  # Horas promedio para responder preguntas


# ==================== SCHEMAS DE BULK OPERATIONS ====================

class ComentariosBulkDelete(BaseModel):
    """Schema para eliminar múltiples comentarios"""
    comentario_ids: List[UUID] = Field(..., min_items=1, max_items=50)
    motivo: Optional[str] = None


class ComentariosBulkUpdate(BaseModel):
    """Schema para actualizar múltiples comentarios"""
    comentario_ids: List[UUID] = Field(..., min_items=1, max_items=50)
    activo: Optional[bool] = None
    tipo: Optional[TipoComentario] = None