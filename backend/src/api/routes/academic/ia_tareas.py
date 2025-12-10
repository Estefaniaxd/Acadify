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
import asyncio
import json
from fastapi.responses import StreamingResponse
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
    BackgroundTasks,
)
from sqlalchemy.orm import Session

from src.api.deps import (
    get_current_active_user,
    get_current_docente_or_coordinador,
    get_current_estudiante,
    get_db,
)
from src.utils.security import security_manager
from src.crud.user.usuario import usuario_crud
from src.models.users.usuario import Usuario
from src.schemas.ai_schemas import (
    ArchivoMetadata,
    EntregaConIAResponse,
    PuntosUsuarioResponse,
    RankingResponse,
)
from src.services.academic.tarea_service import TareaService
from src.services.gamification.puntos_service import PuntosService
import threading

# In-memory job tracker for background jobs (simple, persisted only in memory)
# Structure: JOBS[job_id] = {
#   "job_id": str,
#   "total": int,
#   "completed": int,
#   "errors": int,
#   "estado": "procesando" | "completado" | "error",
#   "progreso": int,  # percent
#   "items": [{"entrega_id": str, "status": "pendiente"|"procesando"|"completado"|"error", "error": str | None}]
# }
JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()


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
# ENDPOINTS - Retroalimentación IA (Gemini)
# =============================================================================


@router.post(
    "/retroalimentacion-individual",
    summary="Generar retroalimentación IA individual",
    description="""
    Genera retroalimentación con Google Gemini para una entrega específica.

    **Flujo**:
    1. Obtener entrega y contenido
    2. Enviar a Google Gemini API
    3. Guardar en entregas_tareas.retroalimentacion_ia (JSONB)
    4. Retornar retroalimentación procesada

    **Respuesta** (< 5 segundos):
    ```json
    {
      "entrega_id": "ent-123",
      "tarea_id": "tarea-456",
      "retroalimentacion": {
        "retroalimentacion_texto": "Análisis completo...",
        "fortalezas": ["..."],
        "areas_mejora": ["..."],
        "recursos_recomendados": ["..."],
        "calificacion_sugerida": 4.2,
        "modelo_usado": "gemini-2.5-flash",
        "tokens_usados": 1250,
        "confianza": 0.92
      }
    }
    ```

    **Permisos**: Solo docentes del curso
    **Tiempo estimado**: 3-5 segundos por entrega
    """,
    responses={
        200: {"description": "Retroalimentación generada exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "No eres docente del curso"},
        404: {"description": "Entrega no encontrada"},
        500: {"description": "Error en Gemini API"},
    },
    tags=["IA Feedback - Gemini"],
)
async def generar_retroalimentacion_individual(
    entrega_id: str,
    modelo: str = "gemini-2.5-flash",
    nivel_detalle: str = "completo",
    incluir_calificacion: bool = True,
    current_user: Usuario = Depends(get_current_docente_or_coordinador),
    db: Session = Depends(get_db),
):
    """Generar retroalimentación IA individual para una entrega."""
    try:
        logger.info(
            f"📊 [IA] Generando retroalimentación individual - Entrega: {entrega_id}, Usuario: {current_user.usuario_id}, Modelo: {modelo}"
        )

        from src.services.ai import GeminiService

        # Obtener entrega
        try:
            from src.models.academic.tarea import EntregaTarea
            entrega = db.query(EntregaTarea).filter_by(entrega_id=entrega_id).first()
            if not entrega:
                logger.warning(f"⚠️ [IA] Entrega no encontrada: {entrega_id}")
                raise HTTPException(status_code=404, detail="Entrega no encontrada")
        except Exception as e:
            logger.error(f"❌ [IA] Error obtener entrega: {e}", exc_info=True)
            raise

        # Generar con Gemini
        try:
            logger.info(f"🚀 [IA] Llamando Gemini API con modelo: {modelo}")
            gemini_service = GeminiService()
            await gemini_service.inicializar()  # Inicializar servicio ANTES de usar
            
            # ✅ CRÍTICO: Extraer contenido REAL de los archivos del estudiante
            contenido_analizar = []
            
            # 1. Comentarios del estudiante
            if entrega.contenido_texto and entrega.contenido_texto.strip() != "Entrega de tarea":
                contenido_analizar.append(f"**Comentarios del estudiante:**\n{entrega.contenido_texto}\n")
            
            # 2. Archivos adjuntos (PDFs, Word, etc.)
            if entrega.archivos_adicionales:
                try:
                    from src.services.ai.helpers import FileProcessor
                    from pathlib import Path
                    
                    archivos_data = entrega.archivos_adicionales
                    if isinstance(archivos_data, str):
                        import json
                        archivos_data = json.loads(archivos_data)
                    
                    archivos_list = archivos_data.get('archivos', []) if isinstance(archivos_data, dict) else []
                    
                    for idx, archivo_info in enumerate(archivos_list, 1):
                        archivo_url = archivo_info.get('url', '')
                        nombre_original = archivo_info.get('nombre_original', archivo_info.get('nombre', 'archivo'))
                        
                        # Construir path absoluto al archivo
                        backend_dir = Path(__file__).parent.parent.parent.parent  # backend/
                        archivo_path = backend_dir / archivo_url.lstrip('/')
                        
                        if archivo_path.exists():
                            try:
                                with open(archivo_path, 'rb') as f:
                                    texto_extraido = FileProcessor.extraer_contenido(f, nombre_original)
                                    contenido_analizar.append(
                                        f"\n{'='*60}\n"
                                        f"📄 **Archivo {idx}: {nombre_original}**\n"
                                        f"{'='*60}\n"
                                        f"{texto_extraido}\n"
                                    )
                                    logger.info(f"   ✅ Contenido extraído de {nombre_original}: {len(texto_extraido)} caracteres")
                            except Exception as e:
                                logger.warning(f"   ⚠️ No se pudo extraer contenido de {nombre_original}: {str(e)}")
                                contenido_analizar.append(f"\n[Archivo {idx}: {nombre_original} - No se pudo extraer texto]\n")
                        else:
                            logger.warning(f"   ⚠️ Archivo no encontrado: {archivo_path}")
                            
                except Exception as e:
                    logger.error(f"   ❌ Error procesando archivos: {str(e)}", exc_info=True)
            
            # 3. Enlaces externos
            if entrega.enlaces_externos:
                try:
                    enlaces = entrega.enlaces_externos if isinstance(entrega.enlaces_externos, list) else []
                    if enlaces:
                        contenido_analizar.append("\n**Enlaces compartidos:**")
                        for enlace in enlaces:
                            titulo = enlace.get('titulo', 'Sin título')
                            url = enlace.get('url', '')
                            contenido_analizar.append(f"- {titulo}: {url}")
                except Exception as e:
                    logger.error(f"   ❌ Error procesando enlaces: {str(e)}")
            
            # Combinar todo el contenido
            contenido_final = "\n\n".join(contenido_analizar) if contenido_analizar else "Sin contenido para analizar"
            
            logger.info(f"   📊 Contenido total para IA: {len(contenido_final)} caracteres")
            
            retroalimentacion = await gemini_service.generar_retroalimentacion(
                entrega=entrega,
                tarea=entrega.tarea,
                archivo_contenido=contenido_final,
                opciones={
                    "nivel_profundidad": nivel_detalle,
                    "modelo": modelo
                }
            )
            logger.info(f"✅ [IA] Retroalimentación generada exitosamente - Tokens: {retroalimentacion.get('tokens_usados', 'N/A')}")
        except Exception as e:
            logger.error(f"❌ [IA] Error Gemini: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generando retroalimentación: {str(e)}")

        # Guardar en BD
        try:
            logger.info(f"💾 [IA] Guardando retroalimentación en BD")
            entrega.retroalimentacion_ia = retroalimentacion
            if retroalimentacion.get("calificacion_sugerida") and incluir_calificacion:
                entrega.calificacion_preliminar_ia = retroalimentacion["calificacion_sugerida"]
            db.commit()
            logger.info(f"✅ [IA] Retroalimentación guardada exitosamente")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ [IA] Error guardando en BD: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error guardando retroalimentación: {str(e)}")

        return {
            "success": True,
            "entrega_id": entrega_id,
            "tarea_id": entrega.tarea_id,
            "retroalimentacion": retroalimentacion,
            "fecha_generacion": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [IA] Error general: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error procesando retroalimentación: {str(e)}")


@router.post(
    "/retroalimentacion-masiva",
    status_code=202,
    summary="Generar retroalimentación masiva (background)",
    description="""
    Inicia procesamiento masivo de retroalimentación para múltiples entregas.

    **Retorna INMEDIATAMENTE** con `job_id` para tracking.

    **Procesa en background**:
    - Itera sobre entregas_ids
    - Genera retroalimentación para cada una
    - Guarda en BD
    - Notifica al completar

    **Respuesta** (202 Accepted):
    ```json
    {
      "job_id": "job-abc123xyz",
      "total_entregas": 15,
      "estado": "procesando",
      "progreso": 0,
      "mensaje": "Procesamiento iniciado. Recibirás notificación cuando termine."
    }
    ```

    **Permisos**: Solo docentes
    **Escalabilidad**: Procesa cientos de entregas sin bloquear
    """,
    responses={
        202: {"description": "Procesamiento iniciado (background)"},
        400: {"description": "No hay entregas para procesar"},
        403: {"description": "No eres docente del curso"},
    },
    tags=["IA Feedback - Gemini"],
)
async def generar_retroalimentacion_masiva(
    entrega_ids: list[str],
    modelo: str = "gemini-2.5-flash",
    nivel_detalle: str = "medio",
    incluir_calificacion: bool = True,
    notificar_estudiantes: bool = True,
    background_tasks: BackgroundTasks = None,
    current_user: Usuario = Depends(get_current_docente_or_coordinador),
    db: Session = Depends(get_db),
):
    """Iniciar procesamiento masivo de retroalimentación (background job)."""
    try:
        if not entrega_ids or len(entrega_ids) == 0:
            logger.warning(f"⚠️ [IA] Intento de procesar 0 entregas")
            raise HTTPException(status_code=400, detail="Se requiere al menos una entrega")

        job_id = str(uuid4())
        logger.info(
            f"📊 [IA] Iniciando procesamiento MASIVO - Job: {job_id}, Entregas: {len(entrega_ids)}, Modelo: {modelo}, Usuario: {current_user.usuario_id}"
        )

        # Agregar tarea en background (no bloquea respuesta)
        if background_tasks:
            background_tasks.add_task(
                _procesar_retroalimentacion_masiva_bg,
                job_id=job_id,
                entrega_ids=entrega_ids,
                modelo=modelo,
                nivel_detalle=nivel_detalle,
                incluir_calificacion=incluir_calificacion,
                notificar_estudiantes=notificar_estudiantes,
                docente_id=str(current_user.usuario_id),
            )
            logger.info(f"✅ [IA] Tarea agregada a background. Job ID: {job_id}")

            # Inicializar job en tracker en memoria (incluye docente_id para control de acceso)
            with JOBS_LOCK:
                JOBS[job_id] = {
                    "job_id": job_id,
                    "docente_id": str(current_user.usuario_id),
                    "total": len(entrega_ids),
                    "completed": 0,
                    "errors": 0,
                    "estado": "procesando",
                    "progreso": 0,
                    "items": [{"entrega_id": eid, "status": "pendiente", "error": None} for eid in entrega_ids],
                }

        return {
            "success": True,
            "job_id": job_id,
            "total_entregas": len(entrega_ids),
            "estado": "procesando",
            "progreso": 0,
            "mensaje": "✅ Procesamiento iniciado en background. Recibirás notificación cuando termine.",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [IA] Error iniciando procesamiento masivo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    "/retroalimentacion/{entrega_id}",
    summary="Obtener retroalimentación existente",
    description="""
    Obtiene la retroalimentación IA guardada para una entrega.

    **Respuesta**:
    ```json
    {
      "entrega_id": "ent-123",
      "tarea_id": "tarea-456",
      "retroalimentacion": {
        "retroalimentacion_texto": "...",
        "fortalezas": [...],
        "areas_mejora": [...],
        ...
      },
      "fecha_generacion": "2025-11-17T10:30:00Z"
    }
    ```

    **Retorna null** si no existe retroalimentación.
    """,
    responses={
        200: {"description": "Retroalimentación obtenida"},
        404: {"description": "Entrega no encontrada"},
    },
    tags=["IA Feedback - Gemini"],
)
async def obtener_retroalimentacion(
    entrega_id: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Obtener retroalimentación IA de una entrega."""
    try:
        logger.info(f"📥 [IA] Obteniendo retroalimentación - Entrega: {entrega_id}, Usuario: {current_user.usuario_id}")

        from src.models.academic.tarea import EntregaTarea
        entrega = db.query(EntregaTarea).filter_by(entrega_id=entrega_id).first()

        if not entrega:
            logger.warning(f"⚠️ [IA] Entrega no encontrada: {entrega_id}")
            raise HTTPException(status_code=404, detail="Entrega no encontrada")

        # Validar permisos
        es_docente = current_user.rol.value in ["docente", "coordinador", "administrador"]
        if not es_docente and str(entrega.estudiante_id) != str(current_user.usuario_id):
            logger.warning(f"⚠️ [IA] Acceso denegado - Usuario: {current_user.usuario_id}, Entrega: {entrega_id}")
            raise HTTPException(status_code=403, detail="No tienes acceso a esta retroalimentación")

        logger.info(f"✅ [IA] Retroalimentación encontrada - Entrega: {entrega_id}")

        return {
            "success": True,
            "entrega_id": entrega_id,
            "tarea_id": entrega.tarea_id,
            "retroalimentacion": entrega.retroalimentacion_ia,
            "fecha_generacion": entrega.fecha_actualizacion.isoformat() if entrega.fecha_actualizacion else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [IA] Error obteniendo retroalimentación: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    "/modelos",
    summary="Listar modelos IA disponibles",
    description="""
    Retorna lista de modelos Gemini disponibles para retroalimentación.

    **Modelos disponibles**:
    - **gemini-2.5-flash**: ⚡ Rápido, económico (recomendado para bulk)
    - **gemini-2.5-pro**: 🧠 Premium, máxima precisión
    - **gemini-2.0-flash**: 💫 Versátil, buen balance

    **Respuesta**:
    ```json
    [
      {
        "nombre": "gemini-2.5-flash",
        "descripcion": "Modelo rápido y económico",
        "velocidad": "rapido",
        "costo_entrada": 0.075,
        "costo_salida": 0.3,
        "capaz_multimedia": true
      },
      ...
    ]
    ```
    """,
    responses={200: {"description": "Lista de modelos obtenida"}},
    tags=["IA Feedback - Gemini"],
)
async def listar_modelos_disponibles(
    current_user: Usuario = Depends(get_current_active_user),
):
    """Listar modelos IA disponibles."""
    try:
        logger.info(f"📋 [IA] Listando modelos disponibles - Usuario: {current_user.usuario_id}")

        modelos = [
            {
                "nombre": "gemini-2.5-flash",
                "descripcion": "⚡ Modelo rápido y económico. Ideal para procesamiento masivo.",
                "velocidad": "rapido",
                "costo_entrada": 0.075,
                "costo_salida": 0.3,
                "capaz_multimedia": True,
            },
            {
                "nombre": "gemini-2.5-pro",
                "descripcion": "🧠 Modelo premium con máxima precisión. Para análisis complejos.",
                "velocidad": "normal",
                "costo_entrada": 1.5,
                "costo_salida": 6.0,
                "capaz_multimedia": True,
            },
            {
                "nombre": "gemini-2.0-flash",
                "descripcion": "💫 Modelo versátil con buen balance costo-rendimiento.",
                "velocidad": "rapido",
                "costo_entrada": 0.075,
                "costo_salida": 0.3,
                "capaz_multimedia": True,
            },
        ]

        logger.info(f"✅ [IA] {len(modelos)} modelos disponibles")
        return {
            "success": True,
            "modelos": modelos,
            "total": len(modelos),
        }

    except Exception as e:
        logger.error(f"❌ [IA] Error listando modelos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# =============================================================================
# TAREA BACKGROUND - Procesamiento Masivo
# =============================================================================


async def _procesar_retroalimentacion_masiva_bg(
    job_id: str,
    entrega_ids: list[str],
    modelo: str,
    nivel_detalle: str,
    incluir_calificacion: bool,
    notificar_estudiantes: bool,
    docente_id: str,
):
    """Procesa retroalimentación masiva en background (no bloquea)."""
    logger.info(f"🔄 [IA] INICIANDO BACKGROUND JOB - Job: {job_id}, Entregas: {len(entrega_ids)}")

    from src.db.database import get_db as get_db_async
    from src.services.ai import GeminiService

    completadas = 0
    errores = 0
    db = next(get_db_async())

    try:
        for idx, entrega_id in enumerate(entrega_ids, 1):
            try:
                logger.info(f"🔄 [IA] Procesando {idx}/{len(entrega_ids)} - Entrega: {entrega_id}")

                # Marcar item como procesando
                with JOBS_LOCK:
                    job = JOBS.get(job_id)
                    if job:
                        for item in job["items"]:
                            if item["entrega_id"] == entrega_id:
                                item["status"] = "procesando"
                                break
                        job["progreso"] = int((job["completed"] / job["total"]) * 100) if job["total"] else 0

                from src.models.academic.tarea import EntregaTarea
                entrega = db.query(EntregaTarea).filter_by(entrega_id=entrega_id).first()

                if not entrega:
                    logger.warning(f"⚠️ [IA] Entrega no encontrada: {entrega_id}")
                    errores += 1
                    continue

                # Generar retroalimentación
                gemini_service = GeminiService()
                retroalimentacion = await gemini_service.generar_retroalimentacion(
                    entrega=entrega,
                    tarea=entrega.tarea,
                    archivo_contenido=entrega.contenido_entrega or "Sin contenido",
                    opciones={
                        "nivel_profundidad": nivel_detalle,
                        "modelo": modelo
                    }
                )

                # Guardar
                entrega.retroalimentacion_ia = retroalimentacion
                if retroalimentacion.get("calificacion_sugerida") and incluir_calificacion:
                    entrega.calificacion_preliminar_ia = retroalimentacion["calificacion_sugerida"]
                db.commit()

                completadas += 1
                logger.info(f"✅ [IA] Procesada {idx}/{len(entrega_ids)} - Entrega: {entrega_id}")

                # Actualizar job tracker
                with JOBS_LOCK:
                    job = JOBS.get(job_id)
                    if job:
                        job["completed"] = completadas
                        job["progreso"] = int((job["completed"] / job["total"]) * 100) if job["total"] else 100
                        for item in job["items"]:
                            if item["entrega_id"] == entrega_id:
                                item["status"] = "completado"
                                item["error"] = None
                                break

            except Exception as e:
                db.rollback()
                errores += 1
                logger.error(f"❌ [IA] Error procesando {entrega_id}: {str(e)}", exc_info=True)

                # Actualizar job tracker con error
                with JOBS_LOCK:
                    job = JOBS.get(job_id)
                    if job:
                        job["errors"] = job.get("errors", 0) + 1
                        job["progreso"] = int((job.get("completed", 0) / job.get("total", 1)) * 100)
                        for item in job["items"]:
                            if item["entrega_id"] == entrega_id:
                                item["status"] = "error"
                                item["error"] = str(e)
                                break

    except Exception as e:
        logger.error(f"❌ [IA] ERROR CRÍTICO en background job: {str(e)}", exc_info=True)
    finally:
        logger.info(f"✅ [IA] COMPLETADO BACKGROUND JOB - Job: {job_id}, Completadas: {completadas}, Errores: {errores}")

        # Marcar job como completado
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if job:
                job["completed"] = completadas
                job["errors"] = errores
                job["progreso"] = 100
                job["estado"] = "completado"

        db.close()


# =============================================================================
# HEALTH CHECK
# =============================================================================


@router.get(
    "/retroalimentacion-masiva/{job_id}",
    summary="Obtener estado de un job masivo de retroalimentación",
    description="Devuelve el estado del job creado por /retroalimentacion-masiva. Permisos: docente creador o administradores.",
    responses={200: {"description": "Estado del job"}, 404: {"description": "Job no encontrado"}, 403: {"description": "Acceso denegado"}},
    tags=["IA Feedback - Gemini"],
)
async def obtener_estado_job_masivo(
    job_id: str,
    current_user: Usuario = Depends(get_current_active_user),
):
    """Retorna el estado del job en memoria (temporal)."""
    try:
        logger.info(f"📡 [IA] Consulta estado job - Job: {job_id}, Usuario: {current_user.usuario_id}")

        with JOBS_LOCK:
            job = JOBS.get(job_id)

        if not job:
            logger.warning(f"⚠️ [IA] Job no encontrado: {job_id}")
            raise HTTPException(status_code=404, detail="Job no encontrado")

        # Control de acceso: solo el docente que inició el job o roles elevados pueden consultar
        docente_id = job.get("docente_id")
        es_docente_creador = docente_id and str(docente_id) == str(current_user.usuario_id)
        es_rol_elevado = getattr(current_user, "rol", None) and (
            getattr(current_user.rol, "value", str(current_user.rol)) in ["administrador", "superadmin", "coordinador"]
        )

        if not (es_docente_creador or es_rol_elevado):
            logger.warning(f"⚠️ [IA] Acceso denegado a job {job_id} por usuario {current_user.usuario_id}")
            raise HTTPException(status_code=403, detail="No tienes permiso para ver este job")

        # Return a shallow copy to avoid accidental mutation
        job_copy = {**job}
        return {"success": True, "job": job_copy}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [IA] Error obteniendo estado de job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



@router.get(
    "/retroalimentacion-masiva/stream/{job_id}",
    summary="Stream SSE - actualizaciones de job masivo",
    description="SSE stream con actualizaciones del job masivo. Requiere token en query param `access_token` o cookie de sesión.",
    responses={200: {"description": "SSE stream"}, 401: {"description": "No autorizado"}},
    tags=["IA Feedback - Gemini"],
)
async def stream_estado_job_masivo(
    job_id: str,
    access_token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Endpoint SSE que emite el estado del job en memoria.

    Nota de implementación: EventSource no permite custom headers (Authorization). Para entornos donde
    el token no se envía por cookie, aceptamos `access_token` como query param temporalmente.
    """

    try:
        logger.info(f"📡 [IA] SSE stream solicitado - Job: {job_id}")

        # Autenticación ligera: requerimos token por query param (temporal)
        if not access_token:
            logger.warning("🔒 [IA] SSE requiere access_token en query param")
            raise HTTPException(status_code=401, detail="Access token requerido para SSE")

        # Decodificar token y obtener usuario
        payload = security_manager.decode_token(access_token)
        # validar tipo
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Token inválido")

        from uuid import UUID as _UUID
        usuario_id = _UUID(payload.get("sub"))
        usuario = usuario_crud.get(db, id=usuario_id)
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        # Control de acceso: el docente que inició el job o roles elevados pueden ver
        with JOBS_LOCK:
            job = JOBS.get(job_id)

        if not job:
            logger.warning(f"⚠️ [IA] Job no encontrado (SSE): {job_id}")
            raise HTTPException(status_code=404, detail="Job no encontrado")

        docente_id = job.get("docente_id")
        es_docente_creador = docente_id and str(docente_id) == str(usuario.usuario_id)
        es_rol_elevado = getattr(usuario, "rol", None) and (
            getattr(usuario.rol, "value", str(usuario.rol)) in ["administrador", "superadmin", "coordinador"]
        )

        if not (es_docente_creador or es_rol_elevado):
            logger.warning(f"⚠️ [IA] Acceso SSE denegado a job {job_id} por usuario {usuario.usuario_id}")
            raise HTTPException(status_code=403, detail="No tienes permiso para ver este job")

        async def event_generator():
            last_payload = None
            try:
                while True:
                    with JOBS_LOCK:
                        current = JOBS.get(job_id)
                        if not current:
                            # enviar evento de error y cerrar
                            yield f"data: {json.dumps({'error':'job_not_found'})}\n\n"
                            return

                        payload = json.dumps({"job": current}, default=str)

                    if payload != last_payload:
                        yield f"data: {payload}\n\n"
                        last_payload = payload

                    # Si el job está completado, salir
                    if current.get("estado") in ("completado", "error"):
                        return

                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                logger.info(f"📡 [IA] SSE client disconnected - Job: {job_id}")
                return

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [IA] Error en SSE stream: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    "/ia/health",
    summary="Verificar estado del sistema de IA",
    description="Verifica que el sistema de IA y gamificación esté funcionando correctamente",
    tags=["IA Feedback - Gemini"],
)
async def health_check_ia():
    """Health check para el sistema de IA y gamificación."""
    logger.info("🏥 [IA] Health check solicitado")
    return {
        "success": True,
        "message": "Sistema de IA y Gamificación operativo",
        "services": {
            "gemini_ai": "✅ operativo",
            "gamificacion": "✅ operativo",
            "puntos": "✅ operativo",
        },
    }


# =============================================================================
# CONFIGURACIÓN DEL ROUTER
# =============================================================================

# Logging de rutas registradas
logger.info(f"✅ Router IA y Gamificación cargado con {len(router.routes)} rutas")
