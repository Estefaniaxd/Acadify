import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.dependencies import get_current_user
from src.core.storage import upload_file_to_storage
from src.crud.academic.tarea import crud_entrega_tarea, crud_rubrica, crud_tarea
from src.enums.academic.tareas import EstadoEntrega, EstadoTarea
from src.models.users.usuario import Usuario
from src.models.academic.tarea import Tarea
from src.schemas.academic.tarea_enriched import RespuestaPaginada, TareaEnriquecida, EstadoVisualizacion, FiltrosTareaEnriquecida
from src.schemas.academic.tarea_schemas import (
    CalificarEntrega,
    EntregaTareaCreate,
    EntregaTareaDetallada,
    EntregaTareaResponse,
    EntregaTareaUpdate,
    FiltrosEntrega,
    FiltrosTarea,
    RubricaCreate,
    RubricaResponse,
    TareaCreate,
    TareaDetallada,
    TareaResponse,
    TareaUpdate,
)
from src.schemas.google_workspace_schemas import GoogleResourceCreate, GoogleResourceType
from src.services.academic.tarea_enriched_service import (
    crear_servicio_tareas_enriquecidas,
)

logger = logging.getLogger(__name__)


router = APIRouter()

# === RUTAS PARA TAREAS ===


@router.post("/", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_data: TareaCreate,
    current_user: Usuario = Depends(get_current_user),
):
    """Crear una nueva tarea."""
    # Verificar que el usuario sea docente o coordinador
    if not hasattr(current_user, "docente") and not hasattr(
        current_user, "coordinador"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes y coordinadores pueden crear tareas",
        )

    try:
        return crud_tarea.crear_tarea(
            db=db, tarea_data=tarea_data, creado_por=current_user.usuario_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la tarea: {e!s}",
        ) from e


@router.get("/grupo/{grupo_id}", response_model=list[TareaResponse])
def obtener_tareas_grupo(
    *,
    db: Session = Depends(get_db),
    grupo_id: str,
    estado: EstadoTarea | None = Query(None),
    tipo: str | None = Query(None, max_length=13),  # Campo real en BD
    solo_activas: bool = Query(True),
    busqueda: str | None = Query(None),
    ordenar_por: str = Query("fecha_limite"),
    orden_desc: bool = Query(False),
    pagina: int = Query(1, ge=1),
    tamaño_pagina: int = Query(20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener todas las tareas de un grupo con filtros."""
    filtros = FiltrosTarea(
        grupo_id=grupo_id,
        estado=estado,
        tipo=tipo,  # Usar el campo correcto
        solo_activas=solo_activas,
        busqueda=busqueda,
        ordenar_por=ordenar_por,
        orden_desc=orden_desc,
        pagina=pagina,
        tamaño_pagina=tamaño_pagina,
    )

    return crud_tarea.obtener_tareas_por_grupo(
        db=db, grupo_id=grupo_id, filtros=filtros, usuario_id=current_user.usuario_id
    )


@router.get("/docente/{docente_id}", response_model=list[TareaResponse])
def obtener_tareas_docente(
    *,
    db: Session = Depends(get_db),
    docente_id: str,
    solo_activas: bool = Query(True),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener todas las tareas creadas por un docente."""
    # Verificar permisos: solo el propio docente o coordinadores pueden ver esto
    if current_user.usuario_id != docente_id and not hasattr(
        current_user, "coordinador"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estas tareas",
        )

    filtros = FiltrosTarea(solo_activas=solo_activas)
    return crud_tarea.obtener_tareas_por_docente(
        db=db, docente_id=docente_id, filtros=filtros
    )


@router.get("/{tarea_id}")
def obtener_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener una tarea específica con detalles completos."""
    from fastapi.responses import JSONResponse
    from datetime import datetime
    
    try:
        logger.info(f"🔍 Obteniendo tarea: {tarea_id}")
        tarea = crud_tarea.obtener_tarea_detallada(db=db, tarea_id=tarea_id)
        
        if not tarea:
            logger.warning(f"⚠️ Tarea no encontrada: {tarea_id}")
            return JSONResponse(
                status_code=404,
                content={"detail": "Tarea no encontrada"}
            )

        # El modelo usa 'tarea_id' como PK, no 'id'
        try:
            tarea_pk = getattr(tarea, 'tarea_id', None) or getattr(tarea, 'id', None)
        except Exception:
            tarea_pk = None
        logger.info(f"✅ Tarea encontrada: {tarea_pk}")

        # Función helper para convertir a dict seguramente
        def serialize_obj(obj, visited=None, depth=0):
            """Serializa recursivamente objetos SQLAlchemy."""
            if visited is None:
                visited = set()
            
            # Limitar profundidad
            if depth > 5:
                return None
            
            # Evitar referencias circulares
            if id(obj) in visited:
                return None
            
            if obj is None:
                return None
            
            # Enums Python: retornar valor string
            try:
                if isinstance(obj, Enum) and not isinstance(obj, str):
                    return str(obj.value)
            except:
                pass
            
            # Datetime
            if isinstance(obj, datetime):
                return obj.isoformat()
            
            # Tipos primitivos
            if isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            
            # Listas y tuples
            if isinstance(obj, (list, tuple)):
                try:
                    return [serialize_obj(item, visited, depth+1) for item in obj]
                except:
                    return None
            
            # Dicts
            if isinstance(obj, dict):
                result = {}
                try:
                    for k, v in obj.items():
                        try:
                            result[k] = serialize_obj(v, visited, depth+1)
                        except Exception as ex:
                            logger.debug(f"No se pudo serializar dict[{k}]: {ex}")
                            result[k] = None
                    return result
                except:
                    return None
            
            # SQLAlchemy objects
            try:
                if hasattr(obj, '__dict__'):
                    visited.add(id(obj))
                    result = {}
                    for key, val in obj.__dict__.items():
                        # Ignorar atributos privados de SQLAlchemy
                        if key.startswith('_'):
                            continue
                        try:
                            result[key] = serialize_obj(val, visited, depth+1)
                        except Exception as ex:
                            logger.debug(f"No se pudo serializar {key}: {type(ex).__name__}: {ex}")
                            result[key] = None
                    return result
            except Exception as ex:
                logger.error(f"Error en serialize_obj: {type(ex).__name__}: {ex}")
                pass
            
            # Fallback: convertir a string
            try:
                return str(obj)
            except:
                return None
        
        logger.info(f"🔄 Serializando tarea...")
        tarea_dict = serialize_obj(tarea)
        logger.info(f"✅ Tarea serializada correctamente")
        logger.debug(f"📦 Contenido tarea_dict: {tarea_dict}")
        
        # Retornar raw JSON sin validación de FastAPI
        import json
        json_str = json.dumps(tarea_dict, default=str)
        return JSONResponse(content=json.loads(json_str), status_code=200)
        
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        logger.error(f"❌ Error en obtener_tarea:\n{error_msg}")
        # Retornar error sin validación de Pydantic
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error al obtener tarea: {error_msg}"}
        )


@router.put("/{tarea_id}", response_model=TareaResponse)
def actualizar_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    tarea_update: TareaUpdate,
    current_user: Usuario = Depends(get_current_user),
):
    """Actualizar una tarea existente."""
    tarea = crud_tarea.get(db=db, id=tarea_id)
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )

    # Verificar permisos: solo el creador o coordinadores pueden editar
    if tarea.docente_id != current_user.usuario_id and not hasattr(
        current_user, "coordinador"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar esta tarea",
        )

    return crud_tarea.update(db=db, db_obj=tarea, obj_in=tarea_update)


@router.patch("/{tarea_id}/estado", response_model=TareaResponse)
def cambiar_estado_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    nuevo_estado: EstadoTarea,
    current_user: Usuario = Depends(get_current_user),
):
    """Cambiar el estado de una tarea."""
    tarea = crud_tarea.actualizar_estado_tarea(
        db=db,
        tarea_id=tarea_id,
        nuevo_estado=nuevo_estado,
        actualizado_por=current_user.usuario_id,
    )

    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )

    return tarea


@router.get("/{tarea_id}/estadisticas", response_model=dict)
def obtener_estadisticas_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener estadísticas detalladas de una tarea."""
    estadisticas = crud_tarea.obtener_estadisticas_tarea(db=db, tarea_id=tarea_id)
    if not estadisticas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )

    return estadisticas


@router.delete("/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    current_user: Usuario = Depends(get_current_user),
) -> None:
    """Eliminar (desactivar) una tarea."""
    tarea = crud_tarea.get(db=db, id=tarea_id)
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )

    # Verificar permisos
    if tarea.docente_id != current_user.usuario_id and not hasattr(
        current_user, "coordinador"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar esta tarea",
        )

    crud_tarea.remove(db=db, id=tarea_id)


# === RUTAS PARA ENTREGAS ===


@router.post(
    "/{tarea_id}/entregas",
    response_model=EntregaTareaResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_entrega(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    entrega_data: EntregaTareaCreate,
    current_user: Usuario = Depends(get_current_user),
):
    """Crear una nueva entrega de tarea con validaciones completas.
    
    Validaciones realizadas:
    1. Usuario es estudiante
    2. Tarea existe y está activa
    3. Estudiante está inscrito en el grupo
    4. Tarea está disponible (fecha inicio/límite)
    5. Estudiante no ha excedido intentos máximos
    
    SOLID Principles:
    - Single Responsibility: Solo crea entrega (delega validación)
    - Dependency Inversion: Usa ValidadorEntregaTarea
    """
    from src.services.academic.entrega_validator import ValidadorEntregaTarea
    
    try:
        # 1. Verificar que el usuario sea estudiante
        if not hasattr(current_user, "estudiante"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los estudiantes pueden entregar tareas",
            )

        # 2. Obtener tarea
        tarea = crud_tarea.get(db=db, id=tarea_id)
        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
            )
        
        if not tarea.activa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta tarea no está activa",
            )

        # 3. Usar validador profesional
        validador = ValidadorEntregaTarea(session=db)
        resultado_validacion = validador.validar_entrega_completa(
            tarea=tarea,
            estudiante_id=current_user.usuario_id,
            grupo_id=tarea.grupo_id
        )
        
        if not resultado_validacion.es_valida:
            # Mapear estado a HTTP status code apropiado
            status_code = {
                "estudiante_no_inscrito": status.HTTP_403_FORBIDDEN,
                "tarea_no_disponible": status.HTTP_400_BAD_REQUEST,
                "tarea_vencida": status.HTTP_400_BAD_REQUEST,
                "limite_intentos_excedido": status.HTTP_400_BAD_REQUEST,
                "entrega_tardia_no_permitida": status.HTTP_400_BAD_REQUEST,
                "tarea_desactivada": status.HTTP_400_BAD_REQUEST,
            }.get(resultado_validacion.estado.value, status.HTTP_400_BAD_REQUEST)
            
            raise HTTPException(
                status_code=status_code,
                detail=resultado_validacion.mensaje,
            )

        # 4. Asegurar que el tarea_id y estudiante_id son correctos (anti-inyección)
        entrega_data.tarea_id = tarea_id
        entrega_data.estudiante_id = current_user.usuario_id

        # 5. Crear entrega
        entrega = crud_entrega_tarea.crear_entrega(db=db, entrega_data=entrega_data)
        
        # 6. Marcar como ENTREGADA inmediatamente
        # Esto asegura que el profesor la vea. En el futuro, esto podría ser un paso separado
        # si se implementa funcionalidad de "Guardar borrador".
        entrega = crud_entrega_tarea.entregar_tarea(db=db, entrega_id=entrega.entrega_id)
        
        logger.info(
            f"✅ Entrega creada y enviada: estudiante={current_user.usuario_id}, "
            f"tarea={tarea_id}, entrega_id={entrega.entrega_id}, "
            f"intentos_restantes={resultado_validacion.intentos_restantes}"
        )
        
        return entrega
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear entrega: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la entrega: {str(e)}",
        ) from e


@router.post("/entregas/{entrega_id}/subir-archivo")
async def subir_archivo_entrega(
    *,
    db: Session = Depends(get_db),
    entrega_id: str,
    archivo: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
):
    """Subir archivo para una entrega con SEGURIDAD completa.
    
    Validaciones de seguridad:
    1. Verificar permisos (es dueño de la entrega)
    2. Validar archivo (extensión, tamaño, MIME type)
    3. Generar nombre seguro (prevenir path traversal)
    4. Guardar con path seguro
    
    SOLID Principles:
    - Single Responsibility: Solo sube archivo (delega validación)
    - Dependency Inversion: Usa ValidadorArchivos
    """
    from src.services.academic.file_validator import ValidadorArchivos
    import uuid
    import os
    
    try:
        # 1. Verificar que entrega existe y pertenece al usuario
        entrega = crud_entrega_tarea.get(db=db, id=entrega_id)
        if not entrega:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrega no encontrada"
            )

        # Verificar permisos
        if entrega.estudiante_id != current_user.usuario_id:
            logger.warning(
                f"Intento de acceso no autorizado a entrega {entrega_id} "
                f"por usuario {current_user.usuario_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes modificar esta entrega",
            )

        # 2. Obtener tarea para configuración de restricciones
        tarea = crud_tarea.get(db=db, id=entrega.tarea_id)
        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea asociada no encontrada"
            )

        # 3. Leer contenido del archivo
        contenido = await archivo.read()
        
        if not contenido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo está vacío"
            )

        # 4. Configurar validador con restricciones de la tarea
        # Por defecto: 50MB, pero puede venir de tarea.restricciones_archivo
        tamaño_maximo = tarea.tamano_maximo_mb if tarea.tamano_maximo_mb else 50
        
        # Extensiones permitidas (whitelist)
        # Si la tarea especifica restricciones, usarlas; si no, todas las permitidas
        if tarea.restricciones_archivo and isinstance(tarea.restricciones_archivo, dict):
            extensiones_permitidas = set(
                tarea.restricciones_archivo.get("tipos_permitidos", [])
            )
            if not extensiones_permitidas:
                extensiones_permitidas = ValidadorArchivos.EXTENSIONES_PERMITIDAS_DEFAULT
        else:
            extensiones_permitidas = ValidadorArchivos.EXTENSIONES_PERMITIDAS_DEFAULT

        validador = ValidadorArchivos(
            extensiones_permitidas=extensiones_permitidas,
            tamaño_maximo_mb=tamaño_maximo
        )

        # 5. VALIDAR completamente el archivo
        metadata = validador.validar(
            nombre=archivo.filename,
            contenido=contenido,
            mime_type=archivo.content_type or "application/octet-stream"
        )

        # ¿Validación exitosa?
        if metadata.validez.value != "valido":
            logger.warning(
                f"Validación fallida: {metadata.validez.value} - {metadata.detalles_error}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=metadata.detalles_error or f"Archivo inválido: {metadata.validez.value}"
            )

        # 6. Generar ruta segura para almacenar
        ruta_almacenamiento = validador.crear_ruta_almacenamiento(
            base_dir="/app/uploads",  # Configurar desde env var
            entrega_id=entrega_id,
            nombre_seguro=metadata.nombre_seguro
        )

        # 7. Subir archivo al storage con ruta segura
        archivo_url = await upload_file_to_storage(
            archivo,
            ruta_almacenamiento  # Usar ruta segura en lugar de filename directo
        )

        # 8. Guardar metadata en BD
        entrega_update = EntregaTareaUpdate(
            archivo_url=archivo_url,
            archivo_metadata={
                "nombre_original": metadata.nombre_original,
                "nombre_seguro": metadata.nombre_seguro,
                "extension": metadata.extension,
                "mime_type": metadata.mime_type,
                "tamaño_bytes": metadata.tamaño_bytes,
                "fecha_subida": metadata.fecha_subida
            }
        )
        entrega_actualizada = crud_entrega_tarea.update(
            db=db,
            db_obj=entrega,
            obj_in=entrega_update
        )

        logger.info(
            f"✅ Archivo subido exitosamente: entrega={entrega_id}, "
            f"archivo={metadata.nombre_seguro}, tamaño={metadata.tamaño_bytes} bytes"
        )

        return {
            "mensaje": "Archivo subido correctamente",
            "archivo_url": archivo_url,
            "metadata": {
                "nombre": metadata.nombre_original,
                "tamaño_mb": round(metadata.tamaño_bytes / (1024 * 1024), 2),
                "tipo": metadata.mime_type,
                "fecha": metadata.fecha_subida
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al subir archivo: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el archivo: {str(e)}",
        ) from e


@router.patch("/entregas/{entrega_id}/entregar", response_model=EntregaTareaResponse)
def entregar_tarea(
    *,
    db: Session = Depends(get_db),
    entrega_id: str,
    current_user: Usuario = Depends(get_current_user),
):
    """Marcar una entrega como entregada (finalizar entrega)."""
    entrega = crud_entrega_tarea.entregar_tarea(db=db, entrega_id=entrega_id)
    if not entrega:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada"
        )

    return entrega


@router.patch("/entregas/{entrega_id}/calificar", response_model=dict)
def calificar_entrega(
    *,
    db: Session = Depends(get_db),
    entrega_id: str,
    calificacion_data: CalificarEntrega,
    current_user: Usuario = Depends(get_current_user),
):
    """Calificar una entrega e integrar puntos de gamificación.
    
    Este endpoint:
    1. Verifica que el usuario sea docente/coordinador
    2. Valida la calificación
    3. Actualiza la entrega con calificación
    4. Calcula puntos automáticamente según la fórmula de gamificación
    5. Almacena puntos en la BD (entregas_tareas.puntos_otorgados)
    6. Retorna resultado completo con detalles de puntos

    Response:
        {
            "entrega_id": "uuid",
            "estudiante_id": "uuid",
            "calificacion": 4.5,
            "puntos_otorgados": 45,
            "formula_aplicada": "50 (base) - 15 (tardía) - 10 (1 intento extra)",
            "estado": "CALIFICADA",
            "fecha_calificacion": "2025-11-18T15:30:00Z",
            ...entrega fields...
        }
    """
    # Verificar que el usuario sea docente
    if not hasattr(current_user, "docente") and not hasattr(
        current_user, "coordinador"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden calificar entregas",
        )
    
    # Validar rango de calificación (0.0 - 5.0)
    if calificacion_data.calificacion is not None:
        if calificacion_data.calificacion < 0.0 or calificacion_data.calificacion > 5.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La calificación debe estar entre 0.0 y 5.0. Valor recibido: {calificacion_data.calificacion}"
            )

    try:
        # Usar el nuevo CRUD que integra cálculo de puntos
        resultado = crud_entrega_tarea.calificar_entrega_con_puntos(
            db=db,
            entrega_id=entrega_id,
            calificacion_data=calificacion_data,
            calificado_por=current_user.usuario_id,
        )

        # Extraer entrega del resultado
        entrega = resultado.pop("entrega")

        # Retornar entrega + información de puntos
        response_data = EntregaTareaResponse.model_validate(entrega).model_dump()
        response_data.update(resultado)  # Agrega puntos_otorgados y formula_aplicada

        logger.info(
            f"Entrega calificada exitosamente: entrega_id={entrega_id}, "
            f"puntos={resultado['puntos_otorgados']}"
        )

        return response_data

    except ValueError as e:
        logger.warning(f"Validación fallida en calificación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        logger.exception(f"Error calificando entrega: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al calificar la entrega",
        ) from e


@router.get("/{tarea_id}/entregas", response_model=list[EntregaTareaResponse])
def obtener_entregas_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    estado: EstadoEntrega | None = Query(None),
    solo_calificadas: bool | None = Query(None),
    solo_pendientes: bool | None = Query(None),
    pagina: int = Query(1, ge=1),
    tamaño_pagina: int = Query(20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener todas las entregas de una tarea."""
    filtros = FiltrosEntrega(
        tarea_id=tarea_id,
        estado=estado,
        solo_calificadas=solo_calificadas,
        solo_pendientes=solo_pendientes,
        pagina=pagina,
        tamaño_pagina=tamaño_pagina,
    )

    return crud_entrega_tarea.obtener_entregas_por_tarea(
        db=db, tarea_id=tarea_id, filtros=filtros
    )


@router.get("/entregas/{entrega_id}", response_model=EntregaTareaDetallada)
def obtener_entrega(
    *,
    db: Session = Depends(get_db),
    entrega_id: str,
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener una entrega específica con detalles completos."""
    entrega = crud_entrega_tarea.obtener_entrega_detallada(db=db, entrega_id=entrega_id)
    if not entrega:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada"
        )

    return entrega


# === RUTAS PARA RÚBRICAS ===


@router.post(
    "/rubricas", response_model=RubricaResponse, status_code=status.HTTP_201_CREATED
)
def crear_rubrica(
    *,
    db: Session = Depends(get_db),
    rubrica_data: RubricaCreate,
    current_user: Usuario = Depends(get_current_user),
):
    """Crear una nueva rúbrica."""
    if not hasattr(current_user, "docente") and not hasattr(
        current_user, "coordinador"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden crear rúbricas",
        )

    rubrica_data.creado_por = current_user.usuario_id
    return crud_rubrica.create(db=db, obj_in=rubrica_data)


@router.get("/rubricas", response_model=list[RubricaResponse])
def obtener_rubricas(
    *,
    db: Session = Depends(get_db),
    incluir_publicas: bool = Query(True),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener rúbricas del docente actual."""
    return crud_rubrica.obtener_rubricas_por_docente(
        db=db, docente_id=current_user.usuario_id, incluir_publicas=incluir_publicas
    )


@router.get("/rubricas/publicas", response_model=list[RubricaResponse])
def obtener_rubricas_publicas(
    *, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    """Obtener todas las rúbricas públicas."""
    return crud_rubrica.obtener_rubricas_publicas(db=db)


@router.post("/rubricas/{rubrica_id}/duplicar", response_model=RubricaResponse)
def duplicar_rubrica(
    *,
    db: Session = Depends(get_db),
    rubrica_id: str,
    nuevo_nombre: str,
    current_user: Usuario = Depends(get_current_user),
):
    """Duplicar una rúbrica existente."""
    rubrica = crud_rubrica.duplicar_rubrica(
        db=db,
        rubrica_id=rubrica_id,
        nuevo_nombre=nuevo_nombre,
        creado_por=current_user.usuario_id,
    )

    if not rubrica:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rúbrica no encontrada"
        )

    return rubrica


# ========================================================
# === ENDPOINTS ENRIQUECIDOS - ESTADOS Y MÉTRICAS ===
# ========================================================


@router.get("/grupo/{grupo_id}/enriquecidas", response_model=RespuestaPaginada)
def obtener_tareas_enriquecidas_grupo(
    *,
    db: Session = Depends(get_db),
    grupo_id: str,
    estado_visualizacion: str | None = Query(
        None,
        description="Estado de visualización (pendiente, proxima_a_vencer, vencida, etc)",
    ),
    solo_activas: bool = Query(True, description="Solo tareas activas"),
    solo_proximas_a_vencer: bool = Query(
        False, description="Solo próximas a vencer (< 48h)"
    ),
    solo_vencidas: bool = Query(False, description="Solo vencidas"),
    solo_con_entregas_pendientes: bool = Query(
        False, description="Solo con entregas sin calificar"
    ),
    busqueda: str | None = Query(None, description="Búsqueda en título y descripción"),
    ordenar_por: str = Query(
        "fecha_limite",
        description="Campo para ordenar (fecha_limite, prioridad, titulo, etc)",
    ),
    orden_desc: bool = Query(False, description="Orden descendente"),
    pagina: int = Query(1, ge=1, description="Número de página"),
    tamaño_pagina: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene tareas enriquecidas con estados calculados y métricas.

    **Estados de visualización disponibles:**
    - `pendiente`: Sin entregas, aún con tiempo
    - `proxima_a_vencer`: Quedan menos de 48 horas
    - `vencida`: Fecha límite expirada
    - `entregada`: Con entregas a tiempo
    - `entregada_tardia`: Con entregas tardías
    - `calificada`: Todas las entregas calificadas
    - `cancelada`: Tarea cancelada

    **Información enriquecida incluida:**
    - Estados visuales (colores, iconos, textos)
    - Tiempo restante calculado (días, horas, minutos)
    - Métricas de progreso (completitud, tasa de puntualidad)
    - Estadísticas de calificación (promedio, mediana, desviación)
    - Flags booleanos útiles (es_urgente, requiere_atención, etc)

    **Ejemplos de uso:**
    - Todas las tareas del grupo: `GET /tareas/grupo/{grupo_id}/enriquecidas`
    - Solo próximas a vencer: `GET /tareas/grupo/{grupo_id}/enriquecidas?solo_proximas_a_vencer=true`
    - Solo vencidas sin calificar: `GET /tareas/grupo/{grupo_id}/enriquecidas?solo_vencidas=true&solo_con_entregas_pendientes=true`
    """
    try:
        # Crear servicio enriquecido
        servicio = crear_servicio_tareas_enriquecidas(db)

        # Construir filtros

        # Convertir string de estado a enum si se proporciona
        estado_viz_enum = None
        if estado_visualizacion:
            try:
                estado_viz_enum = EstadoVisualizacion(estado_visualizacion)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estado de visualización inválido: {estado_visualizacion}",
                ) from None

        filtros = FiltrosTareaEnriquecida(
            grupo_id=grupo_id,
            estado_visualizacion=estado_viz_enum,
            solo_activas=solo_activas,
            solo_proximas_a_vencer=solo_proximas_a_vencer,
            solo_vencidas=solo_vencidas,
            solo_con_entregas_pendientes=solo_con_entregas_pendientes,
            busqueda=busqueda,
            ordenar_por=ordenar_por,
            orden_desc=orden_desc,
            pagina=pagina,
            tamaño_pagina=tamaño_pagina,
        )

        # Obtener tareas enriquecidas
        return servicio.listar_tareas_enriquecidas(filtros)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo tareas enriquecidas: {e!s}",
        ) from e


@router.get("/{tarea_id}/enriquecida", response_model=TareaEnriquecida)
def obtener_tarea_enriquecida_detalle(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    incluir_estadisticas: bool = Query(
        True, description="Incluir estadísticas de calificación"
    ),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene una tarea específica con información enriquecida completa.

    **Información incluida:**
    - Todos los campos base de la tarea
    - Estado de visualización calculado
    - Información visual (colores, iconos, textos)
    - Tiempo restante detallado
    - Métricas de progreso completas:
      * Total de estudiantes
      * Entregas realizadas/pendientes/calificadas
      * Porcentaje de completitud
      * Tasa de puntualidad
    - Estadísticas de calificación (opcional):
      * Promedio, mediana, desviación estándar
      * Calificación máxima y mínima
      * Rango de calificaciones
    - Flags booleanos útiles
    - Cálculos de puntos con penalizaciones

    **Uso:**
    ```
    GET /tareas/{tarea_id}/enriquecida
    GET /tareas/{tarea_id}/enriquecida?incluir_estadisticas=false  # Sin estadísticas para mejor performance
    ```
    """
    try:
        # Crear servicio enriquecido
        servicio = crear_servicio_tareas_enriquecidas(db)

        # Obtener tarea enriquecida
        tarea = servicio.obtener_tarea_enriquecida(
            tarea_id=tarea_id, incluir_estadisticas=incluir_estadisticas
        )

        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea con ID {tarea_id} no encontrada",
            )

        return tarea

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo tarea enriquecida: {e!s}",
        ) from e


@router.get("/docente/{docente_id}/dashboard", response_model=dict)
def obtener_dashboard_docente(
    *,
    db: Session = Depends(get_db),
    docente_id: str,
    current_user: Usuario = Depends(get_current_user),
):
    """Dashboard del docente con métricas agregadas de sus tareas.

    **Métricas incluidas:**
    - Total de tareas activas
    - Tareas próximas a vencer
    - Tareas vencidas
    - Entregas pendientes de calificar
    - Promedio de calificaciones general
    - Tasa de entrega puntual
    - Tareas que requieren atención inmediata

    **Uso:**
    ```
    GET /tareas/docente/{docente_id}/dashboard
    ```
    """
    try:

        # Verificar que el usuario actual sea el docente o un admin
        if str(current_user.usuario_id) != docente_id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver este dashboard",
            )

        # Crear servicio
        servicio = crear_servicio_tareas_enriquecidas(db)

        # Obtener todas las tareas del docente
        filtros = FiltrosTareaEnriquecida(
            docente_id=docente_id,
            solo_activas=True,
            pagina=1,
            tamaño_pagina=1000,  # Obtener todas para cálculos
        )

        respuesta = servicio.listar_tareas_enriquecidas(filtros)
        tareas = respuesta.items

        # Calcular métricas agregadas
        total_activas = len(tareas)
        proximas_a_vencer = sum(1 for t in tareas if t.es_proxima_a_vencer)
        vencidas = sum(1 for t in tareas if t.es_vencida)
        requieren_atencion = sum(1 for t in tareas if t.requiere_atencion)

        # Entregas pendientes de calificar
        entregas_pendientes = sum(
            t.metricas_progreso.entregas_realizadas
            - t.metricas_progreso.entregas_calificadas
            for t in tareas
        )

        # Promedios
        promedios_calificacion = [
            t.estadisticas_calificacion.promedio_calificacion
            for t in tareas
            if t.estadisticas_calificacion
            and t.estadisticas_calificacion.promedio_calificacion
        ]
        promedio_general = (
            sum(promedios_calificacion) / len(promedios_calificacion)
            if promedios_calificacion
            else 0.0
        )

        # Tasa de puntualidad
        tasas_puntualidad = [
            t.metricas_progreso.tasa_puntualidad
            for t in tareas
            if t.metricas_progreso.entregas_realizadas > 0
        ]
        tasa_puntualidad_promedio = (
            sum(tasas_puntualidad) / len(tasas_puntualidad)
            if tasas_puntualidad
            else 100.0
        )

        return {
            "resumen": {
                "total_tareas_activas": total_activas,
                "proximas_a_vencer": proximas_a_vencer,
                "vencidas": vencidas,
                "requieren_atencion": requieren_atencion,
                "entregas_pendientes_calificar": entregas_pendientes,
            },
            "metricas_calidad": {
                "promedio_calificaciones": round(promedio_general, 2),
                "tasa_puntualidad_promedio": round(tasa_puntualidad_promedio, 2),
            },
            "tareas_urgentes": [
                {
                    "tarea_id": t.tarea_id,
                    "titulo": t.titulo,
                    "fecha_limite": t.fecha_limite,
                    "tiempo_restante": (
                        t.tiempo_restante.mensaje_tiempo
                        if t.tiempo_restante
                        else "Vencida"
                    ),
                    "entregas_pendientes": t.metricas_progreso.entregas_pendientes,
                    "estado_visual": t.estado_visual.dict(),
                }
                for t in tareas
                if t.es_proxima_a_vencer or t.es_vencida
            ][
                :10
            ],  # Top 10 más urgentes
            "tareas_sin_calificar": [
                {
                    "tarea_id": t.tarea_id,
                    "titulo": t.titulo,
                    "entregas_sin_calificar": t.metricas_progreso.entregas_realizadas
                    - t.metricas_progreso.entregas_calificadas,
                }
                for t in tareas
                if (
                    t.metricas_progreso.entregas_realizadas
                    - t.metricas_progreso.entregas_calificadas
                )
                > 0
            ][
                :10
            ],  # Top 10 con más entregas pendientes
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando dashboard: {e!s}",
        ) from e

# ========================================================
# === GOOGLE WORKSPACE INTEGRATION ===
# ========================================================


def _pick_value(data: dict[str, Any], *keys: str) -> Any:
    """Retorna el primer valor disponible en el diccionario para las llaves dadas."""

    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    return None


def _normalize_google_resource(
    resource: dict[str, Any],
    resource_type: GoogleResourceType,
    share_with_teacher: bool,
) -> dict[str, Any]:
    """Normaliza la respuesta de Google para almacenarla en la entrega."""

    resource_id = _pick_value(resource, "id", "documentId", "spreadsheetId", "fileId")
    if not resource_id:
        raise ValueError("Respuesta de Google sin identificador de recurso")

    name = _pick_value(resource, "name", "title") or f"Recurso {resource_type.value}"
    url = _pick_value(resource, "url", "web_view_link", "webViewLink", "webContentLink")
    if not url:
        url = f"https://drive.google.com/file/d/{resource_id}/view"

    created_at = _pick_value(
        resource,
        "created_at",
        "createdAt",
        "created_time",
        "createdTime",
    ) or datetime.now(timezone.utc).isoformat()

    return {
        "id": resource_id,
        "type": resource_type.value,
        "name": name,
        "url": url,
        "web_view_link": url,
        "created_at": created_at,
        "shared_with_teacher": share_with_teacher,
        "permissions": resource.get("permissions", []),
        "metadata": resource,
        "linked": True,
    }


def _ensure_google_resource_shape(resource: dict[str, Any]) -> dict[str, Any]:
    """Garantiza que un recurso almacenado tenga las claves esperadas por el frontend."""

    if not resource:
        return {}

    metadata = resource.get("metadata") or resource
    raw_type = resource.get("type") or resource.get("resource_type") or GoogleResourceType.DOCUMENT.value
    try:
        resource_type = GoogleResourceType(raw_type)
    except ValueError:
        resource_type = GoogleResourceType.DOCUMENT

    normalized = _normalize_google_resource(
        resource=metadata,
        resource_type=resource_type,
        share_with_teacher=resource.get("shared_with_teacher", True),
    )

    normalized.update(
        {
            "id": resource.get("id") or normalized["id"],
            "name": resource.get("name") or normalized["name"],
            "url": resource.get("url") or normalized["url"],
            "web_view_link": resource.get("web_view_link")
            or resource.get("webViewLink")
            or normalized["web_view_link"],
            "created_at": resource.get("created_at")
            or resource.get("createdAt")
            or normalized["created_at"],
            "shared_with_teacher": resource.get("shared_with_teacher", normalized["shared_with_teacher"]),
            "permissions": resource.get("permissions") or normalized["permissions"],
            "metadata": resource.get("metadata", metadata),
            "linked": resource.get("linked", normalized["linked"]),
        }
    )

    return normalized


@router.post(
    "/{tarea_id}/google-workspace/create",
    response_model=dict,
    status_code=status.HTTP_201_CREATED
)
async def create_google_workspace_resource(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    resource_data: GoogleResourceCreate,
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un recurso de Google Workspace y lo vincula a la entrega del estudiante.
    
    Flujo:
    1. Verificar que el usuario es estudiante y tiene OAuth token válido
    2. Obtener credenciales Google del usuario desde BD
    3. Crear recurso en Google (Docs, Sheets, Slides, etc.)
    4. Compartir con docente si se solicita
    5. Guardar metadata en EntregaTarea.google_resources
    6. Retornar URL y metadata del recurso
    """
    from src.services.google_workspace_manager import (
        GoogleResourceType,
        google_workspace_manager,
    )
    from src.crud.auth.oauth_crud import crud_oauth_provider
    from google.oauth2.credentials import Credentials
    
    # Verificar que es estudiante
    try:
        if not hasattr(current_user, "estudiante"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los estudiantes pueden crear recursos Google Workspace"
            )
        
        # Verificar que la tarea existe
        # NOTA: Usamos query directa porque crud_tarea.get asume id y el modelo usa tarea_id
        tarea = db.query(Tarea).filter(Tarea.tarea_id == tarea_id).first()
        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        
        # Obtener credenciales OAuth del usuario
        oauth_data = crud_oauth_provider.get_by_usuario_and_provider(
            db=db,
            usuario_id=current_user.usuario_id,
            provider="google"
        )
        
        if not oauth_data or not oauth_data.access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se encontraron credenciales de Google. Por favor, conecta tu cuenta de Google primero."
            )
        
        # Obtener client_id y client_secret de settings
        from src.core.config import settings
        
        # Crear objeto Credentials
        credentials = Credentials(
            token=oauth_data.access_token,
            refresh_token=oauth_data.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET
        )
        
        # Crear recurso en Google Workspace
        resource_type = GoogleResourceType(resource_data.type)
        logger.info(
            "Creando recurso Google %s con título '%s' para usuario %s",
            resource_type,
            resource_data.title,
            current_user.usuario_id,
        )

        resource = await google_workspace_manager.create_resource(
            resource_type=resource_type,
            title=resource_data.title,
            credentials=credentials,
            folder_id=resource_data.folder_id,
            initial_content=resource_data.initial_content,
            headers=resource_data.headers,
            description=resource_data.description,
        )

        normalized_resource = _normalize_google_resource(
            resource=resource,
            resource_type=resource_type,
            share_with_teacher=resource_data.share_with_teacher,
        )
        
        # Compartir con docente si se solicita
        share_with_teacher = resource_data.share_with_teacher
        if share_with_teacher:
            # Obtener email del docente (creador de la tarea -> curso -> docente)
            # Simplificación: Asumimos que el creador del curso es el docente
            # TODO: Mejorar lógica para obtener email del docente correcto
            pass
            
        # Guardar metadata en EntregaTarea
        # 1. Obtener o crear entrega
        entrega = crud_entrega_tarea.get_by_tarea_and_estudiante(
            db=db,
            tarea_id=tarea_id,
            estudiante_id=current_user.usuario_id
        )
        
        if not entrega:
            # Crear entrega vacía si no existe
            from src.schemas.academic.tarea_schemas import EntregaTareaCreate
            from src.schemas.academic.tarea_schemas import EstadoEntrega
            entrega_in = EntregaTareaCreate(
                tarea_id=tarea_id,
                estudiante_id=current_user.usuario_id,
                comentarios="",
                estado=EstadoEntrega.borrador
            )
            entrega = crud_entrega_tarea.create(db=db, obj_in=entrega_in)
            
        # 2. Actualizar lista de recursos
        current_resources = entrega.google_resources or []
        current_resources.append(normalized_resource)

        from src.schemas.academic.tarea_schemas import EntregaTareaUpdate
        entrega_update = EntregaTareaUpdate(google_resources=current_resources)
        crud_entrega_tarea.update(db=db, db_obj=entrega, obj_in=entrega_update)
        
        return {
            "message": "Recurso creado y vinculado exitosamente",
            "resource": normalized_resource,
            "entrega_id": entrega.entrega_id
        }
    except ValueError as exc:
        logger.warning("Error de validación al crear recurso Google Workspace: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error CRITICO al crear recurso Google Workspace: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/{tarea_id}/google-workspace/resources",
    response_model=list[dict]
)
async def get_google_workspace_resources(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene todos los recursos Google Workspace vinculados a la entrega del estudiante."""
    # Verificar que es estudiante
    if not hasattr(current_user, "estudiante"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden ver sus recursos"
        )
    
    # Obtener entrega del estudiante
    entrega = crud_entrega_tarea.get_by_tarea_and_estudiante(
        db=db,
        tarea_id=tarea_id,
        estudiante_id=current_user.usuario_id
    )
    
    if not entrega:
        return []
    
    stored_resources = entrega.google_resources or []
    return [_ensure_google_resource_shape(resource) for resource in stored_resources]


@router.delete(
    "/{tarea_id}/google-workspace/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_google_workspace_resource(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    resource_id: str,
    delete_from_drive: bool = Query(
        False,
        description="Si se debe eliminar también de Google Drive"
    ),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina el vínculo de un recurso Google Workspace de la entrega."""
    from src.services.google_workspace_manager import google_workspace_manager
    from src.crud.auth.oauth_crud import crud_oauth_provider
    from google.oauth2.credentials import Credentials
    
    # Verificar que es estudiante
    if not hasattr(current_user, "estudiante"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden eliminar sus recursos"
        )
    
    # Obtener entrega
    entrega = crud_entrega_tarea.get_by_tarea_and_estudiante(
        db=db,
        tarea_id=tarea_id,
        estudiante_id=current_user.usuario_id
    )
    
    if not entrega:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró entrega para esta tarea"
        )
    
    # Eliminar recurso de la lista
    google_resources = entrega.google_resources or []

    def _resource_is_different(resource: dict[str, Any]) -> bool:
        candidate = _pick_value(resource, "id", "resource_id")
        if not candidate and isinstance(resource.get("metadata"), dict):
            candidate = _pick_value(resource.get("metadata", {}), "id", "resource_id")
        return candidate != resource_id

    google_resources = [r for r in google_resources if _resource_is_different(r)]
    
    from src.schemas.academic.tarea_schemas import EntregaTareaUpdate
    entrega_update = EntregaTareaUpdate(google_resources=google_resources)
    crud_entrega_tarea.update(db=db, db_obj=entrega, obj_in=entrega_update)
    
    # Si se solicita, eliminar también de Drive
    if delete_from_drive:
        try:
            oauth_data = crud_oauth_provider.get_by_usuario_and_provider(
                db=db,
                usuario_id=current_user.usuario_id,
                provider="google"
            )
            
            if oauth_data:
                from src.core.config import settings
                
                credentials = Credentials(
                    token=oauth_data.access_token,
                    refresh_token=oauth_data.refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET
                )
                
                await google_workspace_manager.delete_resource(
                    resource_id=resource_id,
                    credentials=credentials
                )
                logger.info(f"Recurso {resource_id} eliminado de Google Drive")
        except Exception as e:
            logger.warning(f"No se pudo eliminar de Drive: {e}")
    
    logger.info(f"Vínculo de recurso {resource_id} eliminado de entrega {entrega.entrega_id}")
