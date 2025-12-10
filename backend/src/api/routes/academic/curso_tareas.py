"""
Rutas de API para tareas de cursos - REFACTORIZADO

Thin controllers usando tarea_service
SOLID + Clean Code: Delegación completa a service layer
"""

from fastapi import APIRouter, Depends, Body, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging
import json

from src.api import deps
from src.models.users.usuario import Usuario
from src.services.academic.tarea_service import tarea_service
from src.schemas.academic.tarea_schemas import TareaCreateRequest, EntregaTareaDetallada

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cursos/tareas")


@router.get("/{curso_id}/tareas")
async def obtener_tareas_curso(
    curso_id: str,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    incluir_vencidas: bool = Query(True, description="Incluir tareas vencidas en los resultados"),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    logger.info(f"GET tareas curso {curso_id} - Usuario: {current_user.usuario_id} - Incluir vencidas: {incluir_vencidas}")
    return tarea_service.obtener_tareas_curso(
        db=db, curso_id=curso_id, usuario=current_user,
        limit=limit, offset=offset, incluir_vencidas=incluir_vencidas
    )


@router.post("/{curso_id}/tareas")
async def crear_tarea(
    curso_id: str,
    tarea_data: TareaCreateRequest,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Crea una nueva tarea en un curso.
    
    Solo docentes pueden crear tareas. El usuario actual se establece como creador.
    
    **Campos requeridos:**
    - titulo: Título de la tarea (1-200 caracteres)
    - fecha_limite: Fecha límite de entrega (ISO 8601 datetime)
    
    **Campos opcionales:**
    - descripcion: Descripción detallada (default: vacío)
    - puntos_max: Puntuación máxima (default: 100)
    - tipo: Tipo de tarea (default: "ejercicios")
    - prioridad: Nivel de prioridad (default: "media")
    
    **Respuesta:**
    Retorna la tarea creada con todos los detalles incluyendo ID.
    """
    logger.info(f"POST tarea curso {curso_id} - Usuario: {current_user.usuario_id} - Título: {tarea_data.titulo}")
    return tarea_service.crear_tarea(
        db=db, 
        curso_id=curso_id, 
        titulo=tarea_data.titulo,
        descripcion=tarea_data.descripcion,
        fecha_limite=tarea_data.fecha_limite,
        puntos_max=tarea_data.puntos_max,
        usuario=current_user,
        tipo=tarea_data.tipo,
        prioridad=tarea_data.prioridad
    )



from fastapi import Form, File, UploadFile
from pathlib import Path
import shutil
import os
from uuid import uuid4


@router.get("/{tarea_id}")
async def obtener_tarea(
    tarea_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Obtiene los detalles de una tarea específica.
    """
    logger.info(f"GET tarea {tarea_id} - Usuario: {current_user.usuario_id}")
    return tarea_service.obtener_tarea(
        db=db, tarea_id=tarea_id, usuario=current_user
    )


@router.post("/{tarea_id}/entregar")
async def entregar_tarea(
    tarea_id: str,
    contenido: str = Form(None),
    archivos: List[UploadFile] = File(default=None),  # Archivos NUEVOS
    enlaces: str = Form(None),  # JSON string con enlaces NUEVOS
    archivos_existentes: str = Form(None),  # ✅ JSON con archivos a CONSERVAR
    enlaces_existentes: str = Form(None),  # ✅ JSON con enlaces a CONSERVAR
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Entrega una tarea.
    
    **Parámetros**:
    - `contenido`: Texto de la entrega (opcional)
    - `archivos`: Lista de archivos NUEVOS adjuntos (opcional)
    - `enlaces`: JSON string con lista de enlaces NUEVOS (opcional)
    - `archivos_existentes`: JSON con archivos anteriores a CONSERVAR (opcional)
    - `enlaces_existentes`: JSON con enlaces anteriores a CONSERVAR (opcional)
    
    **Respuesta**: Confirmación de entrega con ID
    """
    logger.info(f"📥 POST /tareas/{tarea_id}/entregar - Usuario: {current_user.usuario_id}")
    logger.info(f"   Archivos NUEVOS: {len(archivos) if archivos else 0}")
    
    # Parsear enlaces NUEVOS si existen
    enlaces_nuevos_list = []
    if enlaces:
        try:
            enlaces_nuevos_list = json.loads(enlaces)
            logger.info(f"   Enlaces NUEVOS: {len(enlaces_nuevos_list)}")
        except json.JSONDecodeError:
            logger.warning(f"   Error parseando enlaces NUEVOS JSON")
    
    # ✅ Parsear archivos EXISTENTES a conservar
    archivos_existentes_list = []
    if archivos_existentes:
        try:
            archivos_existentes_list = json.loads(archivos_existentes)
            logger.info(f"   📎 Archivos EXISTENTES a conservar: {len(archivos_existentes_list)}")
        except json.JSONDecodeError:
            logger.warning(f"   Error parseando archivos_existentes JSON")
    
    # ✅ Parsear enlaces EXISTENTES a conservar
    enlaces_existentes_list = []
    if enlaces_existentes:
        try:
            enlaces_existentes_list = json.loads(enlaces_existentes)
            logger.info(f"   🔗 Enlaces EXISTENTES a conservar: {len(enlaces_existentes_list)}")
        except json.JSONDecodeError:
            logger.warning(f"   Error parseando enlaces_existentes JSON")
    
    # Fallback: si contenido es None o vacío, usar texto por defecto
    if not contenido or contenido.strip() == "":
        contenido = "Entrega de tarea"
    
    archivo_urls = []
    archivos_metadata = []
    
    # Procesar TODOS los archivos
    if archivos is None:
        archivos = []
    
    if archivos and len(archivos) > 0:
        logger.info(f"   Procesando {len(archivos)} archivos...")
        try:
            # Crear directorio de uploads si no existe
            backend_dir = Path(__file__).parent.parent.parent.parent  # backend/
            upload_dir = backend_dir / "uploads" / "entregas"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Guardar cada archivo
            for idx, archivo in enumerate(archivos, 1):
                # Generar nombre único para el archivo
                file_ext = Path(archivo.filename).suffix
                unique_filename = f"{uuid4()}{file_ext}"
                file_path = upload_dir / unique_filename

                # Guardar archivo en disco
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(archivo.file, f)

                archivo_url = f"/uploads/entregas/{unique_filename}"
                archivo_urls.append(archivo_url)

                # Guardar metadata: URL + nombre original
                archivos_metadata.append({
                    "url": archivo_url,
                    "nombre_original": archivo.filename,
                    "nombre": archivo.filename,
                    "nombre_almacenado": unique_filename
                })
            
            logger.info(f"   ✅ {len(archivo_urls)} archivos procesados correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error guardando archivos: {str(e)}")
            archivo_urls = []
            archivos_metadata = []
    
    # Usar el primer archivo como URL principal (para compatibilidad con schema existente)
    archivo_url = archivo_urls[0] if archivo_urls else None
    
    # ✅ MERGE: Combinar archivos existentes + nuevos
    archivos_metadata_final = list(archivos_existentes_list)  # Copiar existentes
    archivos_metadata_final.extend(archivos_metadata)  # Agregar nuevos
    logger.info(f"   📎 MERGE archivos: {len(archivos_existentes_list)} existentes + {len(archivos_metadata)} nuevos = {len(archivos_metadata_final)} totales")
    
    # ✅ MERGE: Combinar enlaces existentes + nuevos
    enlaces_finales = list(enlaces_existentes_list)  # Copiar existentes
    enlaces_finales.extend(enlaces_nuevos_list)  # Agregar nuevos
    logger.info(f"   🔗 MERGE enlaces: {len(enlaces_existentes_list)} existentes + {len(enlaces_nuevos_list)} nuevos = {len(enlaces_finales)} totales")
    
    logger.info(f"📤 Llamando a tarea_service.entregar_tarea() con {len(archivo_urls)} archivos nuevos, {len(archivos_metadata_final)} archivos totales y {len(enlaces_finales)} enlaces totales...")
    logger.info(f"   - archivos_metadata_final: {archivos_metadata_final}")
    logger.info(f"   - enlaces_finales: {enlaces_finales}")
    
    return tarea_service.entregar_tarea(
        db=db,
        tarea_id=tarea_id,
        usuario=current_user,
        contenido=contenido,
        archivo_url=archivo_url,
        archivo_urls=archivo_urls,
        archivos_metadata=archivos_metadata_final,  # ✅ MERGED
        enlaces_externos=enlaces_finales  # ✅ MERGED
    )




@router.get("/entregas/{entrega_id}")
async def obtener_entrega(
    entrega_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Obtiene los detalles de una entrega específica - SIN VALIDACIÓN PYDANTIC.
    """
    logger.info(f"GET entrega {entrega_id} - Usuario: {current_user.usuario_id}")
    
    try:
        # Obtener entrega del service
        entrega_raw = tarea_service.obtener_entrega(
            db=db, entrega_id=entrega_id, usuario=current_user
        )
        
        # Función para convertir cualquier tipo a JSON-compatible
        def to_json_compatible(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: to_json_compatible(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [to_json_compatible(item) for item in obj]
            elif hasattr(obj, '__dict__'):  # Objetos especiales como UUID, Enum, etc
                return str(obj)
            else:
                return obj
        
        # Convertir todo recursivamente
        clean_data = to_json_compatible(entrega_raw)
        
        # Retornar como JSON puro, sin Pydantic
        return JSONResponse(content=clean_data, status_code=200)
        
    except HTTPException as http_err:
        # Re-lanzar HTTPException (errores 403, 404, etc)
        raise http_err
    except Exception as err:
        logger.error(f"❌ Error crítico en GET entrega {entrega_id}: {type(err).__name__}: {str(err)}")
        return JSONResponse(
            content={"error": str(err), "error_type": type(err).__name__},
            status_code=500
        )


@router.delete("/entregas/{entrega_id}")
async def cancelar_entrega(
    entrega_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Cancela/elimina una entrega de tarea.
    
    **Restricciones**:
    - Solo el estudiante que hizo la entrega puede cancelarla
    - No se puede cancelar si ya está calificada
    - Solo se puede cancelar si el estado es 'entregada' o 'pendiente'
    """
    logger.info(f"DELETE entrega {entrega_id} - Usuario: {current_user.usuario_id}")
    return tarea_service.cancelar_entrega(
        db=db, entrega_id=entrega_id, usuario=current_user
    )


@router.post("/entregas/{entrega_id}/calificar")
async def calificar_entrega(
    entrega_id: str,
    calificacion: float = Body(..., ge=0, le=100),
    comentarios: Optional[str] = Body(None),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Califica una entrega de tarea con gamificación completa integrada.
    
    **Funcionalidades:**
    - Registra calificación del docente
    - Otorga puntos según calidad (calificación)
    - Otorga bonos por rapidez (entrega temprana)
    - Penaliza entregas tardías
    - Verifica y actualiza racha diaria del estudiante
    - Otorga recompensas de racha (10-50 pts/día según ciclo semanal)
    - Verifica milestones de racha (7, 30, 100, 365 días)
    
    **Desglose de puntos:**
    - Puntos base: Configurados en la tarea (default 50)
    - Bono calidad: Si calificación >= 90 (excelente)
    - Bono rapidez: 5-15 pts si entregó en primera mitad del plazo
    - Penalización tardía: -10 pts
    - Penalización intentos: -5 pts por reenvío adicional
    
    **Respuesta incluye:**
    - Calificación registrada
    - Puntos otorgados (con desglose detallado)
    - Racha actualizada (días actuales, puntos de racha)
    - Milestones alcanzados (si aplica)
    """
    logger.info(f"POST calificar entrega {entrega_id} - Usuario: {current_user.usuario_id}")
    return await tarea_service.calificar_entrega(
        db=db, entrega_id=entrega_id, calificacion=calificacion,
        retroalimentacion=comentarios, usuario=current_user
    )
