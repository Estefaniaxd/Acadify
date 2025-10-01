from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime

from ...api.dependencies import get_current_user, get_db
from ...models.users.usuario import Usuario
from ...crud.academic.tarea import crud_tarea, crud_entrega_tarea, crud_rubrica
from ...schemas.academic.tarea_schemas import (
    TareaResponse, TareaDetallada, TareaCreate, TareaUpdate, FiltrosTarea,
    EntregaTareaResponse, EntregaTareaDetallada, EntregaTareaCreate, EntregaTareaUpdate,
    CalificarEntrega, FiltrosEntrega, EstadisticasTarea, EstadisticasEntrega,
    RubricaResponse, RubricaDetallada, RubricaCreate, RubricaUpdate
)
from ...enums.academic.tareas import EstadoTarea, EstadoEntrega
from ...core.storage import upload_file_to_storage

router = APIRouter()

# === RUTAS PARA TAREAS ===

@router.post("/", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_data: TareaCreate,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear una nueva tarea
    """
    # Verificar que el usuario sea docente o coordinador
    if not hasattr(current_user, 'docente') and not hasattr(current_user, 'coordinador'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes y coordinadores pueden crear tareas"
        )
    
    try:
        tarea = crud_tarea.crear_tarea(
            db=db,
            tarea_data=tarea_data,
            creado_por=current_user.usuario_id
        )
        return tarea
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la tarea: {str(e)}"
        )

@router.get("/grupo/{grupo_id}", response_model=List[TareaResponse])
def obtener_tareas_grupo(
    *,
    db: Session = Depends(get_db),
    grupo_id: str,
    estado: Optional[EstadoTarea] = Query(None),
    tipo_tarea: Optional[str] = Query(None),
    solo_activas: bool = Query(True),
    busqueda: Optional[str] = Query(None),
    ordenar_por: str = Query("fecha_limite"),
    orden_desc: bool = Query(False),
    pagina: int = Query(1, ge=1),
    tamaño_pagina: int = Query(20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener todas las tareas de un grupo con filtros
    """
    filtros = FiltrosTarea(
        grupo_id=grupo_id,
        estado=estado,
        solo_activas=solo_activas,
        busqueda=busqueda,
        ordenar_por=ordenar_por,
        orden_desc=orden_desc,
        pagina=pagina,
        tamaño_pagina=tamaño_pagina
    )
    
    tareas = crud_tarea.obtener_tareas_por_grupo(
        db=db,
        grupo_id=grupo_id,
        filtros=filtros,
        usuario_id=current_user.usuario_id
    )
    
    return tareas

@router.get("/docente/{docente_id}", response_model=List[TareaResponse])
def obtener_tareas_docente(
    *,
    db: Session = Depends(get_db),
    docente_id: str,
    solo_activas: bool = Query(True),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener todas las tareas creadas por un docente
    """
    # Verificar permisos: solo el propio docente o coordinadores pueden ver esto
    if (current_user.usuario_id != docente_id and 
        not hasattr(current_user, 'coordinador')):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estas tareas"
        )
    
    filtros = FiltrosTarea(solo_activas=solo_activas)
    tareas = crud_tarea.obtener_tareas_por_docente(
        db=db,
        docente_id=docente_id,
        filtros=filtros
    )
    
    return tareas

@router.get("/{tarea_id}", response_model=TareaDetallada)
def obtener_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener una tarea específica con detalles completos
    """
    tarea = crud_tarea.obtener_tarea_detallada(db=db, tarea_id=tarea_id)
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    return tarea

@router.put("/{tarea_id}", response_model=TareaResponse)
def actualizar_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    tarea_update: TareaUpdate,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar una tarea existente
    """
    tarea = crud_tarea.get(db=db, id=tarea_id)
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    # Verificar permisos: solo el creador o coordinadores pueden editar
    if (tarea.docente_id != current_user.usuario_id and 
        not hasattr(current_user, 'coordinador')):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar esta tarea"
        )
    
    tarea_actualizada = crud_tarea.update(
        db=db,
        db_obj=tarea,
        obj_in=tarea_update
    )
    
    return tarea_actualizada

@router.patch("/{tarea_id}/estado", response_model=TareaResponse)
def cambiar_estado_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    nuevo_estado: EstadoTarea,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambiar el estado de una tarea
    """
    tarea = crud_tarea.actualizar_estado_tarea(
        db=db,
        tarea_id=tarea_id,
        nuevo_estado=nuevo_estado,
        actualizado_por=current_user.usuario_id
    )
    
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    return tarea

@router.get("/{tarea_id}/estadisticas", response_model=dict)
def obtener_estadisticas_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener estadísticas detalladas de una tarea
    """
    estadisticas = crud_tarea.obtener_estadisticas_tarea(db=db, tarea_id=tarea_id)
    if not estadisticas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    return estadisticas

@router.delete("/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Eliminar (desactivar) una tarea
    """
    tarea = crud_tarea.get(db=db, id=tarea_id)
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    # Verificar permisos
    if (tarea.docente_id != current_user.usuario_id and 
        not hasattr(current_user, 'coordinador')):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar esta tarea"
        )
    
    crud_tarea.remove(db=db, id=tarea_id)

# === RUTAS PARA ENTREGAS ===

@router.post("/{tarea_id}/entregas", response_model=EntregaTareaResponse, status_code=status.HTTP_201_CREATED)
def crear_entrega(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    entrega_data: EntregaTareaCreate,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear una nueva entrega de tarea
    """
    # Verificar que el usuario sea estudiante
    if not hasattr(current_user, 'estudiante'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden entregar tareas"
        )
    
    # Verificar que la tarea existe y está activa
    tarea = crud_tarea.get(db=db, id=tarea_id)
    if not tarea or not tarea.activa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o no disponible"
        )
    
    # Asegurar que el tarea_id y estudiante_id son correctos
    entrega_data.tarea_id = tarea_id
    entrega_data.estudiante_id = current_user.usuario_id
    
    try:
        entrega = crud_entrega_tarea.crear_entrega(db=db, entrega_data=entrega_data)
        return entrega
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la entrega: {str(e)}"
        )

@router.post("/entregas/{entrega_id}/subir-archivo")
async def subir_archivo_entrega(
    *,
    db: Session = Depends(get_db),
    entrega_id: str,
    archivo: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Subir archivo para una entrega
    """
    entrega = crud_entrega_tarea.get(db=db, id=entrega_id)
    if not entrega:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrega no encontrada"
        )
    
    # Verificar permisos
    if entrega.estudiante_id != current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes modificar esta entrega"
        )
    
    try:
        # Subir archivo al storage
        archivo_url = await upload_file_to_storage(
            archivo,
            f"entregas/{entrega_id}/{archivo.filename}"
        )
        
        # Actualizar la entrega con la URL del archivo
        entrega_update = EntregaTareaUpdate(archivo_url=archivo_url)
        entrega_actualizada = crud_entrega_tarea.update(
            db=db,
            db_obj=entrega,
            obj_in=entrega_update
        )
        
        return {"mensaje": "Archivo subido correctamente", "archivo_url": archivo_url}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el archivo: {str(e)}"
        )

@router.patch("/entregas/{entrega_id}/entregar", response_model=EntregaTareaResponse)
def entregar_tarea(
    *,
    db: Session = Depends(get_db),
    entrega_id: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Marcar una entrega como entregada (finalizar entrega)
    """
    entrega = crud_entrega_tarea.entregar_tarea(db=db, entrega_id=entrega_id)
    if not entrega:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrega no encontrada"
        )
    
    return entrega

@router.patch("/entregas/{entrega_id}/calificar", response_model=EntregaTareaResponse)
def calificar_entrega(
    *,
    db: Session = Depends(get_db),
    entrega_id: str,
    calificacion_data: CalificarEntrega,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Calificar una entrega
    """
    # Verificar que el usuario sea docente
    if not hasattr(current_user, 'docente') and not hasattr(current_user, 'coordinador'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden calificar entregas"
        )
    
    try:
        entrega = crud_entrega_tarea.calificar_entrega(
            db=db,
            entrega_id=entrega_id,
            calificacion_data=calificacion_data,
            calificado_por=current_user.usuario_id
        )
        
        if not entrega:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrega no encontrada"
            )
        
        return entrega
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{tarea_id}/entregas", response_model=List[EntregaTareaResponse])
def obtener_entregas_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    estado: Optional[EstadoEntrega] = Query(None),
    solo_calificadas: Optional[bool] = Query(None),
    solo_pendientes: Optional[bool] = Query(None),
    pagina: int = Query(1, ge=1),
    tamaño_pagina: int = Query(20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener todas las entregas de una tarea
    """
    filtros = FiltrosEntrega(
        tarea_id=tarea_id,
        estado=estado,
        solo_calificadas=solo_calificadas,
        solo_pendientes=solo_pendientes,
        pagina=pagina,
        tamaño_pagina=tamaño_pagina
    )
    
    entregas = crud_entrega_tarea.obtener_entregas_por_tarea(
        db=db,
        tarea_id=tarea_id,
        filtros=filtros
    )
    
    return entregas

@router.get("/entregas/{entrega_id}", response_model=EntregaTareaDetallada)
def obtener_entrega(
    *,
    db: Session = Depends(get_db),
    entrega_id: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener una entrega específica con detalles completos
    """
    entrega = crud_entrega_tarea.obtener_entrega_detallada(db=db, entrega_id=entrega_id)
    if not entrega:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrega no encontrada"
        )
    
    return entrega

# === RUTAS PARA RÚBRICAS ===

@router.post("/rubricas", response_model=RubricaResponse, status_code=status.HTTP_201_CREATED)
def crear_rubrica(
    *,
    db: Session = Depends(get_db),
    rubrica_data: RubricaCreate,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear una nueva rúbrica
    """
    if not hasattr(current_user, 'docente') and not hasattr(current_user, 'coordinador'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden crear rúbricas"
        )
    
    rubrica_data.creado_por = current_user.usuario_id
    rubrica = crud_rubrica.create(db=db, obj_in=rubrica_data)
    
    return rubrica

@router.get("/rubricas", response_model=List[RubricaResponse])
def obtener_rubricas(
    *,
    db: Session = Depends(get_db),
    incluir_publicas: bool = Query(True),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener rúbricas del docente actual
    """
    rubricas = crud_rubrica.obtener_rubricas_por_docente(
        db=db,
        docente_id=current_user.usuario_id,
        incluir_publicas=incluir_publicas
    )
    
    return rubricas

@router.get("/rubricas/publicas", response_model=List[RubricaResponse])
def obtener_rubricas_publicas(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener todas las rúbricas públicas
    """
    rubricas = crud_rubrica.obtener_rubricas_publicas(db=db)
    return rubricas

@router.post("/rubricas/{rubrica_id}/duplicar", response_model=RubricaResponse)
def duplicar_rubrica(
    *,
    db: Session = Depends(get_db),
    rubrica_id: str,
    nuevo_nombre: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Duplicar una rúbrica existente
    """
    rubrica = crud_rubrica.duplicar_rubrica(
        db=db,
        rubrica_id=rubrica_id,
        nuevo_nombre=nuevo_nombre,
        creado_por=current_user.usuario_id
    )
    
    if not rubrica:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rúbrica no encontrada"
        )
    
    return rubrica