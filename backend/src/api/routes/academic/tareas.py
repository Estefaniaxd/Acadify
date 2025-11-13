from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from src.api.api.dependencies import get_current_user, get_db
from src.api.core.storage import upload_file_to_storage
from src.api.crud.academic.tarea import crud_entrega_tarea, crud_rubrica, crud_tarea
from src.api.enums.academic.tareas import EstadoEntrega, EstadoTarea
from src.api.models.users.usuario import Usuario
from src.api.schemas.academic.tarea_enriched import RespuestaPaginada, TareaEnriquecida
from src.api.schemas.academic.tarea_schemas import (
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
from src.api.services.academic.tarea_enriched_service import (
    crear_servicio_tareas_enriquecidas,
)


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


@router.get("/{tarea_id}", response_model=TareaDetallada)
def obtener_tarea(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener una tarea específica con detalles completos."""
    tarea = crud_tarea.obtener_tarea_detallada(db=db, tarea_id=tarea_id)
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )

    return tarea


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
    """Crear una nueva entrega de tarea."""
    # Verificar que el usuario sea estudiante
    if not hasattr(current_user, "estudiante"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden entregar tareas",
        )

    # Verificar que la tarea existe y está activa
    tarea = crud_tarea.get(db=db, id=tarea_id)
    if not tarea or not tarea.activa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o no disponible",
        )

    # Asegurar que el tarea_id y estudiante_id son correctos
    entrega_data.tarea_id = tarea_id
    entrega_data.estudiante_id = current_user.usuario_id

    try:
        return crud_entrega_tarea.crear_entrega(db=db, entrega_data=entrega_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la entrega: {e!s}",
        ) from e


@router.post("/entregas/{entrega_id}/subir-archivo")
async def subir_archivo_entrega(
    *,
    db: Session = Depends(get_db),
    entrega_id: str,
    archivo: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
):
    """Subir archivo para una entrega."""
    entrega = crud_entrega_tarea.get(db=db, id=entrega_id)
    if not entrega:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada"
        )

    # Verificar permisos
    if entrega.estudiante_id != current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes modificar esta entrega",
        )

    try:
        # Subir archivo al storage
        archivo_url = await upload_file_to_storage(
            archivo, f"entregas/{entrega_id}/{archivo.filename}"
        )

        # Actualizar la entrega con la URL del archivo
        entrega_update = EntregaTareaUpdate(archivo_url=archivo_url)
        crud_entrega_tarea.update(db=db, db_obj=entrega, obj_in=entrega_update)

        return {"mensaje": "Archivo subido correctamente", "archivo_url": archivo_url}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el archivo: {e!s}",
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


@router.patch("/entregas/{entrega_id}/calificar", response_model=EntregaTareaResponse)
def calificar_entrega(
    *,
    db: Session = Depends(get_db),
    entrega_id: str,
    calificacion_data: CalificarEntrega,
    current_user: Usuario = Depends(get_current_user),
):
    """Calificar una entrega."""
    # Verificar que el usuario sea docente
    if not hasattr(current_user, "docente") and not hasattr(
        current_user, "coordinador"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden calificar entregas",
        )

    try:
        entrega = crud_entrega_tarea.calificar_entrega(
            db=db,
            entrega_id=entrega_id,
            calificacion_data=calificacion_data,
            calificado_por=current_user.usuario_id,
        )

        if not entrega:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada"
            )

        return entrega

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
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
        from src.api.schemas.academic.tarea_enriched import (
            EstadoVisualizacion,
            FiltrosTareaEnriquecida,
        )

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
        from src.api.schemas.academic.tarea_enriched import FiltrosTareaEnriquecida

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
