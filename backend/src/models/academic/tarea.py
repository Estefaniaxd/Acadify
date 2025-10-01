from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, Float, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid
from src.db.base_class import Base

class EstadoTarea(str, Enum):
    ASIGNADA = "asignada"
    EN_PROGRESO = "en_progreso"
    ENTREGADA = "entregada"
    CALIFICADA = "calificada"
    VENCIDA = "vencida"
    CANCELADA = "cancelada"

class TipoTarea(str, Enum):
    ENSAYO = "ensayo"
    PROYECTO = "proyecto"
    EJERCICIOS = "ejercicios"
    INVESTIGACION = "investigacion"
    PRESENTACION = "presentacion"
    LABORATORIO = "laboratorio"
    LECTURA = "lectura"
    EXAMEN = "examen"
    OTRO = "otro"

class PrioridadTarea(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"

class Tarea(Base):
    __tablename__ = "tareas"
    
    # Clave primaria
    tarea_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relaciones principales
    grupo_id = Column(String, ForeignKey("Grupo.grupo_id", ondelete="CASCADE"), nullable=False)
    docente_id = Column(String, ForeignKey("Usuario.usuario_id", ondelete="CASCADE"), nullable=False)
    
    # Información básica
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    instrucciones = Column(Text)  # Instrucciones detalladas
    objetivos = Column(Text)  # Objetivos de aprendizaje
    
    # Clasificación
    tipo_tarea = Column(SQLEnum(TipoTarea), nullable=False, default=TipoTarea.ENSAYO)
    prioridad = Column(SQLEnum(PrioridadTarea), nullable=False, default=PrioridadTarea.MEDIA)
    categoria = Column(String(100))  # Categoria personalizada
    tags = Column(String(500))  # Tags separados por comas
    
    # Fechas y tiempo
    fecha_asignacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_limite = Column(DateTime(timezone=True), nullable=False)
    fecha_inicio_disponible = Column(DateTime(timezone=True))  # Cuando se puede empezar
    tiempo_estimado = Column(Integer)  # Tiempo estimado en minutos
    
    # Configuración de entrega
    permite_entrega_tardia = Column(Boolean, default=False)
    penalizacion_tardia = Column(Float, default=0.0)  # Porcentaje de penalización
    intentos_maximos = Column(Integer, default=1)
    formato_entrega = Column(String(200))  # Formatos aceptados: PDF, DOCX, etc.
    tamano_maximo_mb = Column(Float, default=10.0)  # Tamaño máximo en MB
    
    # Calificación
    puntuacion_maxima = Column(Float, nullable=False, default=100.0)
    peso_evaluacion = Column(Float, default=1.0)  # Peso en la nota final
    rubrica_id = Column(String, ForeignKey("rubricas.rubrica_id"), nullable=True)
    
    # Estado y configuración
    estado = Column(SQLEnum(EstadoTarea), nullable=False, default=EstadoTarea.ASIGNADA)
    es_grupal = Column(Boolean, default=False)  # Tarea individual o grupal
    es_publica = Column(Boolean, default=True)  # Visible para todos los estudiantes del grupo
    requiere_aprobacion = Column(Boolean, default=False)  # Si requiere aprobación antes de mostrar
    
    # Opciones avanzadas
    configuracion_json = Column(JSON)  # Configuraciones adicionales en JSON
    recursos_necesarios = Column(Text)  # Lista de recursos necesarios
    criterios_evaluacion = Column(Text)  # Criterios de evaluación
    
    # Metadatos
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    creado_por = Column(String, ForeignKey("Usuario.usuario_id"), nullable=True)
    actualizado_por = Column(String, ForeignKey("Usuario.usuario_id"), nullable=True)
    
    # Relaciones
    grupo = relationship("Grupo", back_populates="tareas")
    docente = relationship("Usuario", foreign_keys=[docente_id])
    entregas = relationship("EntregaTarea", back_populates="tarea", cascade="all, delete-orphan")
    rubrica = relationship("Rubrica", back_populates="tareas", uselist=False)
    
    # Propiedades calculadas
    @property
    def total_entregas(self) -> int:
        """Número total de entregas recibidas"""
        return len([e for e in self.entregas if e.estado != "borrador"])
    
    @property
    def entregas_pendientes(self) -> int:
        """Número de entregas pendientes de calificación"""
        return len([e for e in self.entregas if e.estado == "entregada"])
    
    @property
    def promedio_calificaciones(self) -> float:
        """Promedio de las calificaciones otorgadas"""
        calificadas = [e for e in self.entregas if e.calificacion is not None]
        if not calificadas:
            return 0.0
        return sum(e.calificacion for e in calificadas) / len(calificadas)
    
    @property
    def esta_vencida(self) -> bool:
        """Indica si la fecha límite ya pasó"""
        from datetime import datetime
        return datetime.now() > self.fecha_limite if self.fecha_limite else False
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'tarea_id': self.tarea_id,
            'grupo_id': self.grupo_id,
            'docente_id': self.docente_id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'tipo_tarea': self.tipo_tarea.value if self.tipo_tarea else None,
            'prioridad': self.prioridad.value if self.prioridad else None,
            'estado': self.estado.value if self.estado else None,
            'fecha_limite': self.fecha_limite.isoformat() if self.fecha_limite else None,
            'puntuacion_maxima': self.puntuacion_maxima,
            'es_grupal': self.es_grupal,
            'total_entregas': self.total_entregas,
            'entregas_pendientes': self.entregas_pendientes,
            'esta_vencida': self.esta_vencida,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }


class EntregaTarea(Base):
    __tablename__ = "entregas_tareas"
    
    # Clave primaria
    entrega_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relaciones principales
    tarea_id = Column(String, ForeignKey("tareas.tarea_id", ondelete="CASCADE"), nullable=False)
    estudiante_id = Column(String, ForeignKey("Usuario.usuario_id", ondelete="CASCADE"), nullable=False)
    
    # Información de entrega
    titulo_entrega = Column(String(200))
    descripcion_entrega = Column(Text)
    comentarios_estudiante = Column(Text)  # Comentarios del estudiante al entregar
    
    # Archivos y contenido
    archivo_url = Column(String(500))  # URL del archivo principal
    archivos_adicionales = Column(JSON)  # Lista de archivos adicionales
    contenido_texto = Column(Text)  # Para entregas de texto plano
    enlaces_externos = Column(JSON)  # Enlaces a recursos externos (GitHub, etc.)
    
    # Fechas y control
    fecha_entrega = Column(DateTime(timezone=True))
    fecha_limite_original = Column(DateTime(timezone=True))  # Para tracking de entregas tardías
    numero_intento = Column(Integer, default=1)
    es_entrega_tardia = Column(Boolean, default=False)
    
    # Calificación
    calificacion = Column(Float)  # Nota numérica
    calificacion_letras = Column(String(5))  # A, B, C, D, F
    comentarios_docente = Column(Text)  # Retroalimentación del docente
    rubrica_calificacion = Column(JSON)  # Calificación detallada por rúbrica
    
    # Estado y configuración
    estado = Column(String(50), default="borrador")  # borrador, entregada, calificada, devuelta
    es_final = Column(Boolean, default=False)  # Si es la entrega final
    requiere_revision = Column(Boolean, default=False)  # Si necesita revisión adicional
    
    # Metadatos de evaluación
    tiempo_empleado = Column(Integer)  # Tiempo empleado en minutos (self-reported)
    dificultad_percibida = Column(Integer)  # 1-5, qué tan difícil percibió la tarea
    satisfaccion_estudiante = Column(Integer)  # 1-5, qué tan satisfecho está con su entrega
    
    # Metadatos
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    calificado_por = Column(String, ForeignKey("Usuario.usuario_id"), nullable=True)
    fecha_calificacion = Column(DateTime(timezone=True))
    
    # Relaciones
    tarea = relationship("src.models.academic.tarea.Tarea", back_populates="entregas")
    estudiante = relationship("Usuario", foreign_keys=[estudiante_id])
    calificador = relationship("Usuario", foreign_keys=[calificado_por])
    
    # Propiedades calculadas
    @property
    def dias_desde_entrega(self) -> int:
        """Días transcurridos desde la entrega"""
        if not self.fecha_entrega:
            return 0
        from datetime import datetime
        return (datetime.now() - self.fecha_entrega).days
    
    @property
    def porcentaje_calificacion(self) -> float:
        """Calificación como porcentaje"""
        if not self.calificacion or not self.tarea:
            return 0.0
        return (self.calificacion / self.tarea.puntuacion_maxima) * 100
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'entrega_id': self.entrega_id,
            'tarea_id': self.tarea_id,
            'estudiante_id': self.estudiante_id,
            'titulo_entrega': self.titulo_entrega,
            'estado': self.estado,
            'fecha_entrega': self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            'calificacion': self.calificacion,
            'es_entrega_tardia': self.es_entrega_tardia,
            'numero_intento': self.numero_intento,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'porcentaje_calificacion': self.porcentaje_calificacion
        }


class Rubrica(Base):
    __tablename__ = "rubricas"
    
    # Clave primaria
    rubrica_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Información básica
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    
    # Criterios de evaluación (JSON)
    criterios = Column(JSON, nullable=False)  # Lista de criterios con niveles y puntuaciones
    
    # Configuración
    puntuacion_total = Column(Float, nullable=False, default=100.0)
    es_publica = Column(Boolean, default=True)  # Si puede ser usada por otros docentes
    es_plantilla = Column(Boolean, default=False)  # Si es una plantilla predefinida
    
    # Metadatos
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    creado_por = Column(String, ForeignKey("Usuario.usuario_id"), nullable=False)
    
    # Relaciones
    tareas = relationship("src.models.academic.tarea.Tarea", back_populates="rubrica")
    creador = relationship("Usuario", foreign_keys=[creado_por])
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'rubrica_id': self.rubrica_id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'criterios': self.criterios,
            'puntuacion_total': self.puntuacion_total,
            'es_publica': self.es_publica,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }