"""
TestDataBuilders - Patrón Builder para Tests Profesionales
==========================================================

Implementación profesional del Builder Pattern para crear fixtures de test.

Principios aplicados:
- Builder Pattern: Construcción fluida de objetos complejos
- Fluent Interface: Métodos encadenables
- Sensible Defaults: Valores por defecto razonables
- Single Responsibility: Cada builder un modelo
- DRY: No repetir configuraciones comunes

Author: GitHub Copilot
Date: 1 nov 2025
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID
from typing import Optional, List, Dict, Any
from decimal import Decimal

# Imports de modelos
from src.models.evaluaciones.evaluacion_expandida import (
    Evaluacion,
    PreguntaEvaluacion,
    TipoEvaluacion,
    TipoPreguntaExpandido,
    EstadoEvaluacion,
    VisibilidadEvaluacion,
)
from src.models.evaluaciones.intento_respuesta_gamificacion import (
    IntentoEvaluacion,
    RespuestaEstudiante,
    EstadoIntento,
    NivelRiesgoIntento,
)
from src.models.evaluaciones.configuracion_antitrampa import (
    ConfiguracionAntiTrampa,
    TipoConfiguracion,
    NivelSeguridad,
)
from src.models.academic.curso import Curso


# ==================== BASE BUILDER ====================

class BaseBuilder:
    """Clase base para todos los builders"""
    
    def build(self):
        """Construye y retorna el objeto"""
        raise NotImplementedError("Subclases deben implementar build()")


# ==================== EVALUACION BUILDER ====================

class EvaluacionBuilder(BaseBuilder):
    """
    Builder para crear Evaluaciones de test.
    
    Uso:
        evaluacion = (EvaluacionBuilder()
            .with_titulo("Mi Examen")
            .with_tipo(TipoEvaluacion.QUIZ)
            .with_fechas_activas()
            .build())
    """
    
    def __init__(self):
        # Valores por defecto mínimos
        self._evaluacion_id = uuid4()
        self._titulo = "Evaluación de Prueba"
        self._tipo_evaluacion = TipoEvaluacion.QUIZ
        self._estado = EstadoEvaluacion.BORRADOR
        self._puntuacion_total = 100.0
        self._fecha_creacion = datetime.now(timezone.utc)
        
        # Opcionales (None por defecto)
        self._curso_id: Optional[UUID] = None
        self._descripcion: Optional[str] = None
        self._fecha_apertura: Optional[datetime] = None
        self._fecha_cierre: Optional[datetime] = None
        self._tiempo_limite_minutos: Optional[int] = None
        self._max_intentos: int = 1
        self._codigo_acceso: Optional[str] = None
        
    def with_id(self, evaluacion_id: UUID) -> 'EvaluacionBuilder':
        """Establece ID específico"""
        self._evaluacion_id = evaluacion_id
        return self
        
    def with_titulo(self, titulo: str) -> 'EvaluacionBuilder':
        """Establece título"""
        self._titulo = titulo
        return self
        
    def with_tipo(self, tipo: TipoEvaluacion) -> 'EvaluacionBuilder':
        """Establece tipo de evaluación"""
        self._tipo_evaluacion = tipo
        return self
        
    def with_estado(self, estado: EstadoEvaluacion) -> 'EvaluacionBuilder':
        """Establece estado"""
        self._estado = estado
        return self
        
    def with_curso(self, curso_id: UUID) -> 'EvaluacionBuilder':
        """Asocia a un curso"""
        self._curso_id = curso_id
        return self
        
    def with_puntuacion(self, total: float, minima: Optional[float] = None) -> 'EvaluacionBuilder':
        """Establece puntuación total y mínima de aprobación"""
        self._puntuacion_total = total
        if minima:
            self._puntuacion_minima_aprobacion = minima
        return self
        
    def with_fechas_activas(self, duracion_dias: int = 7) -> 'EvaluacionBuilder':
        """
        Configura fechas para evaluación activa.
        Por defecto: abierta hace 1 hora, cierra en 7 días
        """
        ahora = datetime.now(timezone.utc)
        self._fecha_apertura = ahora - timedelta(hours=1)
        self._fecha_cierre = ahora + timedelta(days=duracion_dias)
        return self
        
    def with_fechas_futuras(self, dias_hasta_apertura: int = 7) -> 'EvaluacionBuilder':
        """Configura fechas para evaluación futura"""
        ahora = datetime.now(timezone.utc)
        self._fecha_apertura = ahora + timedelta(days=dias_hasta_apertura)
        self._fecha_cierre = ahora + timedelta(days=dias_hasta_apertura + 7)
        return self
        
    def with_tiempo_limite(self, minutos: int) -> 'EvaluacionBuilder':
        """Establece tiempo límite"""
        self._tiempo_limite_minutos = minutos
        return self
        
    def with_multiples_intentos(self, max_intentos: int = 3) -> 'EvaluacionBuilder':
        """Permite múltiples intentos"""
        self._max_intentos = max_intentos
        return self
        
    def with_codigo_acceso(self, codigo: str) -> 'EvaluacionBuilder':
        """Requiere código de acceso"""
        self._codigo_acceso = codigo
        return self
        
    def publicada(self) -> 'EvaluacionBuilder':
        """Marca como activa (publicada)"""
        self._estado = EstadoEvaluacion.ACTIVA
        self.with_fechas_activas()
        return self
        
    def build(self) -> Evaluacion:
        """Construye la evaluación"""
        return Evaluacion(
            evaluacion_id=self._evaluacion_id,
            titulo=self._titulo,
            tipo_evaluacion=self._tipo_evaluacion,
            estado=self._estado,
            puntuacion_total=self._puntuacion_total,
            fecha_creacion=self._fecha_creacion,
            curso_id=self._curso_id,
            descripcion=self._descripcion,
            fecha_apertura=self._fecha_apertura,
            fecha_cierre=self._fecha_cierre,
            tiempo_limite_minutos=self._tiempo_limite_minutos,
            max_intentos=self._max_intentos,
            codigo_acceso=self._codigo_acceso,
        )


# ==================== PREGUNTA BUILDER ====================

class PreguntaBuilder(BaseBuilder):
    """
    Builder para crear Preguntas de test.
    
    Uso:
        pregunta = (PreguntaBuilder()
            .opcion_multiple("¿Qué es Python?", ["Lenguaje", "Base de datos"], "Lenguaje")
            .con_puntuacion(10.0)
            .build())
    """
    
    def __init__(self):
        self._pregunta_id = uuid4()
        self._evaluacion_id: Optional[UUID] = None
        self._enunciado = "Pregunta de prueba"
        self._tipo_pregunta = TipoPreguntaExpandido.OPCION_MULTIPLE
        self._opciones: Optional[List[str]] = None
        self._respuesta_correcta: Optional[str] = None
        self._puntuacion = 10.0
        self._orden: Optional[int] = None
        
    def with_evaluacion(self, evaluacion_id: UUID) -> 'PreguntaBuilder':
        """Asocia a una evaluación"""
        self._evaluacion_id = evaluacion_id
        return self
        
    def opcion_multiple(
        self, 
        enunciado: str, 
        opciones: List[str], 
        correcta: str
    ) -> 'PreguntaBuilder':
        """Configura como pregunta de opción múltiple"""
        self._tipo_pregunta = TipoPreguntaExpandido.OPCION_MULTIPLE
        self._enunciado = enunciado
        self._opciones = opciones
        self._respuesta_correcta = correcta
        return self
        
    def verdadero_falso(self, enunciado: str, es_verdadero: bool) -> 'PreguntaBuilder':
        """Configura como pregunta verdadero/falso"""
        self._tipo_pregunta = TipoPreguntaExpandido.VERDADERO_FALSO
        self._enunciado = enunciado
        self._opciones = ["Verdadero", "Falso"]
        self._respuesta_correcta = "Verdadero" if es_verdadero else "Falso"
        return self
        
    def respuesta_corta(self, enunciado: str, respuesta: str) -> 'PreguntaBuilder':
        """Configura como pregunta de respuesta corta"""
        self._tipo_pregunta = TipoPreguntaExpandido.RESPUESTA_CORTA
        self._enunciado = enunciado
        self._respuesta_correcta = respuesta
        return self
        
    def ensayo(self, enunciado: str) -> 'PreguntaBuilder':
        """Configura como pregunta de ensayo"""
        self._tipo_pregunta = TipoPreguntaExpandido.ENSAYO
        self._enunciado = enunciado
        return self
        
    def con_puntuacion(self, puntuacion: float) -> 'PreguntaBuilder':
        """Establece puntuación"""
        self._puntuacion = puntuacion
        return self
        
    def con_orden(self, orden: int) -> 'PreguntaBuilder':
        """Establece orden"""
        self._orden = orden
        return self
        
    def build(self) -> PreguntaEvaluacion:
        """Construye la pregunta"""
        return PreguntaEvaluacion(
            pregunta_id=self._pregunta_id,
            evaluacion_id=self._evaluacion_id or uuid4(),
            enunciado=self._enunciado,
            tipo_pregunta=self._tipo_pregunta,
            opciones=self._opciones,
            respuesta_correcta=self._respuesta_correcta,
            puntuacion=self._puntuacion,
            orden=self._orden,
        )


# ==================== INTENTO BUILDER ====================

class IntentoBuilder(BaseBuilder):
    """
    Builder para crear Intentos de evaluación.
    
    Uso:
        intento = (IntentoBuilder()
            .para_evaluacion(eval_id)
            .de_estudiante(est_id)
            .en_progreso()
            .build())
    """
    
    def __init__(self):
        self._intento_id = uuid4()
        self._evaluacion_id: Optional[UUID] = None
        self._estudiante_id: Optional[UUID] = None
        self._numero_intento = 1
        self._estado = EstadoIntento.INICIADO
        self._puntuacion_maxima = 100.0
        self._fecha_inicio = datetime.now(timezone.utc)
        
    def para_evaluacion(self, evaluacion_id: UUID) -> 'IntentoBuilder':
        """Asocia a una evaluación"""
        self._evaluacion_id = evaluacion_id
        return self
        
    def de_estudiante(self, estudiante_id: UUID) -> 'IntentoBuilder':
        """Asocia a un estudiante"""
        self._estudiante_id = estudiante_id
        return self
        
    def numero(self, numero: int) -> 'IntentoBuilder':
        """Establece número de intento"""
        self._numero_intento = numero
        return self
        
    def en_progreso(self) -> 'IntentoBuilder':
        """Marca como en progreso"""
        self._estado = EstadoIntento.EN_PROGRESO
        return self
        
    def finalizado(self, puntuacion: float = 0.0) -> 'IntentoBuilder':
        """Marca como finalizado con puntuación"""
        self._estado = EstadoIntento.FINALIZADO
        self._puntuacion_obtenida = puntuacion
        self._fecha_finalizacion = datetime.now(timezone.utc)
        return self
        
    def build(self) -> IntentoEvaluacion:
        """Construye el intento"""
        return IntentoEvaluacion(
            intento_id=self._intento_id,
            evaluacion_id=self._evaluacion_id or uuid4(),
            estudiante_id=self._estudiante_id or uuid4(),
            numero_intento=self._numero_intento,
            estado=self._estado,
            puntuacion_maxima=self._puntuacion_maxima,
            fecha_inicio=self._fecha_inicio,
        )


# ==================== CONFIGURACION ANTITRAMPA BUILDER ====================

class ConfiguracionAntiTrampaBuilder(BaseBuilder):
    """Builder para ConfiguracionAntiTrampa"""
    
    def __init__(self):
        self._id = uuid4()
        self._nombre = "Configuración de Prueba"
        self._tipo = TipoConfiguracion.GLOBAL
        self._nivel_seguridad = NivelSeguridad.MEDIO
        
    def con_nivel(self, nivel: NivelSeguridad) -> 'ConfiguracionAntiTrampaBuilder':
        """Establece nivel de seguridad"""
        self._nivel_seguridad = nivel
        return self
        
    def tipo_global(self) -> 'ConfiguracionAntiTrampaBuilder':
        """Marca como configuración global"""
        self._tipo = TipoConfiguracion.GLOBAL
        return self
        
    def build(self) -> ConfiguracionAntiTrampa:
        """Construye la configuración"""
        return ConfiguracionAntiTrampa(
            id=self._id,
            nombre=self._nombre,
            tipo=self._tipo,
            nivel_seguridad=self._nivel_seguridad,
        )


# ==================== CURSO BUILDER ====================

class CursoBuilder(BaseBuilder):
    """Builder para Curso"""
    
    def __init__(self):
        self._curso_id = uuid4()
        self._nombre = "Curso de Prueba"
        self._institucion_id = uuid4()
        self._fecha_creacion = datetime.now(timezone.utc)
        
    def con_nombre(self, nombre: str) -> 'CursoBuilder':
        """Establece nombre"""
        self._nombre = nombre
        return self
        
    def con_codigo(self, codigo: str) -> 'CursoBuilder':
        """Establece código"""
        self._codigo_curso = codigo
        return self
        
    def build(self) -> Curso:
        """Construye el curso"""
        return Curso(
            curso_id=self._curso_id,
            nombre=self._nombre,
            institucion_id=self._institucion_id,
            fecha_creacion=self._fecha_creacion,
        )


# ==================== OBJECT MOTHER - ESCENARIOS COMUNES ====================

class EvaluacionMother:
    """Object Mother: Provee evaluaciones para escenarios comunes"""
    
    @staticmethod
    def quiz_simple() -> Evaluacion:
        """Quiz simple de 10 preguntas"""
        return (EvaluacionBuilder()
            .with_titulo("Quiz Rápido")
            .with_tipo(TipoEvaluacion.QUIZ)
            .with_tiempo_limite(30)
            .publicada()
            .build())
            
    @staticmethod
    def examen_final() -> Evaluacion:
        """Examen final formal"""
        return (EvaluacionBuilder()
            .with_titulo("Examen Final")
            .with_tipo(TipoEvaluacion.EXAMEN_FINAL)
            .with_puntuacion(100.0, 60.0)
            .with_tiempo_limite(120)
            .with_codigo_acceso("FINAL2025")
            .publicada()
            .build())
            
    @staticmethod
    def evaluacion_futura() -> Evaluacion:
        """Evaluación que abre en el futuro"""
        return (EvaluacionBuilder()
            .with_titulo("Evaluación Próxima")
            .with_fechas_futuras(7)
            .build())


class PreguntaMother:
    """Object Mother: Provee preguntas para escenarios comunes"""
    
    @staticmethod
    def opcion_multiple_facil(evaluacion_id: UUID) -> PreguntaEvaluacion:
        """Pregunta fácil de opción múltiple"""
        return (PreguntaBuilder()
            .with_evaluacion(evaluacion_id)
            .opcion_multiple(
                "¿Cuál es la capital de Francia?",
                ["Londres", "París", "Madrid", "Roma"],
                "París"
            )
            .con_puntuacion(5.0)
            .build())
            
    @staticmethod
    def verdadero_falso(evaluacion_id: UUID) -> PreguntaEvaluacion:
        """Pregunta verdadero/falso"""
        return (PreguntaBuilder()
            .with_evaluacion(evaluacion_id)
            .verdadero_falso("Python es un lenguaje interpretado", True)
            .con_puntuacion(5.0)
            .build())
