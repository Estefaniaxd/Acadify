"""
Schemas enriquecidos para el sistema de tareas.
Incluye estados calculados, métricas de progreso y lógica de negocio.
Aplica Clean Code y principios SOLID.
"""

from pydantic import BaseModel, Field, computed_field
from typing import Optional, Literal
from datetime import datetime, timedelta
from enum import Enum

from .tarea_schemas import TareaResponse
from ...enums.academic.tareas import EstadoTarea, PrioridadTarea


class EstadoVisualizacion(str, Enum):
    """Estados calculados para visualización en el frontend."""
    PENDIENTE = "pendiente"
    PROXIMA_A_VENCER = "proxima_a_vencer"  # Menos de 48 horas
    VENCIDA = "vencida"
    ENTREGADA = "entregada"
    ENTREGADA_TARDIA = "entregada_tardia"
    CALIFICADA = "calificada"
    REVISADA = "revisada"
    CANCELADA = "cancelada"


class ColorEstado(str, Enum):
    """Colores para badges según estado."""
    GRAY = "gray"      # Pendiente
    BLUE = "blue"      # En progreso
    YELLOW = "yellow"  # Próxima a vencer
    RED = "red"        # Vencida
    GREEN = "green"    # Entregada/Calificada
    PURPLE = "purple"  # Revisada
    ORANGE = "orange"  # Entregada tardía


class IconoEstado(str, Enum):
    """Iconos para representar estados."""
    CLOCK = "clock"
    ALERT = "alert"
    CHECK = "check"
    X_CIRCLE = "x-circle"
    STAR = "star"
    EDIT = "edit"


class MetricasProgreso(BaseModel):
    """Métricas de progreso de una tarea."""
    
    total_estudiantes: int = Field(..., description="Total de estudiantes asignados")
    entregas_realizadas: int = Field(..., description="Número de entregas realizadas")
    entregas_calificadas: int = Field(..., description="Número de entregas calificadas")
    entregas_pendientes: int = Field(..., description="Número de entregas pendientes")
    entregas_tardias: int = Field(default=0, description="Número de entregas tardías")
    
    @computed_field
    @property
    def porcentaje_completitud(self) -> float:
        """Calcula porcentaje de completitud (entregas/total)."""
        if self.total_estudiantes == 0:
            return 0.0
        return round((self.entregas_realizadas / self.total_estudiantes) * 100, 2)
    
    @computed_field
    @property
    def porcentaje_calificadas(self) -> float:
        """Calcula porcentaje de entregas calificadas."""
        if self.entregas_realizadas == 0:
            return 0.0
        return round((self.entregas_calificadas / self.entregas_realizadas) * 100, 2)
    
    @computed_field
    @property
    def tasa_puntualidad(self) -> float:
        """Calcula tasa de entregas puntuales."""
        if self.entregas_realizadas == 0:
            return 100.0
        entregas_puntuales = self.entregas_realizadas - self.entregas_tardias
        return round((entregas_puntuales / self.entregas_realizadas) * 100, 2)


class EstadisticasCalificacion(BaseModel):
    """Estadísticas de calificación de una tarea."""
    
    promedio_calificacion: Optional[float] = Field(None, description="Promedio de calificaciones")
    calificacion_maxima: Optional[float] = Field(None, description="Calificación más alta")
    calificacion_minima: Optional[float] = Field(None, description="Calificación más baja")
    desviacion_estandar: Optional[float] = Field(None, description="Desviación estándar")
    mediana: Optional[float] = Field(None, description="Mediana de calificaciones")
    
    @computed_field
    @property
    def rango_calificacion(self) -> Optional[float]:
        """Calcula el rango de calificaciones."""
        if self.calificacion_maxima is not None and self.calificacion_minima is not None:
            return round(self.calificacion_maxima - self.calificacion_minima, 2)
        return None


class TiempoRestante(BaseModel):
    """Información sobre tiempo restante para una tarea."""
    
    dias_restantes: int = Field(..., description="Días restantes hasta la fecha límite")
    horas_restantes: int = Field(..., description="Horas restantes adicionales")
    minutos_restantes: int = Field(..., description="Minutos restantes adicionales")
    
    @computed_field
    @property
    def total_horas(self) -> float:
        """Total de horas restantes (incluyendo días)."""
        return round(self.dias_restantes * 24 + self.horas_restantes + self.minutos_restantes / 60, 2)
    
    @computed_field
    @property
    def es_urgente(self) -> bool:
        """Indica si quedan menos de 48 horas."""
        return self.total_horas < 48
    
    @computed_field
    @property
    def es_muy_urgente(self) -> bool:
        """Indica si quedan menos de 24 horas."""
        return self.total_horas < 24
    
    @computed_field
    @property
    def mensaje_tiempo(self) -> str:
        """Mensaje legible sobre el tiempo restante."""
        if self.dias_restantes > 7:
            return f"{self.dias_restantes} días"
        elif self.dias_restantes > 0:
            return f"{self.dias_restantes}d {self.horas_restantes}h"
        elif self.horas_restantes > 0:
            return f"{self.horas_restantes}h {self.minutos_restantes}m"
        else:
            return f"{self.minutos_restantes} minutos"


class EstadoVisual(BaseModel):
    """Información visual para representar el estado de una tarea."""
    
    estado: EstadoVisualizacion = Field(..., description="Estado calculado")
    color: ColorEstado = Field(..., description="Color para badge")
    icono: IconoEstado = Field(..., description="Icono a mostrar")
    texto: str = Field(..., description="Texto descriptivo del estado")
    tooltip: Optional[str] = Field(None, description="Tooltip adicional")


class TareaEnriquecida(TareaResponse):
    """
    Schema enriquecido de Tarea con estados calculados y métricas.
    Extiende TareaResponse añadiendo información procesada.
    """
    
    # Estados calculados
    estado_visualizacion: EstadoVisualizacion = Field(..., description="Estado calculado para UI")
    estado_visual: EstadoVisual = Field(..., description="Información visual del estado")
    
    # Tiempo
    tiempo_restante: Optional[TiempoRestante] = Field(None, description="Información de tiempo restante")
    dias_desde_asignacion: int = Field(..., description="Días desde que se asignó")
    
    # Métricas
    metricas_progreso: MetricasProgreso = Field(..., description="Métricas de progreso")
    estadisticas_calificacion: Optional[EstadisticasCalificacion] = Field(
        None, description="Estadísticas de calificación"
    )
    
    # Flags booleanos útiles
    es_activa: bool = Field(..., description="Si la tarea está activa y disponible")
    es_vencida: bool = Field(..., description="Si la fecha límite ya pasó")
    es_proxima_a_vencer: bool = Field(..., description="Si vence en menos de 48h")
    requiere_atencion: bool = Field(..., description="Si requiere atención inmediata")
    permite_entregas: bool = Field(..., description="Si aún se pueden hacer entregas")
    
    # Información adicional
    peso_porcentual: float = Field(..., description="Peso en porcentaje del total de evaluaciones")
    puntos_disponibles: float = Field(..., description="Puntos disponibles considerando penalizaciones")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "tarea_id": "123e4567-e89b-12d3-a456-426614174000",
                "titulo": "Ensayo sobre Algoritmos",
                "estado_visualizacion": "proxima_a_vencer",
                "estado_visual": {
                    "estado": "proxima_a_vencer",
                    "color": "yellow",
                    "icono": "alert",
                    "texto": "Próxima a vencer",
                    "tooltip": "Quedan menos de 48 horas"
                },
                "tiempo_restante": {
                    "dias_restantes": 1,
                    "horas_restantes": 12,
                    "minutos_restantes": 30,
                    "mensaje_tiempo": "1d 12h"
                },
                "metricas_progreso": {
                    "total_estudiantes": 30,
                    "entregas_realizadas": 25,
                    "entregas_calificadas": 20,
                    "entregas_pendientes": 5,
                    "porcentaje_completitud": 83.33
                }
            }
        }


class TareaResumen(BaseModel):
    """Schema resumido para listas y vistas rápidas."""
    
    tarea_id: str
    titulo: str
    fecha_limite: datetime
    puntuacion_maxima: float
    prioridad: PrioridadTarea
    
    # Estados y métricas resumidas
    estado_visualizacion: EstadoVisualizacion
    color_badge: ColorEstado
    icono: IconoEstado
    dias_restantes: Optional[int]
    mensaje_tiempo: Optional[str]
    porcentaje_completitud: float
    entregas_pendientes: int
    
    # Flags
    es_vencida: bool
    es_urgente: bool
    tiene_entregas_sin_calificar: bool
    
    class Config:
        from_attributes = True


class TareaEstudianteEnriquecida(BaseModel):
    """Schema enriquecido desde la perspectiva del estudiante."""
    
    tarea_id: str
    titulo: str
    descripcion: Optional[str]
    instrucciones: Optional[str]
    fecha_limite: datetime
    puntuacion_maxima: float
    peso_evaluacion: float
    
    # Estado personal del estudiante
    ha_entregado: bool = Field(..., description="Si el estudiante ha entregado")
    entrega_calificada: bool = Field(default=False, description="Si su entrega está calificada")
    calificacion_obtenida: Optional[float] = Field(None, description="Calificación obtenida")
    numero_intentos: int = Field(default=0, description="Número de intentos realizados")
    intentos_restantes: int = Field(..., description="Intentos que le quedan")
    
    # Estados calculados
    estado_personal: Literal[
        "sin_entregar",
        "entregada_sin_calificar",
        "entregada_tardia",
        "calificada_aprobada",
        "calificada_reprobada",
        "vencida_sin_entregar"
    ] = Field(..., description="Estado personal del estudiante")
    
    tiempo_restante: Optional[TiempoRestante]
    puede_entregar: bool = Field(..., description="Si puede hacer/rehacer entrega")
    es_tardia: bool = Field(..., description="Si la entrega sería tardía")
    penalizacion_aplicable: float = Field(default=0.0, description="Penalización si entrega ahora")
    
    class Config:
        from_attributes = True


# Schemas para requests con filtros
class FiltrosTareaEnriquecida(BaseModel):
    """Filtros para consultar tareas enriquecidas."""
    
    grupo_id: Optional[str] = None
    docente_id: Optional[str] = None
    estado_visualizacion: Optional[EstadoVisualizacion] = None
    prioridad: Optional[PrioridadTarea] = None
    solo_activas: bool = True
    solo_proximas_a_vencer: bool = False
    solo_vencidas: bool = False
    solo_con_entregas_pendientes: bool = False
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    busqueda: Optional[str] = None
    ordenar_por: Literal[
        "fecha_limite",
        "fecha_asignacion",
        "prioridad",
        "titulo",
        "porcentaje_completitud"
    ] = "fecha_limite"
    orden_desc: bool = False
    pagina: int = Field(default=1, ge=1)
    tamaño_pagina: int = Field(default=20, ge=1, le=100)


class RespuestaPaginada(BaseModel):
    """Respuesta paginada genérica."""
    
    items: list[TareaEnriquecida] = Field(..., description="Lista de tareas enriquecidas")
    total: int = Field(..., description="Total de items")
    pagina: int = Field(..., description="Página actual")
    tamaño_pagina: int = Field(..., description="Tamaño de página")
    total_paginas: int = Field(..., description="Total de páginas")
    tiene_siguiente: bool = Field(..., description="Si hay página siguiente")
    tiene_anterior: bool = Field(..., description="Si hay página anterior")
    
    @computed_field
    @property
    def rango_items(self) -> str:
        """Rango de items mostrados (ej: "1-20 de 150")."""
        inicio = (self.pagina - 1) * self.tamaño_pagina + 1
        fin = min(inicio + self.tamaño_pagina - 1, self.total)
        return f"{inicio}-{fin} de {self.total}"
