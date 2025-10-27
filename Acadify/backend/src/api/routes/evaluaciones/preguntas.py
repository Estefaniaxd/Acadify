"""
API routes para gestión de preguntas de examen
Incluye creación, edición, reordenamiento e importación desde banco
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, get_db
from src.crud.evaluaciones import pregunta_examen, banco_pregunta, examen
from src.schemas.evaluaciones import (
    PreguntaExamenCreate, PreguntaExamenUpdate, PreguntaExamenResponse,
    PreguntaParaEstudiante
)
from src.models.evaluaciones import TipoPregunta, DificultadPregunta
from src.models.users.usuario import Usuario

router = APIRouter()


@router.post("/", response_model=PreguntaExamenResponse, status_code=status.HTTP_201_CREATED)
def crear_pregunta(
    *,
    db: Session = Depends(get_db),
    pregunta_in: PreguntaExamenCreate,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear una nueva pregunta para un examen.
    Solo el creador del examen puede añadir preguntas.
    """
    # Verificar que el examen existe y el usuario tiene permisos
    exam = examen.get(db=db, id=pregunta_in.examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Examen no encontrado"
        )
    
    # Verificar permisos
    puede_editar = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam.creado_por == current_user.user_id)
    )
    
    if not puede_editar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para añadir preguntas a este examen"
        )
    
    # Crear pregunta con orden automático
    created_pregunta = pregunta_examen.create_pregunta_con_orden(db=db, obj_in=pregunta_in)
    
    # Actualizar estadísticas del examen
    examen.actualizar_estadisticas_examen(db=db, examen_id=pregunta_in.examen_id)
    
    return created_pregunta


@router.get("/{examen_id}", response_model=List[PreguntaExamenResponse])
def listar_preguntas_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    current_user: Usuario = Depends(get_current_user),
    para_estudiante: bool = Query(False, description="Filtrar información sensible para estudiantes")
):
    """
    Obtener todas las preguntas de un examen.
    """
    # Verificar que el examen existe
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Examen no encontrado"
        )
    
    # Verificar permisos de acceso
    puede_ver = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam.creado_por == current_user.user_id) or
        current_user.role == "estudiante"
    )
    
    if not puede_ver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver las preguntas de este examen"
        )
    
    preguntas = pregunta_examen.get_preguntas_por_examen(db=db, examen_id=examen_id)
    
    # Si es para estudiante, filtrar información sensible
    if para_estudiante or current_user.role == "estudiante":
        preguntas_filtradas = []
        for pregunta in preguntas:
            pregunta_dict = pregunta.__dict__.copy()
            # Remover respuestas correctas y explicaciones
            pregunta_dict.pop('respuesta_correcta', None)
            pregunta_dict.pop('explicacion', None)
            preguntas_filtradas.append(pregunta_dict)
        return preguntas_filtradas
    
    return preguntas


@router.get("/pregunta/{pregunta_id}", response_model=PreguntaExamenResponse)
def obtener_pregunta(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener detalles de una pregunta específica.
    """
    pregunta = pregunta_examen.get(db=db, id=pregunta_id)
    if not pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    # Verificar permisos
    exam = examen.get(db=db, id=pregunta.examen_id)
    puede_ver = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam.creado_por == current_user.user_id)
    )
    
    if not puede_ver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver esta pregunta"
        )
    
    return pregunta


@router.put("/pregunta/{pregunta_id}", response_model=PreguntaExamenResponse)
def actualizar_pregunta(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta"),
    pregunta_in: PreguntaExamenUpdate,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar una pregunta existente.
    """
    pregunta = pregunta_examen.get(db=db, id=pregunta_id)
    if not pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    # Verificar permisos
    exam = examen.get(db=db, id=pregunta.examen_id)
    puede_editar = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam.creado_por == current_user.user_id)
    )
    
    if not puede_editar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar esta pregunta"
        )
    
    # Verificar si el examen permite edición
    if exam.estado.value not in ["borrador", "publicado"] and exam.total_intentos > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede editar preguntas de un examen con intentos realizados"
        )
    
    updated_pregunta = pregunta_examen.update(db=db, db_obj=pregunta, obj_in=pregunta_in)
    
    # Actualizar estadísticas del examen
    examen.actualizar_estadisticas_examen(db=db, examen_id=pregunta.examen_id)
    
    return updated_pregunta


@router.delete("/pregunta/{pregunta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pregunta(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Eliminar una pregunta y reordenar las siguientes.
    """
    pregunta = pregunta_examen.get(db=db, id=pregunta_id)
    if not pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    # Verificar permisos
    exam = examen.get(db=db, id=pregunta.examen_id)
    puede_eliminar = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam.creado_por == current_user.user_id)
    )
    
    if not puede_eliminar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar esta pregunta"
        )
    
    # Verificar si se puede eliminar
    if exam.total_intentos > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar preguntas de un examen con intentos realizados"
        )
    
    # Eliminar con reordenamiento automático
    success = pregunta_examen.eliminar_con_reordenamiento(db=db, pregunta_id=pregunta_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la pregunta"
        )
    
    # Actualizar estadísticas del examen
    examen.actualizar_estadisticas_examen(db=db, examen_id=pregunta.examen_id)


@router.post("/{examen_id}/reordenar", response_model=List[PreguntaExamenResponse])
def reordenar_preguntas(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    nuevos_ordenes: List[Dict[str, Any]] = Body(..., description="Lista con nuevos órdenes"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Reordenar preguntas de un examen.
    
    Body format:
    [
        {"pregunta_id": "id1", "nuevo_orden": 1},
        {"pregunta_id": "id2", "nuevo_orden": 2},
        ...
    ]
    """
    # Verificar que el examen existe
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Examen no encontrado"
        )
    
    # Verificar permisos
    puede_reordenar = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam.creado_por == current_user.user_id)
    )
    
    if not puede_reordenar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para reordenar preguntas de este examen"
        )
    
    # Verificar formato de datos
    required_keys = {"pregunta_id", "nuevo_orden"}
    for item in nuevos_ordenes:
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Formato incorrecto. Se requiere pregunta_id y nuevo_orden"
            )
    
    try:
        preguntas_reordenadas = pregunta_examen.reordenar_preguntas(
            db=db, examen_id=examen_id, nuevos_ordenes=nuevos_ordenes
        )
        return preguntas_reordenadas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reordenar preguntas: {str(e)}"
        )


@router.post("/{examen_id}/importar-desde-banco", response_model=PreguntaExamenResponse)
def importar_pregunta_desde_banco(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    banco_pregunta_id: str = Body(..., embed=True, description="ID de la pregunta en el banco"),
    puntuacion_personalizada: Optional[float] = Body(None, embed=True, description="Puntuación personalizada"),
    orden_personalizado: Optional[int] = Body(None, embed=True, description="Orden personalizado"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Importar una pregunta del banco de preguntas a un examen.
    """
    # Verificar que el examen existe
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Examen no encontrado"
        )
    
    # Verificar permisos
    puede_importar = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam.creado_por == current_user.user_id)
    )
    
    if not puede_importar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para importar preguntas a este examen"
        )
    
    # Importar pregunta
    pregunta_importada = pregunta_examen.importar_desde_banco(
        db=db,
        examen_id=examen_id,
        banco_pregunta_id=banco_pregunta_id,
        puntuacion_personalizada=puntuacion_personalizada,
        orden_personalizado=orden_personalizado
    )
    
    if not pregunta_importada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta del banco no encontrada"
        )
    
    # Actualizar estadísticas del examen
    examen.actualizar_estadisticas_examen(db=db, examen_id=examen_id)
    
    return pregunta_importada


@router.post("/pregunta/{pregunta_id}/duplicar", response_model=PreguntaExamenResponse)
def duplicar_pregunta(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta a duplicar"),
    nuevo_examen_id: Optional[str] = Body(None, embed=True, description="ID del examen destino (opcional)"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Duplicar una pregunta, opcionalmente a otro examen.
    """
    pregunta_original = pregunta_examen.get(db=db, id=pregunta_id)
    if not pregunta_original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta a duplicar no encontrada"
        )
    
    # Verificar permisos sobre la pregunta original
    exam_original = examen.get(db=db, id=pregunta_original.examen_id)
    puede_duplicar = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam_original.creado_por == current_user.user_id)
    )
    
    if not puede_duplicar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para duplicar esta pregunta"
        )
    
    # Si se especifica un examen destino diferente, verificar permisos
    if nuevo_examen_id and nuevo_examen_id != pregunta_original.examen_id:
        exam_destino = examen.get(db=db, id=nuevo_examen_id)
        if not exam_destino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Examen destino no encontrado"
            )
        
        puede_editar_destino = (
            current_user.role in ["coordinador", "administrador"] or
            (current_user.role == "docente" and exam_destino.creado_por == current_user.user_id)
        )
        
        if not puede_editar_destino:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para añadir preguntas al examen destino"
            )
    
    # Duplicar pregunta
    pregunta_duplicada = pregunta_examen.duplicar_pregunta(
        db=db, pregunta_id=pregunta_id, nuevo_examen_id=nuevo_examen_id
    )
    
    if not pregunta_duplicada:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al duplicar la pregunta"
        )
    
    # Actualizar estadísticas del examen destino
    examen_destino_id = nuevo_examen_id or pregunta_original.examen_id
    examen.actualizar_estadisticas_examen(db=db, examen_id=examen_destino_id)
    
    return pregunta_duplicada


@router.get("/pregunta/{pregunta_id}/estadisticas")
def obtener_estadisticas_pregunta(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener estadísticas detalladas de una pregunta.
    """
    pregunta = pregunta_examen.get(db=db, id=pregunta_id)
    if not pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    # Verificar permisos
    exam = examen.get(db=db, id=pregunta.examen_id)
    puede_ver_estadisticas = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam.creado_por == current_user.user_id)
    )
    
    if not puede_ver_estadisticas:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estadísticas de esta pregunta"
        )
    
    estadisticas = pregunta_examen.get_estadisticas_pregunta(db=db, pregunta_id=pregunta_id)
    return estadisticas


@router.get("/pregunta/{pregunta_id}/validar")
def validar_pregunta(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Validar configuración de una pregunta.
    """
    pregunta = pregunta_examen.get(db=db, id=pregunta_id)
    if not pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    # Verificar permisos
    exam = examen.get(db=db, id=pregunta.examen_id)
    puede_validar = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam.creado_por == current_user.user_id)
    )
    
    if not puede_validar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para validar esta pregunta"
        )
    
    validacion = pregunta_examen.validar_pregunta(db=db, pregunta_id=pregunta_id)
    return validacion