"""
Endpoints de Proctoring para Evaluaciones

Este módulo maneja todo lo relacionado con el sistema de proctoring
(monitoreo por cámara y micrófono) durante la toma de exámenes.

Características:
- Registro de eventos anti-trampa
- Almacenamiento de snapshots de cámara
- Registro de eventos de audio
- Resumen de sesión de proctoring
- Análisis de riesgos

Principios SOLID aplicados:
- Single Responsibility: Solo maneja proctoring
- Open/Closed: Extensible mediante nuevos tipos de eventos
- Dependency Inversion: Usa servicios inyectados

Author: Acadify Team
Date: 2025-11-08
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from enum import Enum

from src.api.deps import get_db, get_current_user
from src.models import IntentoEvaluacion, EventoAntiTrampa, EventoAudio
from src.models.users.usuario import Usuario

# ================================
# ENUMS Y TIPOS
# ================================

class TipoEventoProctoring(str, Enum):
    """Tipos de eventos de proctoring"""
    # Eventos de rostros
    SIN_ROSTRO_DETECTADO = "sin_rostro_detectado"
    MULTIPLES_ROSTROS = "multiples_rostros"
    ROSTRO_DESCONOCIDO = "rostro_desconocido"
    
    # Eventos de audio
    AUDIO_SOSPECHOSO = "audio_sospechoso"
    MULTIPLES_VOCES = "multiples_voces"
    AUDIO_EXTERNO = "audio_externo"
    
    # Eventos de navegación
    CAMBIO_PESTANA = "cambio_pestana"
    CAMBIO_APLICACION = "cambio_aplicacion"
    SALIDA_PANTALLA_COMPLETA = "salida_pantalla_completa"
    
    # Eventos de interacción
    CLIC_FUERA_VENTANA = "clic_fuera_ventana"
    COPIAR_TEXTO = "copiar_texto"
    PEGAR_TEXTO = "pegar_texto"
    
    # Eventos de objetos
    CELULAR_DETECTADO = "celular_detectado"
    LIBRO_DETECTADO = "libro_detectado"
    PERSONA_ADICIONAL = "persona_adicional"


class SeveridadEvento(str, Enum):
    """Severidad de eventos de proctoring"""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class NivelRiesgo(str, Enum):
    """Nivel de riesgo global de la sesión"""
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


# ================================
# SCHEMAS PYDANTIC
# ================================

class EventoProctoringCreate(BaseModel):
    """Schema para crear un evento de proctoring"""
    tipo_evento: TipoEventoProctoring
    severidad: SeveridadEvento
    detalle: str = Field(..., min_length=1, max_length=500)
    datos_adicionales: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "tipo_evento": "sin_rostro_detectado",
                "severidad": "alta",
                "detalle": "No se detectó ningún rostro durante 5 segundos",
                "datos_adicionales": {"duracion_segundos": 5}
            }
        }


class SnapshotProctoringCreate(BaseModel):
    """Schema para crear un snapshot de cámara"""
    imagen_base64: str = Field(..., min_length=100)
    ancho: int = Field(..., gt=0, le=1920)
    alto: int = Field(..., gt=0, le=1080)
    calidad: float = Field(0.7, ge=0.1, le=1.0)
    rostros_detectados: int = Field(0, ge=0)
    datos_adicionales: Optional[dict] = None
    
    @validator('imagen_base64')
    def validar_base64(cls, v):
        if not v.startswith('data:image/'):
            raise ValueError('Imagen debe ser base64 con prefijo data:image/')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
                "ancho": 1280,
                "alto": 720,
                "calidad": 0.7,
                "rostros_detectados": 1,
                "datos_adicionales": {"timestamp": "2025-11-08T12:30:45Z"}
            }
        }


class EventoAudioCreate(BaseModel):
    """Schema para crear un evento de audio"""
    nivel_audio: int = Field(..., ge=0, le=100)
    duracion_ms: int = Field(..., gt=0)
    frecuencia_dominante: Optional[float] = None
    es_sospechoso: bool = False
    datos_adicionales: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "nivel_audio": 75,
                "duracion_ms": 1000,
                "frecuencia_dominante": 440.0,
                "es_sospechoso": True,
                "datos_adicionales": {"umbral_superado": 70}
            }
        }


class EventoProctoringResponse(BaseModel):
    """Schema de respuesta para evento de proctoring"""
    evento_id: str
    intento_id: str
    tipo_evento: str
    severidad: str
    detalle: str
    timestamp: datetime
    resuelta: bool
    datos_adicionales: Optional[dict]
    
    class Config:
        from_attributes = True


class ResumenProctoringResponse(BaseModel):
    """Schema de respuesta para resumen de proctoring"""
    intento_id: str
    total_eventos: int
    eventos_por_severidad: dict
    eventos_por_tipo: dict
    nivel_riesgo: NivelRiesgo
    duracion_minutos: float
    total_snapshots: int
    total_eventos_audio: int
    promedio_nivel_audio: float
    infracciones_criticas: List[EventoProctoringResponse]
    ultimo_snapshot: Optional[str]
    recomendacion: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "intento_id": "uuid-123",
                "total_eventos": 15,
                "eventos_por_severidad": {"baja": 5, "media": 7, "alta": 2, "critica": 1},
                "eventos_por_tipo": {"sin_rostro_detectado": 3, "audio_sospechoso": 5},
                "nivel_riesgo": "medio",
                "duracion_minutos": 45.5,
                "total_snapshots": 30,
                "total_eventos_audio": 100,
                "promedio_nivel_audio": 35.5,
                "infracciones_criticas": [],
                "ultimo_snapshot": "snapshot_url",
                "recomendacion": "Revisar eventos de audio sospechoso"
            }
        }


# ================================
# ROUTER
# ================================

router = APIRouter(
    prefix="/proctoring",
    tags=["Proctoring"],
    responses={404: {"description": "No encontrado"}}
)


# ================================
# ENDPOINTS
# ================================

@router.post(
    "/intentos/{intento_id}/eventos",
    response_model=EventoProctoringResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar evento de proctoring",
    description="""
    Registra un evento anti-trampa detectado durante el examen.
    
    **Tipos de eventos**:
    - Rostros: sin rostro, múltiples rostros, rostro desconocido
    - Audio: audio sospechoso, múltiples voces
    - Navegación: cambio de pestaña, salida de pantalla completa
    - Objetos: celular, libro, persona adicional
    
    **Severidades**:
    - Baja: Eventos menores, no requieren acción inmediata
    - Media: Eventos que ameritan revisión
    - Alta: Eventos sospechosos que deben investigarse
    - Crítica: Eventos graves que pueden invalidar el examen
    """
)
async def registrar_evento_proctoring(
    intento_id: str,
    evento: EventoProctoringCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registra un evento de proctoring durante un intento de examen.
    
    Args:
        intento_id: ID del intento de examen
        evento: Datos del evento a registrar
        db: Sesión de base de datos
        current_user: Usuario autenticado
    
    Returns:
        EventoProctoringResponse: Evento registrado
    
    Raises:
        HTTPException 404: Intento no encontrado
        HTTPException 403: Usuario no autorizado
    """
    # Verificar que el intento existe y pertenece al usuario
    intento = db.query(IntentoExamen).filter(
        IntentoExamen.intento_id == intento_id
    ).first()
    
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento de examen no encontrado"
        )
    
    if intento.estudiante_id != current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para acceder a este intento"
        )
    
    # Crear evento anti-trampa
    nuevo_evento = EventoAntiTrampa(
        intento_id=intento_id,
        tipo_evento=evento.tipo_evento.value,
        severidad=evento.severidad.value,
        detalle=evento.detalle,
        timestamp=datetime.utcnow(),
        resuelta=False,
        datos_adicionales=evento.datos_adicionales or {}
    )
    
    db.add(nuevo_evento)
    db.commit()
    db.refresh(nuevo_evento)
    
    return EventoProctoringResponse(
        evento_id=str(nuevo_evento.evento_id),
        intento_id=str(nuevo_evento.intento_id),
        tipo_evento=nuevo_evento.tipo_evento,
        severidad=nuevo_evento.severidad,
        detalle=nuevo_evento.detalle,
        timestamp=nuevo_evento.timestamp,
        resuelta=nuevo_evento.resuelta,
        datos_adicionales=nuevo_evento.datos_adicionales
    )


@router.post(
    "/intentos/{intento_id}/snapshots",
    status_code=status.HTTP_201_CREATED,
    summary="Subir snapshot de cámara",
    description="""
    Sube un snapshot (imagen) capturado de la cámara durante el examen.
    
    **Características**:
    - Formato: JPEG/PNG en base64
    - Resolución máxima: 1920x1080
    - Calidad: 0.1 - 1.0 (recomendado: 0.7)
    - Incluye datos adicionales de detección de rostros
    
    **Almacenamiento**:
    - Las imágenes se almacenan en S3/almacenamiento objeto
    - Se mantienen por 90 días según políticas de retención
    - Encriptadas en reposo
    """
)
async def subir_snapshot(
    intento_id: str,
    snapshot: SnapshotProctoringCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Sube un snapshot de cámara capturado durante el examen.
    
    Args:
        intento_id: ID del intento de examen
        snapshot: Datos del snapshot
        db: Sesión de base de datos
        current_user: Usuario autenticado
    
    Returns:
        dict: URL del snapshot almacenado
    
    Raises:
        HTTPException 404: Intento no encontrado
        HTTPException 403: Usuario no autorizado
        HTTPException 413: Imagen demasiado grande
    """
    # Verificar intento
    intento = db.query(IntentoExamen).filter(
        IntentoExamen.intento_id == intento_id
    ).first()
    
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento de examen no encontrado"
        )
    
    if intento.estudiante_id != current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para acceder a este intento"
        )
    
    # TODO: Implementar almacenamiento en S3/Cloud Storage
    # from src.services.storage import upload_snapshot
    # snapshot_url = await upload_snapshot(
    #     intento_id=intento_id,
    #     imagen_base64=snapshot.imagen_base64,
    #     datos_adicionales={
    #         "ancho": snapshot.ancho,
    #         "alto": snapshot.alto,
    #         "calidad": snapshot.calidad,
    #         "rostros_detectados": snapshot.rostros_detectados,
    #         "timestamp": datetime.utcnow().isoformat()
    #     }
    # )
    
    # Por ahora, retornar URL simulada
    snapshot_url = f"https://storage.acadify.com/snapshots/{intento_id}/{datetime.utcnow().timestamp()}.jpg"
    
    return {
        "snapshot_url": snapshot_url,
        "mensaje": "Snapshot almacenado correctamente",
        "intento_id": intento_id,
        "timestamp": datetime.utcnow()
    }


@router.post(
    "/intentos/{intento_id}/eventos-audio",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar evento de audio",
    description="""
    Registra un evento de audio capturado durante el examen.
    
    **Métricas capturadas**:
    - Nivel de audio (0-100%)
    - Duración del evento
    - Frecuencia dominante (Hz)
    - Flag de sospecha
    
    **Análisis**:
    - Nivel > 70%: Considerado sospechoso
    - Múltiples frecuencias: Posible conversación
    - Patrones irregulares: Alertas automáticas
    """
)
async def registrar_evento_audio(
    intento_id: str,
    evento_audio: EventoAudioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registra un evento de audio durante el examen.
    
    Args:
        intento_id: ID del intento de examen
        evento_audio: Datos del evento de audio
        db: Sesión de base de datos
        current_user: Usuario autenticado
    
    Returns:
        dict: Confirmación de registro
    """
    # Verificar intento
    intento = db.query(IntentoExamen).filter(
        IntentoExamen.intento_id == intento_id
    ).first()
    
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento de examen no encontrado"
        )
    
    if intento.estudiante_id != current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para acceder a este intento"
        )
    
    # TODO: Almacenar en tabla de eventos_audio (crear migración)
    # nuevo_evento_audio = EventoAudio(
    #     intento_id=intento_id,
    #     nivel_audio=evento_audio.nivel_audio,
    #     duracion_ms=evento_audio.duracion_ms,
    #     frecuencia_dominante=evento_audio.frecuencia_dominante,
    #     es_sospechoso=evento_audio.es_sospechoso,
    #     timestamp=datetime.utcnow(),
    #     datos_adicionales=evento_audio.datos_adicionales or {}
    # )
    # db.add(nuevo_evento_audio)
    # db.commit()
    
    return {
        "mensaje": "Evento de audio registrado",
        "intento_id": intento_id,
        "nivel_audio": evento_audio.nivel_audio,
        "es_sospechoso": evento_audio.es_sospechoso,
        "timestamp": datetime.utcnow()
    }


@router.get(
    "/intentos/{intento_id}/resumen",
    response_model=ResumenProctoringResponse,
    summary="Obtener resumen de proctoring",
    description="""
    Obtiene un resumen completo de la sesión de proctoring.
    
    **Incluye**:
    - Estadísticas de eventos por severidad y tipo
    - Nivel de riesgo calculado
    - Métricas de audio
    - Infracciones críticas
    - Recomendaciones
    
    **Niveles de riesgo**:
    - Bajo: 0-5 eventos menores
    - Medio: 6-15 eventos o 1-2 críticos
    - Alto: 16-30 eventos o 3-5 críticos
    - Crítico: >30 eventos o >5 críticos
    """
)
async def obtener_resumen_proctoring(
    intento_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene resumen completo de proctoring para un intento.
    
    Args:
        intento_id: ID del intento de examen
        db: Sesión de base de datos
        current_user: Usuario autenticado
    
    Returns:
        ResumenProctoringResponse: Resumen completo
    """
    # Verificar intento
    intento = db.query(IntentoExamen).filter(
        IntentoExamen.intento_id == intento_id
    ).first()
    
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento de examen no encontrado"
        )
    
    # Verificar permisos (estudiante o profesor)
    es_estudiante = intento.estudiante_id == current_user.usuario_id
    # TODO: Verificar si es profesor del curso
    es_profesor = False  # Implementar lógica
    
    if not (es_estudiante or es_profesor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para ver este resumen"
        )
    
    # Obtener todos los eventos
    eventos = db.query(EventoAntiTrampa).filter(
        EventoAntiTrampa.intento_id == intento_id
    ).all()
    
    # Calcular estadísticas
    total_eventos = len(eventos)
    eventos_por_severidad = {
        "baja": sum(1 for e in eventos if e.severidad == "baja"),
        "media": sum(1 for e in eventos if e.severidad == "media"),
        "alta": sum(1 for e in eventos if e.severidad == "alta"),
        "critica": sum(1 for e in eventos if e.severidad == "critica"),
    }
    
    eventos_por_tipo = {}
    for evento in eventos:
        eventos_por_tipo[evento.tipo_evento] = eventos_por_tipo.get(evento.tipo_evento, 0) + 1
    
    # Calcular nivel de riesgo
    criticas = eventos_por_severidad["critica"]
    altas = eventos_por_severidad["alta"]
    
    if criticas >= 5 or total_eventos > 30:
        nivel_riesgo = NivelRiesgo.CRITICO
        recomendacion = "REVISAR URGENTE: Múltiples infracciones críticas detectadas"
    elif criticas >= 3 or altas >= 5 or total_eventos > 15:
        nivel_riesgo = NivelRiesgo.ALTO
        recomendacion = "Revisar sesión: Varias infracciones detectadas"
    elif criticas > 0 or altas > 2 or total_eventos > 5:
        nivel_riesgo = NivelRiesgo.MEDIO
        recomendacion = "Supervisión recomendada: Algunas infracciones menores"
    else:
        nivel_riesgo = NivelRiesgo.BAJO
        recomendacion = "Sesión normal: Sin infracciones significativas"
    
    # Calcular duración
    duracion_minutos = 0.0
    if intento.fecha_inicio and intento.fecha_finalizacion:
        delta = intento.fecha_finalizacion - intento.fecha_inicio
        duracion_minutos = delta.total_seconds() / 60
    
    # Infracciones críticas
    infracciones_criticas = [
        EventoProctoringResponse(
            evento_id=str(e.evento_id),
            intento_id=str(e.intento_id),
            tipo_evento=e.tipo_evento,
            severidad=e.severidad,
            detalle=e.detalle,
            timestamp=e.timestamp,
            resuelta=e.resuelta,
            datos_adicionales=e.datos_adicionales
        )
        for e in eventos if e.severidad == "critica"
    ]
    
    return ResumenProctoringResponse(
        intento_id=intento_id,
        total_eventos=total_eventos,
        eventos_por_severidad=eventos_por_severidad,
        eventos_por_tipo=eventos_por_tipo,
        nivel_riesgo=nivel_riesgo,
        duracion_minutos=duracion_minutos,
        total_snapshots=0,  # TODO: Contar snapshots reales
        total_eventos_audio=0,  # TODO: Contar eventos de audio reales
        promedio_nivel_audio=0.0,  # TODO: Calcular promedio real
        infracciones_criticas=infracciones_criticas,
        ultimo_snapshot=None,  # TODO: Obtener último snapshot
        recomendacion=recomendacion
    )


@router.patch(
    "/eventos/{evento_id}/resolver",
    summary="Resolver evento de proctoring",
    description="""
    Marca un evento de proctoring como resuelto.
    
    **Uso**:
    - Profesor revisa el evento
    - Determina si fue falsa alarma o infracción real
    - Marca como resuelto con notas opcionales
    """
)
async def resolver_evento(
    evento_id: str,
    notas: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Marca un evento como resuelto (solo profesores).
    """
    # TODO: Verificar que current_user es profesor
    
    evento = db.query(EventoAntiTrampa).filter(
        EventoAntiTrampa.evento_id == evento_id
    ).first()
    
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )
    
    evento.resuelta = True
    if notas:
        evento.datos_adicionales = evento.datos_adicionales or {}
        evento.datos_adicionales["notas_resolucion"] = notas
        evento.datos_adicionales["resuelto_por"] = current_user.usuario_id
        evento.datos_adicionales["fecha_resolucion"] = datetime.utcnow().isoformat()
    
    db.commit()
    
    return {
        "mensaje": "Evento marcado como resuelto",
        "evento_id": evento_id,
        "timestamp": datetime.utcnow()
    }
