"""
Modelo para EventoAudio - Sistema de Proctoring de Audio
Registra eventos de audio capturados durante evaluaciones.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.db.base_class import Base


class EventoAudio(Base):
    """
    Modelo para registrar eventos de audio durante el proctoring.
    
    Attributes:
        evento_audio_id: ID único del evento de audio
        intento_id: ID del intento de evaluación asociado
        nivel_audio: Nivel de audio detectado (0-100)
        frecuencias_detectadas: Array de frecuencias dominantes detectadas
        duracion_ms: Duración del evento en milisegundos
        es_sospechoso: Indica si el evento es considerado sospechoso
        descripcion: Descripción adicional del evento
        datos_adicionales: Datos adicionales en formato JSON
        fecha_creacion: Timestamp de creación del evento
    """
    
    __tablename__ = "eventos_audio"
    
    # Campos principales
    evento_audio_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID único del evento de audio"
    )
    
    intento_id = Column(
        String,
        ForeignKey("intentos_evaluacion.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="Referencia al intento de evaluación"
    )
    
    nivel_audio = Column(
        Float,
        nullable=False,
        comment="Nivel de audio detectado (0-100)"
    )
    
    frecuencias_detectadas = Column(
        JSONB,
        default=list,
        nullable=False,
        comment="Array JSON con frecuencias dominantes detectadas"
    )
    
    duracion_ms = Column(
        Integer,
        nullable=False,
        comment="Duración del evento en milisegundos"
    )
    
    es_sospechoso = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Indica si el evento es considerado sospechoso"
    )
    
    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción adicional del evento"
    )
    
    datos_adicionales = Column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Datos adicionales en formato JSON"
    )
    
    fecha_creacion = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Timestamp de creación del evento"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            'nivel_audio >= 0 AND nivel_audio <= 100',
            name='check_eventos_audio_nivel_audio_range'
        ),
        CheckConstraint(
            'duracion_ms > 0',
            name='check_eventos_audio_duracion_positiva'
        ),
    )
    
    # Relaciones
    intento = relationship(
        "IntentoEvaluacion",
        back_populates="eventos_audio",
        foreign_keys=[intento_id]
    )
    
    def __repr__(self) -> str:
        return (
            f"<EventoAudio("
            f"id={self.evento_audio_id}, "
            f"intento_id={self.intento_id}, "
            f"nivel_audio={self.nivel_audio}, "
            f"es_sospechoso={self.es_sospechoso}"
            f")>"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario"""
        return {
            "evento_audio_id": self.evento_audio_id,
            "intento_id": self.intento_id,
            "nivel_audio": self.nivel_audio,
            "frecuencias_detectadas": self.frecuencias_detectadas,
            "duracion_ms": self.duracion_ms,
            "es_sospechoso": self.es_sospechoso,
            "descripcion": self.descripcion,
            "datos_adicionales": self.datos_adicionales,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    @property
    def duracion_segundos(self) -> float:
        """Retorna la duración en segundos"""
        return self.duracion_ms / 1000.0
    
    @property
    def frecuencia_promedio(self) -> Optional[float]:
        """Calcula la frecuencia promedio detectada"""
        if not self.frecuencias_detectadas or len(self.frecuencias_detectadas) == 0:
            return None
        return sum(self.frecuencias_detectadas) / len(self.frecuencias_detectadas)
    
    @property
    def tiene_multiples_voces(self) -> bool:
        """
        Determina si hay múltiples voces basado en las frecuencias.
        Heurística simple: si hay más de 2 frecuencias dominantes muy diferentes.
        """
        if not self.frecuencias_detectadas or len(self.frecuencias_detectadas) < 2:
            return False
        
        # Si hay más de 2 frecuencias con diferencia significativa (>100Hz)
        freqs_sorted = sorted(self.frecuencias_detectadas)
        diferencias_grandes = 0
        for i in range(len(freqs_sorted) - 1):
            if freqs_sorted[i + 1] - freqs_sorted[i] > 100:
                diferencias_grandes += 1
        
        return diferencias_grandes >= 2
