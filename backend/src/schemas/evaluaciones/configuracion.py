"""
Schemas Pydantic para configuración del sistema anti-trampa.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID

from src.models.evaluaciones.configuracion_antitrampa import NivelSeguridad, TipoConfiguracion


# ==========================================
# SCHEMAS DE CREACIÓN Y ACTUALIZACIÓN
# ==========================================

class ConfiguracionAntiTrampaBase(BaseModel):
    """Base común para configuración"""
    nombre: str = Field(..., max_length=200, description="Nombre de la configuración")
    descripcion: Optional[str] = Field(None, max_length=500)
    nivel_seguridad: NivelSeguridad = Field(NivelSeguridad.MEDIO)
    es_plantilla: bool = Field(False, description="Si es plantilla reutilizable")
    es_activa: bool = Field(True)
    
    # Detección cambios contexto
    detectar_cambio_pestana: bool = True
    max_cambios_pestana: Optional[int] = Field(5, ge=0, le=100)
    accion_exceder_cambios_pestana: str = Field("alertar", regex="^(alertar|terminar|bloquear)$")
    detectar_cambio_aplicacion: bool = True
    max_cambios_aplicacion: Optional[int] = Field(3, ge=0, le=50)
    detectar_salida_pantalla_completa: bool = True
    max_salidas_pantalla_completa: Optional[int] = Field(2, ge=0, le=20)
    detectar_clic_fuera_ventana: bool = True
    max_clics_fuera_ventana: Optional[int] = Field(10, ge=0, le=200)
    
    # Inactividad
    detectar_inactividad: bool = True
    tiempo_max_inactividad_minutos: Optional[int] = Field(5, ge=1, le=60)
    accion_inactividad: str = Field("alertar", regex="^(alertar|pausar|terminar)$")
    
    # Teclas y acciones
    detectar_teclas_sospechosas: bool = True
    bloquear_copy_paste: bool = False
    bloquear_clic_derecho: bool = False
    bloquear_imprimir_pantalla: bool = True
    bloquear_tecla_windows: bool = False
    teclas_bloqueadas_custom: Optional[List[str]] = None
    
    # Sesiones múltiples
    detectar_multiples_sesiones: bool = True
    permitir_cambio_ip: bool = False
    max_cambios_ip: Optional[int] = Field(0, ge=0, le=10)
    permitir_cambio_user_agent: bool = False
    max_cambios_user_agent: Optional[int] = Field(0, ge=0, le=10)
    detectar_multiples_dispositivos: bool = True
    
    # Patrones respuesta
    detectar_respuestas_muy_rapidas: bool = True
    tiempo_minimo_respuesta_segundos: Optional[int] = Field(5, ge=1, le=300)
    detectar_respuestas_muy_lentas: bool = False
    tiempo_maximo_respuesta_minutos: Optional[int] = Field(30, ge=1, le=180)
    detectar_patron_tiempo_uniforme: bool = True
    umbral_uniformidad: Optional[float] = Field(0.8, ge=0.0, le=1.0)
    detectar_precision_velocidad_anomala: bool = True
    umbral_precision_velocidad: Optional[float] = Field(0.9, ge=0.0, le=1.0)
    detectar_patron_repetitivo: bool = True
    longitud_patron_repetitivo: Optional[int] = Field(3, ge=2, le=10)
    
    # Detección IA
    detectar_ia_respuestas: bool = False
    umbral_probabilidad_ia: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    api_deteccion_ia: str = Field("gptZero", regex="^(gptZero|openai|gemini|custom)$")
    analizar_estilo_escritura: bool = False
    comparar_estilo_previo: bool = False
    
    # Plagio
    detectar_plagio: bool = False
    umbral_similitud_plagio: Optional[float] = Field(0.8, ge=0.0, le=1.0)
    comparar_con_respuestas_previas: bool = True
    comparar_entre_estudiantes_curso: bool = True
    comparar_con_internet: bool = False
    api_plagio_externa: Optional[str] = None
    
    # Webcam
    requerir_webcam: bool = False
    captura_periodica_webcam: bool = False
    intervalo_captura_minutos: Optional[int] = Field(5, ge=1, le=60)
    verificar_identidad_facial: bool = False
    umbral_similitud_facial: Optional[float] = Field(0.85, ge=0.0, le=1.0)
    detectar_multiples_personas: bool = True
    detectar_ausencia_persona: bool = True
    accion_deteccion_anomalia_webcam: str = Field("alertar", regex="^(alertar|pausar|terminar)$")
    almacenar_capturas: bool = True
    encriptar_capturas: bool = True
    eliminar_capturas_dias: Optional[int] = Field(30, ge=1, le=365)
    
    # Red
    monitorear_actividad_red: bool = False
    dominios_permitidos: Optional[List[str]] = None
    dominios_bloqueados: Optional[List[str]] = None
    bloquear_todas_conexiones_externas: bool = False
    alertar_acceso_dominio_sospechoso: bool = True
    
    # Dispositivos
    detectar_dispositivos_externos: bool = False
    bloquear_usb: bool = False
    bloquear_bluetooth: bool = False
    alertar_dispositivo_conectado: bool = True
    
    # Tiempo real
    monitoreo_tiempo_real: bool = True
    alertas_inmediatas: bool = True
    umbral_eventos_criticos: Optional[int] = Field(3, ge=1, le=20)
    enviar_notificacion_profesor: bool = True
    pausar_examen_automaticamente: bool = False
    terminar_examen_automaticamente: bool = False
    mostrar_estudiantes_en_vivo: bool = True
    actualizar_dashboard_segundos: Optional[int] = Field(10, ge=5, le=60)
    
    # Puntuación (pesos personalizables)
    usar_sistema_puntuacion: bool = True
    peso_cambio_pestana: int = Field(3, ge=0, le=10)
    peso_cambio_aplicacion: int = Field(4, ge=0, le=10)
    peso_salida_pantalla_completa: int = Field(5, ge=0, le=10)
    peso_clic_fuera_ventana: int = Field(2, ge=0, le=10)
    peso_inactividad: int = Field(2, ge=0, le=10)
    peso_teclas_sospechosas: int = Field(4, ge=0, le=10)
    peso_multiple_sesion: int = Field(6, ge=0, le=10)
    peso_patron_respuesta: int = Field(5, ge=0, le=10)
    peso_velocidad_anomala: int = Field(3, ge=0, le=10)
    peso_deteccion_ia: int = Field(8, ge=0, le=10)
    peso_plagio: int = Field(7, ge=0, le=10)
    peso_anomalia_webcam: int = Field(6, ge=0, le=10)
    peso_actividad_red_sospechosa: int = Field(5, ge=0, le=10)
    
    umbral_riesgo_bajo: int = Field(15, ge=0, le=100)
    umbral_riesgo_medio: int = Field(35, ge=0, le=100)
    umbral_riesgo_alto: int = Field(60, ge=0, le=100)
    
    # Reporte integridad
    generar_reporte_automatico: bool = True
    umbral_integridad_alta: int = Field(80, ge=0, le=100)
    umbral_integridad_media: int = Field(60, ge=0, le=100)
    umbral_integridad_baja: int = Field(40, ge=0, le=100)
    accion_integridad_muy_baja: str = Field("revisar", regex="^(aprobar|revisar|investigar|invalidar)$")
    
    # Grabación
    grabar_sesion_video: bool = False
    grabar_pantalla: bool = False
    grabar_audio: bool = False
    
    # Avanzada
    configuracion_avanzada: Optional[Dict[str, Any]] = None
    
    @validator('umbral_riesgo_medio')
    def validar_umbral_medio(cls, v, values):
        if 'umbral_riesgo_bajo' in values and v <= values['umbral_riesgo_bajo']:
            raise ValueError('umbral_riesgo_medio debe ser mayor que umbral_riesgo_bajo')
        return v
    
    @validator('umbral_riesgo_alto')
    def validar_umbral_alto(cls, v, values):
        if 'umbral_riesgo_medio' in values and v <= values['umbral_riesgo_medio']:
            raise ValueError('umbral_riesgo_alto debe ser mayor que umbral_riesgo_medio')
        return v
    
    @validator('umbral_integridad_media')
    def validar_integridad_media(cls, v, values):
        if 'umbral_integridad_alta' in values and v >= values['umbral_integridad_alta']:
            raise ValueError('umbral_integridad_media debe ser menor que umbral_integridad_alta')
        return v
    
    @validator('umbral_integridad_baja')
    def validar_integridad_baja(cls, v, values):
        if 'umbral_integridad_media' in values and v >= values['umbral_integridad_media']:
            raise ValueError('umbral_integridad_baja debe ser menor que umbral_integridad_media')
        return v


class ConfiguracionAntiTrampaCreate(ConfiguracionAntiTrampaBase):
    """Schema para crear configuración"""
    tipo: TipoConfiguracion
    padre_id: Optional[UUID] = None
    institucion_id: Optional[UUID] = None
    curso_id: Optional[UUID] = None
    examen_id: Optional[UUID] = None
    estudiante_id: Optional[UUID] = None


class ConfiguracionAntiTrampaUpdate(BaseModel):
    """Schema para actualizar configuración - todos los campos opcionales"""
    nombre: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    nivel_seguridad: Optional[NivelSeguridad] = None
    es_activa: Optional[bool] = None
    
    # Cualquier campo de ConfiguracionAntiTrampaBase puede ser actualizado
    detectar_cambio_pestana: Optional[bool] = None
    max_cambios_pestana: Optional[int] = None
    accion_exceder_cambios_pestana: Optional[str] = None
    detectar_cambio_aplicacion: Optional[bool] = None
    max_cambios_aplicacion: Optional[int] = None
    detectar_salida_pantalla_completa: Optional[bool] = None
    max_salidas_pantalla_completa: Optional[int] = None
    detectar_clic_fuera_ventana: Optional[bool] = None
    max_clics_fuera_ventana: Optional[int] = None
    
    detectar_inactividad: Optional[bool] = None
    tiempo_max_inactividad_minutos: Optional[int] = None
    accion_inactividad: Optional[str] = None
    
    detectar_teclas_sospechosas: Optional[bool] = None
    bloquear_copy_paste: Optional[bool] = None
    bloquear_clic_derecho: Optional[bool] = None
    bloquear_imprimir_pantalla: Optional[bool] = None
    bloquear_tecla_windows: Optional[bool] = None
    teclas_bloqueadas_custom: Optional[List[str]] = None
    
    detectar_multiples_sesiones: Optional[bool] = None
    permitir_cambio_ip: Optional[bool] = None
    max_cambios_ip: Optional[int] = None
    permitir_cambio_user_agent: Optional[bool] = None
    max_cambios_user_agent: Optional[int] = None
    detectar_multiples_dispositivos: Optional[bool] = None
    
    detectar_respuestas_muy_rapidas: Optional[bool] = None
    tiempo_minimo_respuesta_segundos: Optional[int] = None
    detectar_respuestas_muy_lentas: Optional[bool] = None
    tiempo_maximo_respuesta_minutos: Optional[int] = None
    detectar_patron_tiempo_uniforme: Optional[bool] = None
    umbral_uniformidad: Optional[float] = None
    detectar_precision_velocidad_anomala: Optional[bool] = None
    umbral_precision_velocidad: Optional[float] = None
    detectar_patron_repetitivo: Optional[bool] = None
    longitud_patron_repetitivo: Optional[int] = None
    
    detectar_ia_respuestas: Optional[bool] = None
    umbral_probabilidad_ia: Optional[float] = None
    api_deteccion_ia: Optional[str] = None
    analizar_estilo_escritura: Optional[bool] = None
    comparar_estilo_previo: Optional[bool] = None
    
    detectar_plagio: Optional[bool] = None
    umbral_similitud_plagio: Optional[float] = None
    comparar_con_respuestas_previas: Optional[bool] = None
    comparar_entre_estudiantes_curso: Optional[bool] = None
    comparar_con_internet: Optional[bool] = None
    api_plagio_externa: Optional[str] = None
    
    requerir_webcam: Optional[bool] = None
    captura_periodica_webcam: Optional[bool] = None
    intervalo_captura_minutos: Optional[int] = None
    verificar_identidad_facial: Optional[bool] = None
    umbral_similitud_facial: Optional[float] = None
    detectar_multiples_personas: Optional[bool] = None
    detectar_ausencia_persona: Optional[bool] = None
    accion_deteccion_anomalia_webcam: Optional[str] = None
    almacenar_capturas: Optional[bool] = None
    encriptar_capturas: Optional[bool] = None
    eliminar_capturas_dias: Optional[int] = None
    
    monitorear_actividad_red: Optional[bool] = None
    dominios_permitidos: Optional[List[str]] = None
    dominios_bloqueados: Optional[List[str]] = None
    bloquear_todas_conexiones_externas: Optional[bool] = None
    alertar_acceso_dominio_sospechoso: Optional[bool] = None
    
    detectar_dispositivos_externos: Optional[bool] = None
    bloquear_usb: Optional[bool] = None
    bloquear_bluetooth: Optional[bool] = None
    alertar_dispositivo_conectado: Optional[bool] = None
    
    monitoreo_tiempo_real: Optional[bool] = None
    alertas_inmediatas: Optional[bool] = None
    umbral_eventos_criticos: Optional[int] = None
    enviar_notificacion_profesor: Optional[bool] = None
    pausar_examen_automaticamente: Optional[bool] = None
    terminar_examen_automaticamente: Optional[bool] = None
    mostrar_estudiantes_en_vivo: Optional[bool] = None
    actualizar_dashboard_segundos: Optional[int] = None
    
    usar_sistema_puntuacion: Optional[bool] = None
    peso_cambio_pestana: Optional[int] = None
    peso_cambio_aplicacion: Optional[int] = None
    peso_salida_pantalla_completa: Optional[int] = None
    peso_clic_fuera_ventana: Optional[int] = None
    peso_inactividad: Optional[int] = None
    peso_teclas_sospechosas: Optional[int] = None
    peso_multiple_sesion: Optional[int] = None
    peso_patron_respuesta: Optional[int] = None
    peso_velocidad_anomala: Optional[int] = None
    peso_deteccion_ia: Optional[int] = None
    peso_plagio: Optional[int] = None
    peso_anomalia_webcam: Optional[int] = None
    peso_actividad_red_sospechosa: Optional[int] = None
    
    umbral_riesgo_bajo: Optional[int] = None
    umbral_riesgo_medio: Optional[int] = None
    umbral_riesgo_alto: Optional[int] = None
    
    generar_reporte_automatico: Optional[bool] = None
    umbral_integridad_alta: Optional[int] = None
    umbral_integridad_media: Optional[int] = None
    umbral_integridad_baja: Optional[int] = None
    accion_integridad_muy_baja: Optional[str] = None
    
    grabar_sesion_video: Optional[bool] = None
    grabar_pantalla: Optional[bool] = None
    grabar_audio: Optional[bool] = None
    
    configuracion_avanzada: Optional[Dict[str, Any]] = None


class ConfiguracionAntiTrampaResponse(ConfiguracionAntiTrampaBase):
    """Schema de respuesta"""
    id: UUID
    tipo: TipoConfiguracion
    padre_id: Optional[UUID] = None
    institucion_id: Optional[UUID] = None
    curso_id: Optional[UUID] = None
    examen_id: Optional[UUID] = None
    estudiante_id: Optional[UUID] = None
    creado_por_id: UUID
    fecha_creacion: datetime
    fecha_modificacion: datetime
    
    class Config:
        from_attributes = True


class ConfiguracionEfectivaResponse(BaseModel):
    """Configuración efectiva después de aplicar herencia"""
    configuracion: Dict[str, Any]
    origen_valores: Dict[str, str]  # campo -> "propio" | "heredado" | "default"
    configuracion_id: UUID
    jerarquia: List[Dict[str, Any]]  # Lista de configs desde raíz hasta actual


# ==========================================
# SCHEMAS DE PLANTILLAS
# ==========================================

class PlantillaConfiguracionCreate(BaseModel):
    """Crear plantilla desde configuración existente"""
    nombre: str = Field(..., max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    nivel_seguridad: NivelSeguridad
    configuracion_base: ConfiguracionAntiTrampaCreate
    es_publica: bool = True


class PlantillaConfiguracionUpdate(BaseModel):
    """Actualizar plantilla"""
    nombre: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    es_publica: Optional[bool] = None


class PlantillaConfiguracionResponse(BaseModel):
    """Respuesta de plantilla"""
    id: UUID
    nombre: str
    descripcion: Optional[str]
    nivel_seguridad: NivelSeguridad
    configuracion_id: UUID
    es_sistema: bool
    es_publica: bool
    veces_utilizada: int
    creado_por_id: UUID
    institucion_id: Optional[UUID]
    fecha_creacion: datetime
    fecha_modificacion: datetime
    
    # Incluir la configuración completa
    configuracion: Optional[ConfiguracionAntiTrampaResponse] = None
    
    class Config:
        from_attributes = True


class AplicarPlantillaRequest(BaseModel):
    """Request para aplicar plantilla a examen/curso/etc"""
    plantilla_id: UUID
    tipo_destino: TipoConfiguracion
    destino_id: UUID  # ID del examen, curso, etc.
    sobrescribir_existente: bool = False


# ==========================================
# SCHEMAS DE PERFILES RÁPIDOS
# ==========================================

class PerfilSeguridadResponse(BaseModel):
    """Perfil de seguridad predefinido"""
    nivel: NivelSeguridad
    nombre: str
    descripcion: str
    configuracion_sugerida: Dict[str, Any]
    uso_recomendado: str
    
    class Config:
        schema_extra = {
            "example": {
                "nivel": "alto",
                "nombre": "Seguridad Alta",
                "descripcion": "Para exámenes críticos con monitoreo estricto",
                "uso_recomendado": "Exámenes finales, certificaciones",
                "configuracion_sugerida": {
                    "detectar_cambio_pestana": True,
                    "max_cambios_pestana": 3,
                    "requerir_webcam": True,
                    "detectar_plagio": True,
                    "detectar_ia_respuestas": True
                }
            }
        }


# ==========================================
# SCHEMAS DE IMPORTAR/EXPORTAR
# ==========================================

class ExportarConfiguracionResponse(BaseModel):
    """Configuración exportada en formato portable"""
    version: str = "1.0"
    fecha_exportacion: datetime
    configuracion: Dict[str, Any]
    metadatos: Dict[str, Any]


class ImportarConfiguracionRequest(BaseModel):
    """Importar configuración desde JSON"""
    datos_exportados: Dict[str, Any]
    tipo_destino: TipoConfiguracion
    destino_id: Optional[UUID] = None
    nombre_config: str
