# src/models/communication/comentario.py

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from src.db.base_class import Base


class TipoComentario(enum.Enum):
    """Tipos de comentarios posibles"""
    comentario = "comentario"
    anuncio = "anuncio"
    pregunta = "pregunta"
    respuesta = "respuesta"


class Comentario(Base):
    """
    Modelo para comentarios en cursos
    
    Permite a profesores y estudiantes hacer comentarios, anuncios,
    preguntas y respuestas en los cursos.
    """
    __tablename__ = "Comentario"
    
    # Identificación
    comentario_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="ID único del comentario"
    )
    
    # Relaciones
    curso_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Curso.curso_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID del curso al que pertenece el comentario"
    )
    
    autor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID del usuario que escribió el comentario"
    )
    
    # Comentario padre (para respuestas)
    comentario_padre_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Comentario.comentario_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        doc="ID del comentario padre si es una respuesta"
    )
    
    # Contenido
    contenido = Column(
        Text,
        nullable=False,
        doc="Contenido del comentario"
    )
    
    tipo = Column(
        Enum(TipoComentario),
        nullable=False,
        default=TipoComentario.comentario,
        index=True,
        doc="Tipo de comentario"
    )
    
    # Archivos adjuntos (JSON con lista de URLs)
    archivos_adjuntos = Column(
        Text,  # JSON string
        nullable=True,
        doc="JSON con lista de archivos adjuntos"
    )
    
    # Metadatos
    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="Fecha y hora de creación"
    )
    
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
        doc="Fecha y hora de última actualización"
    )
    
    fecha_eliminacion = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Fecha y hora de eliminación (soft delete)"
    )
    
    esta_eliminado = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Indica si el comentario está eliminado (soft delete)"
    )
    
    editado = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Indica si el comentario ha sido editado"
    )
    
    activo = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Indica si el comentario está activo (no eliminado)"
    )
    
    # Relaciones
    curso = relationship(
        "Curso",
        back_populates="comentarios",
        doc="Curso al que pertenece el comentario"
    )
    
    autor = relationship(
        "Usuario",
        back_populates="comentarios",
        doc="Usuario autor del comentario"
    )
    
    # Relación padre-hijo para respuestas
    respuestas = relationship(
        "Comentario",
        backref="comentario_padre",
        remote_side=[comentario_id],
        cascade="all, delete",
        doc="Respuestas a este comentario"
    )
    
    def __repr__(self) -> str:
        return f"<Comentario {self.comentario_id}: {self.tipo.value} en curso {self.curso_id}>"
    
    @property
    def autor_nombre_completo(self) -> str:
        """Obtener nombre completo del autor"""
        if self.autor:
            return f"{self.autor.nombres} {self.autor.apellidos}"
        return "Usuario desconocido"
    
    @property
    def archivos_lista(self) -> list:
        """Obtener lista de archivos adjuntos"""
        if not self.archivos_adjuntos:
            return []
        
        try:
            import json
            return json.loads(self.archivos_adjuntos)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @archivos_lista.setter
    def archivos_lista(self, archivos: list):
        """Establecer lista de archivos adjuntos"""
        import json
        self.archivos_adjuntos = json.dumps(archivos) if archivos else None