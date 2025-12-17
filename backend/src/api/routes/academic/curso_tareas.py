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


@router.get("/{curso_id}/reporte/export")
async def exportar_reporte_curso(
    curso_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Exporta un reporte completo del curso en formato CSV.
    
    El reporte incluye:
    - Información del curso (nombre, código, institución)
    - Lista de todos los estudiantes inscritos
    - Todas las tareas asignadas al curso
    - Estado de entrega y calificaciones para cada estudiante-tarea
    - Métricas calculadas (promedio, % entregas, etc.)
    
    **Formato CSV:**
    - Header con información del curso
    - Columnas: ID, Nombres, Apellidos, Email, [Tarea1], [Tarea2], ..., Promedio, Total Entregas, % Entregas
    - Cada tarea muestra: calificación, "No entregó", o "Entregada - Sin calificar"
    
    **Permisos:** Solo coordinadores y docentes del curso pueden exportar.
    """
    from fastapi import HTTPException
    from fastapi.responses import Response
    from datetime import datetime
    from sqlalchemy import and_
    from src.models.academic.curso import Curso
    from src.models.academic.grupo_curso import GrupoCurso
    from src.models.academic.grupo import Grupo
    from src.models.academic.estudiante_grupo import EstudianteGrupo
    from src.models.users.estudiante import Estudiante
    from src.models.users.usuario import Usuario as UsuarioModel
    from src.models.academic.tarea import Tarea, EntregaTarea
    import csv
    from io import StringIO
    
    logger.info(f"GET reporte export curso {curso_id} - Usuario: {current_user.usuario_id}")
    
    # Verificar permisos (solo coordinadores y docentes)
    if current_user.rol not in ['coordinador', 'docente']:
        raise HTTPException(
            status_code=403,
            detail="Solo coordinadores y docentes pueden exportar reportes"
        )
    
    # Obtener información del curso
    curso = db.query(Curso).filter(Curso.curso_id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Obtener institución
    institucion_nombre = curso.institucion.nombre if curso.institucion else "N/A"
    
    # Obtener todos los grupos asociados al curso
    grupos_ids = db.query(GrupoCurso.grupo_id).filter(
        GrupoCurso.curso_id == curso_id
    ).all()
    grupos_ids = [g[0] for g in grupos_ids]
    
    # Obtener todos los estudiantes del curso
    estudiantes_data = db.query(
        UsuarioModel.usuario_id,
        UsuarioModel.nombres,
        UsuarioModel.apellidos,
        UsuarioModel.correo_institucional,
        Estudiante.fecha_ingreso
    ).join(
        Estudiante, Estudiante.estudiante_id == UsuarioModel.usuario_id
    ).join(
        EstudianteGrupo, EstudianteGrupo.estudiante_id == Estudiante.estudiante_id
    ).filter(
        EstudianteGrupo.grupo_id.in_(grupos_ids)
    ).distinct().all()
    
    if not estudiantes_data:
        logger.warning(f"No hay estudiantes inscritos en el curso {curso_id}")
    
    # Obtener todas las tareas del curso
    tareas = db.query(Tarea).filter(
        Tarea.grupo_id.in_(grupos_ids)
    ).order_by(Tarea.fecha_limite).all()
    
    if not tareas:
        logger.warning(f"No hay tareas asignadas en el curso {curso_id}")
    
    # Crear CSV en memoria
    output = StringIO()
    
    # Agregar BOM UTF-8 para compatibilidad con Excel
    output.write('\ufeff')
    
    writer = csv.writer(output)
    
    # Header del reporte
    writer.writerow([f"Curso: {curso.nombre} ({curso.codigo_curso or 'N/A'})"])
    writer.writerow([f"Institución: {institucion_nombre}"])
    writer.writerow([f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    writer.writerow([f"Total estudiantes: {len(estudiantes_data)}"])
    writer.writerow([f"Total tareas: {len(tareas)}"])
    writer.writerow([])  # Línea vacía
    
    # Construir headers de columnas
    headers = [
        "ID Estudiante",
        "Nombres",
        "Apellidos",
        "Email",
        "Fecha Ingreso"
    ]
    
    # Agregar columnas de tareas
    for tarea in tareas:
        fecha_limite = tarea.fecha_limite.strftime('%Y-%m-%d') if tarea.fecha_limite else 'N/A'
        puntaje_max = tarea.puntuacion_maxima or 100
        headers.append(f"{tarea.titulo} - Max: {puntaje_max}pts - Límite: {fecha_limite}")
    
    # Agregar columnas de métricas
    headers.extend(["Promedio", "Tareas Entregadas", "% Entregas"])
    
    writer.writerow(headers)
    
    # Procesar cada estudiante
    for est_data in estudiantes_data:
        estudiante_id = str(est_data.usuario_id)
        row = [
            estudiante_id,
            est_data.nombres or "",
            est_data.apellidos or "",
            est_data.correo_institucional or "",
            est_data.fecha_ingreso.strftime('%Y-%m-%d') if est_data.fecha_ingreso else ""
        ]
        
        calificaciones = []
        tareas_entregadas = 0
        
        # Para cada tarea, buscar la entrega del estudiante
        for tarea in tareas:
            entrega = db.query(EntregaTarea).filter(
                and_(
                    EntregaTarea.tarea_id == tarea.tarea_id,
                    EntregaTarea.estudiante_id == estudiante_id
                )
            ).first()
            
            if entrega:
                if entrega.calificacion is not None:
                    # Tiene calificación
                    calificaciones.append(float(entrega.calificacion))
                    tardia = " (Tardía)" if entrega.es_entrega_tardia or entrega.es_tardia else ""
                    row.append(f"{entrega.calificacion}{tardia}")
                    tareas_entregadas += 1
                else:
                    # Entregada pero sin calificar
                    row.append("Entregada - Sin calificar")
                    tareas_entregadas += 1
            else:
                # No entregó
                row.append("No entregó")
        
        # Calcular métricas
        promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0
        porcentaje_entregas = (tareas_entregadas / len(tareas) * 100) if tareas else 0
        
        row.append(f"{promedio:.2f}")
        row.append(str(tareas_entregadas))
        row.append(f"{porcentaje_entregas:.1f}%")
        
        writer.writerow(row)
    
    # Obtener contenido CSV
    csv_content = output.getvalue()
    output.close()
    
    # Generar nombre de archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reporte_curso_{curso.codigo_curso or curso_id}_{timestamp}.csv"
    
    logger.info(f"Reporte generado exitosamente: {filename} - {len(estudiantes_data)} estudiantes, {len(tareas)} tareas")
    
    # Retornar como respuesta CSV
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
