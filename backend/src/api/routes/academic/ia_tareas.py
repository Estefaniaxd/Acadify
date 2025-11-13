"""API Routes para el Sistema de IA y Gamificación en Tareas.

Este módulo proporciona endpoints para:
- Entrega de tareas con análisis automático de IA
- Obtención de retroalimentación de IA
- Consulta de puntos y gamificación de usuarios
- Rankings y leaderboards

Autor: Acadify Team
Fecha: 2024
"""

import logging
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from src.api.deps import (
    get_current_active_user,
    get_current_docente_or_coordinador,
    get_current_estudiante,
    get_db,
)
from src.models.users.usuario import Usuario
from src.schemas.ai_schemas import (
    ArchivoMetadata,
    EntregaConIAResponse,
    PuntosUsuarioResponse,
    RankingResponse,
)
from src.services.academic.tarea_service import TareaService
from src.services.gamification.puntos_service import PuntosService


logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter()


# =============================================================================
# HELPER FUNCTIONS - Validación y procesamiento de archivos
# =============================================================================


async def _validar_y_procesar_archivo(
    archivo: UploadFile | None,
) -> tuple[bytes | None, ArchivoMetadata | None]:
    """Valida y procesa el archivo subido.

    Returns:
        Tuple (archivo_binario, archivo_metadata)
    """
    if not archivo:
        return None, None

    # Validar tamaño (50MB máximo)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    # Leer archivo
    archivo_binario = await archivo.read()
    tamano_bytes = len(archivo_binario)

    if tamano_bytes > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo excede el tamaño máximo permitido (50MB). Tamaño actual: {tamano_bytes / (1024*1024):.2f}MB",
        )

    if tamano_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo está vacío"
        )

    # Validar MIME type
    MIME_TYPES_PERMITIDOS = [
        # Documentos
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/msword",  # .doc
        "text/plain",
        # Hojas de cálculo
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/vnd.ms-excel",  # .xls
        # Presentaciones
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
        "application/vnd.ms-powerpoint",  # .ppt
        # Imágenes
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/gif",
        "image/webp",
        # Código fuente
        "text/x-python",
        "application/x-python",
        "text/javascript",
        "application/javascript",
        "text/html",
        "text/css",
        "application/json",
        "application/xml",
        "text/xml",
        # Comprimidos
        "application/zip",
        "application/x-zip-compressed",
    ]

    mime_type = archivo.content_type
    if mime_type not in MIME_TYPES_PERMITIDOS:
        logger.warning(f"MIME type no permitido: {mime_type}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no soportado: {mime_type}. Formatos permitidos: PDF, Word, Excel, PowerPoint, imágenes, código fuente.",
        )

    # Crear metadata
    metadata = ArchivoMetadata(
        nombre=archivo.filename, mime_type=mime_type, tamaño_bytes=tamano_bytes
    )

    logger.info(
        f"Archivo procesado: {archivo.filename} ({tamano_bytes / 1024:.2f}KB, {mime_type})"
    )

    return archivo_binario, metadata


def _validar_contenido_entrega(
    contenido_texto: str | None, archivo: UploadFile | None
) -> None:
    """Valida que la entrega tenga al menos contenido de texto o archivo."""
    if not contenido_texto and not archivo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes proporcionar contenido de texto o un archivo para la entrega",
        )

    if contenido_texto and len(contenido_texto.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contenido de texto no puede estar vacío",
        )


# =============================================================================
# ENDPOINTS - Entregas de tareas con IA
# =============================================================================


@router.post(
    "/cursos/{curso_id}/tareas/{tarea_id}/entregas",
    response_model=EntregaConIAResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Entregar tarea con análisis de IA",
    description="""
    Permite a un estudiante entregar una tarea para ser analizada automáticamente con IA.

    **Proceso completo**:
    1. Valida la tarea y permisos del estudiante
    2. Guarda la entrega en la base de datos
    3. Analiza el contenido con Google Gemini AI
    4. Calcula puntos según rúbrica y rendimiento
    5. Otorga puntos al estudiante (gamificación)
    6. Verifica y otorga insignias automáticas
    7. Retorna retroalimentación completa con análisis de IA

    **Entrada**:
    - `contenido_texto`: Texto de la entrega (opcional si hay archivo)
    - `archivo`: Archivo adjunto (opcional si hay texto)
    - Al menos uno de los dos debe estar presente

    **Salida**:
    - Retroalimentación detallada de IA con fortalezas, áreas de mejora y sugerencias
    - Puntos otorgados con desglose completo
    - Información de gamificación: nivel actual, progreso, nuevas insignias

    **Permisos**: Solo estudiantes inscritos en el curso

    **Límites**:
    - Tamaño máximo de archivo: 50MB
    - Texto máximo: 50,000 caracteres
    - Formatos soportados: PDF, Word, Excel, PowerPoint, imágenes, código
    """,
    responses={
        201: {
            "description": "Entrega procesada exitosamente con análisis de IA",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Entrega procesada exitosamente con IA. ¡Felicidades! Has obtenido 70 puntos.",
                        "data": {
                            "entrega_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                            "intentos": 1,
                            "es_tardia": False,
                            "fecha_entrega": "2024-01-20T15:30:00Z",
                            "retroalimentacion_ia": {
                                "analisis_general": "Excelente trabajo. El código está bien estructurado...",
                                "calificacion": 4.2,
                                "fortalezas": [
                                    "Código limpio y legible",
                                    "Buena documentación",
                                ],
                                "areas_mejora": [
                                    "Agregar más validaciones de entrada",
                                    "Mejorar manejo de errores",
                                ],
                            },
                            "puntos": {
                                "puntos_base": 50,
                                "puntos_bonificacion": 20,
                                "puntos_totales": 70,
                                "desglose": "50 (base) + 20 (bonus excelencia)",
                            },
                            "gamificacion": {
                                "puntos_otorgados": 70,
                                "puntos_acumulados": 170,
                                "nivel_actual": "Bronce II",
                                "progreso_siguiente_nivel": 68.0,
                                "nuevas_insignias": [
                                    {
                                        "insignia_id": "primera-entrega",
                                        "nombre": "Primera Entrega",
                                        "descripcion": "Completaste tu primera tarea",
                                    }
                                ],
                            },
                        },
                    }
                }
            },
        },
        400: {"description": "Datos inválidos o entrega vacía"},
        403: {"description": "No tienes permisos para entregar esta tarea"},
        404: {"description": "Tarea no encontrada"},
        413: {"description": "Archivo muy grande (máximo 50MB)"},
        415: {"description": "Tipo de archivo no soportado"},
    },
    tags=["IA y Gamificación"],
)
async def entregar_tarea_con_ia(
    curso_id: str,
    tarea_id: str,
    contenido_texto: str | None = Form(None, max_length=50000),
    archivo: UploadFile | None = File(None),
    current_user: Usuario = Depends(get_current_estudiante),
    db: Session = Depends(get_db),
):
    """Endpoint para que un estudiante entregue una tarea con análisis automático de IA."""
    try:
        logger.info(
            f"Procesando entrega de tarea {tarea_id} del estudiante {current_user.usuario_id}"
        )

        # 1. Validar que hay contenido
        _validar_contenido_entrega(contenido_texto, archivo)

        # 2. Procesar archivo si existe
        archivo_binario, archivo_metadata = await _validar_y_procesar_archivo(archivo)

        # 3. Procesar entrega con IA (orquestación completa)
        tarea_service = TareaService()
        resultado = await tarea_service.procesar_entrega_con_ia(
            db=db,
            tarea_id=tarea_id,
            estudiante_id=current_user.usuario_id,
            contenido_texto=contenido_texto,
            archivo_binario=archivo_binario,
            archivo_metadata=archivo_metadata.dict() if archivo_metadata else None,
        )

        # 4. Construir respuesta
        response = EntregaConIAResponse(**resultado)

        logger.info(f"Entrega procesada exitosamente: {response.data.entrega_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando entrega con IA: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la entrega: {e!s}",
        ) from e


@router.get(
    "/entregas/{entrega_id}/retroalimentacion",
    response_model=EntregaConIAResponse,
    summary="Obtener retroalimentación de IA",
    description="""
    Obtiene la retroalimentación completa de IA para una entrega específica.

    **Permisos**:
    - Estudiantes: Solo pueden ver su propia retroalimentación
    - Docentes/Coordinadores: Pueden ver retroalimentación de cualquier entrega

    **Retorna**:
    - Análisis completo de IA
    - Puntos otorgados
    - Información de gamificación
    """,
    responses={
        200: {"description": "Retroalimentación obtenida exitosamente"},
        403: {"description": "No tienes permisos para ver esta retroalimentación"},
        404: {"description": "Entrega no encontrada o sin retroalimentación de IA"},
    },
    tags=["IA y Gamificación"],
)
async def obtener_retroalimentacion_ia(
    entrega_id: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Endpoint para obtener la retroalimentación de IA de una entrega."""
    try:
        logger.info(
            f"Obteniendo retroalimentación de entrega {entrega_id} para usuario {current_user.usuario_id}"
        )

        tarea_service = TareaService()
        resultado = await tarea_service.obtener_retroalimentacion_ia(
            db=db, entrega_id=entrega_id, usuario=current_user
        )

        return EntregaConIAResponse(**resultado)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo retroalimentación: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener retroalimentación: {e!s}",
        ) from e


# =============================================================================
# ENDPOINTS - Gamificación y Puntos
# =============================================================================


@router.get(
    "/usuarios/{usuario_id}/puntos",
    response_model=PuntosUsuarioResponse,
    summary="Obtener información de puntos de un usuario",
    description="""
    Obtiene la información completa de gamificación de un usuario.

    **Incluye**:
    - Puntos acumulados totales
    - Nivel actual (Bronce I - Platino III)
    - Información detallada del nivel: progreso, puntos para siguiente nivel
    - Historial reciente de cambios de puntos
    - Insignias obtenidas

    **Permisos**:
    - Estudiantes: Solo pueden ver sus propios puntos
    - Docentes/Coordinadores: Pueden ver puntos de cualquier usuario
    """,
    responses={
        200: {"description": "Información de puntos obtenida exitosamente"},
        403: {"description": "No tienes permisos para ver estos puntos"},
        404: {"description": "Usuario no encontrado"},
    },
    tags=["IA y Gamificación"],
)
async def obtener_puntos_usuario(
    usuario_id: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Endpoint para obtener información completa de puntos de un usuario."""
    try:
        # Validar permisos
        es_docente = current_user.rol.value in [
            "docente",
            "coordinador",
            "administrador",
        ]
        if not es_docente and str(current_user.usuario_id) != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver los puntos de otro usuario",
            )

        logger.info(f"Obteniendo puntos del usuario {usuario_id}")

        puntos_service = PuntosService(db)
        usuario_uuid = UUID(usuario_id)
        resultado = await puntos_service.obtener_puntos_usuario(usuario_id=usuario_uuid)

        return PuntosUsuarioResponse(**resultado)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo puntos de usuario: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener puntos: {e!s}",
        ) from e


@router.get(
    "/usuarios/ranking",
    response_model=RankingResponse,
    summary="Obtener ranking de usuarios por puntos",
    description="""
    Obtiene el ranking global de usuarios ordenado por puntos acumulados.

    **Parámetros**:
    - `limite`: Número de usuarios a retornar (1-100, por defecto 10)
    - `offset`: Posición inicial para paginación (por defecto 0)

    **Retorna**:
    - Lista de usuarios con su posición, nombre, puntos y nivel
    - Total de usuarios en el ranking

    **Permisos**: Cualquier usuario autenticado puede ver el ranking
    """,
    responses={
        200: {
            "description": "Ranking obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "posicion": 1,
                                "usuario_id": "uuid-123",
                                "nombre_completo": "María García",
                                "puntos": 5250,
                                "nivel": "Oro II",
                            },
                            {
                                "posicion": 2,
                                "usuario_id": "uuid-456",
                                "nombre_completo": "Juan Pérez",
                                "puntos": 3800,
                                "nivel": "Plata III",
                            },
                        ],
                        "total": 150,
                    }
                }
            },
        }
    },
    tags=["IA y Gamificación"],
)
async def obtener_ranking_puntos(
    limite: int = Query(10, ge=1, le=100, description="Número de usuarios a retornar"),
    offset: int = Query(0, ge=0, description="Posición inicial para paginación"),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Endpoint para obtener el ranking global de usuarios por puntos."""
    try:
        logger.info(f"Obteniendo ranking: limite={limite}, offset={offset}")

        puntos_service = PuntosService(db)
        resultado = await puntos_service.obtener_ranking(limite=limite, offset=offset)

        return RankingResponse(**resultado)

    except Exception as e:
        logger.error(f"Error obteniendo ranking: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ranking: {e!s}",
        ) from e


@router.get(
    "/usuarios/mi-ranking",
    response_model=dict,
    summary="Obtener mi posición en el ranking",
    description="""
    Obtiene la posición del usuario actual en el ranking global.

    **Retorna**:
    - Posición actual en el ranking
    - Puntos acumulados
    - Nivel actual
    - Diferencia de puntos con el usuario anterior
    - Diferencia de puntos con el siguiente usuario
    """,
    responses={
        200: {
            "description": "Posición en ranking obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "posicion": 15,
                            "puntos": 1450,
                            "nivel": "Bronce III",
                            "puntos_hasta_anterior": 150,
                            "puntos_hasta_siguiente": 50,
                            "total_usuarios": 150,
                        },
                    }
                }
            },
        }
    },
    tags=["IA y Gamificación"],
)
async def obtener_mi_posicion_ranking(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Endpoint para obtener la posición del usuario actual en el ranking."""
    try:
        logger.info(
            f"Obteniendo posición en ranking del usuario {current_user.usuario_id}"
        )

        puntos_service = PuntosService(db)
        resultado = await puntos_service.obtener_posicion_usuario(
            usuario_id=str(current_user.usuario_id)
        )

        return {"success": True, "data": resultado}

    except Exception as e:
        logger.error(f"Error obteniendo posición en ranking: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener posición: {e!s}",
        ) from e


# =============================================================================
# ENDPOINTS - Estadísticas (Docentes)
# =============================================================================


@router.get(
    "/cursos/{curso_id}/tareas/{tarea_id}/estadisticas-ia",
    summary="Obtener estadísticas de IA de una tarea",
    description="""
    Obtiene estadísticas agregadas del análisis de IA para todas las entregas de una tarea.

    **Solo para docentes y coordinadores**

    **Incluye**:
    - Calificación promedio de IA
    - Distribución de calificaciones
    - Fortalezas más comunes identificadas
    - Áreas de mejora más frecuentes
    - Puntos promedio otorgados
    """,
    responses={
        200: {"description": "Estadísticas obtenidas exitosamente"},
        403: {"description": "Solo docentes pueden ver estas estadísticas"},
        404: {"description": "Tarea no encontrada"},
    },
    tags=["IA y Gamificación"],
)
async def obtener_estadisticas_ia_tarea(
    curso_id: str,
    tarea_id: str,
    current_user: Usuario = Depends(get_current_docente_or_coordinador),
    db: Session = Depends(get_db),
):
    """Endpoint para obtener estadísticas de IA de una tarea (solo docentes)."""
    try:
        logger.info(f"Obteniendo estadísticas de IA para tarea {tarea_id}")

        tarea_service = TareaService()
        resultado = tarea_service.obtener_estadisticas_ia_tarea(
            db=db, tarea_id=tarea_id, docente_id=current_user.usuario_id
        )

        return {"success": True, "data": resultado}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de IA: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {e!s}",
        ) from e


# =============================================================================
# HEALTH CHECK
# =============================================================================


@router.get(
    "/ia/health",
    summary="Verificar estado del sistema de IA",
    description="Verifica que el sistema de IA y gamificación esté funcionando correctamente",
    tags=["IA y Gamificación"],
)
async def health_check_ia():
    """Health check para el sistema de IA y gamificación."""
    return {
        "success": True,
        "message": "Sistema de IA y Gamificación operativo",
        "services": {
            "gemini_ai": "operativo",
            "gamificacion": "operativo",
            "puntos": "operativo",
        },
    }


# =============================================================================
# CONFIGURACIÓN DEL ROUTER
# =============================================================================

# Logging de rutas registradas
logger.info(f"✅ Router IA y Gamificación cargado con {len(router.routes)} rutas")
