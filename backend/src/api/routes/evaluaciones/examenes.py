"""API routes para gestión de exámenes
Incluye creación, edición, publicación y gestión de exámenes.
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, get_db
from src.crud.evaluaciones import examen, pregunta_examen
from src.models.evaluaciones import EstadoExamen, TipoExamen
from src.models.users.usuario import Usuario
from src.schemas.evaluaciones import (
    ExamenCompleto,
    ExamenCreate,
    ExamenResponse,
    ExamenUpdate,
)


router = APIRouter()


@router.post("/", response_model=ExamenResponse, status_code=status.HTTP_201_CREATED)
def crear_examen(
    *,
    db: Session = Depends(get_db),
    exam_in: ExamenCreate,
    current_user: Usuario = Depends(get_current_user),
):
    """Crear un nuevo examen.
    Solo profesores y coordinadores pueden crear exámenes.
    """
    # Verificar permisos
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear exámenes",
        )

    # Asegurar que el creador es el usuario actual
    exam_in.creado_por = current_user.user_id

    # Crear el examen
    return examen.create(db=db, obj_in=exam_in)


@router.get("/", response_model=list[ExamenResponse])
def listar_examenes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=200, description="Límite de registros"),
    estado: EstadoExamen | None = Query(None, description="Filtrar por estado"),
    tipo_examen: TipoExamen | None = Query(None, description="Filtrar por tipo"),
    curso_id: str | None = Query(None, description="Filtrar por curso"),
    busqueda: str | None = Query(None, description="Búsqueda por título o descripción"),
):
    """Listar exámenes según el rol del usuario:
    - Profesores: sus propios exámenes
    - Coordinadores: exámenes de su institución
    - Estudiantes: exámenes disponibles para ellos.
    """
    filtros = {}
    if busqueda:
        filtros["busqueda"] = busqueda
    if curso_id:
        filtros["curso_id"] = curso_id
    if estado:
        filtros["estado"] = estado
    if tipo_examen:
        filtros["tipo_examen"] = tipo_examen

    if current_user.role == "estudiante":
        # Estudiantes solo ven exámenes disponibles
        # TODO: Implementar lógica para obtener cursos del estudiante
        examenes = examen.get_examenes_disponibles_para_estudiante(
            db=db, estudiante_id=current_user.user_id
        )
    elif current_user.role in ["docente", "coordinador", "administrador"]:
        if current_user.role == "docente":
            filtros["profesor_id"] = current_user.user_id

        examenes = examen.buscar_examenes(
            db=db, filtros=filtros, skip=skip, limit=limit
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver exámenes",
        )

    return examenes


@router.get("/{examen_id}", response_model=ExamenCompleto)
def obtener_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    current_user: Usuario = Depends(get_current_user),
    incluir_preguntas: bool = Query(True, description="Incluir preguntas del examen"),
):
    """Obtener detalles de un examen específico.
    Los profesores ven toda la información, los estudiantes una versión filtrada.
    """
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Examen no encontrado"
        )

    # Verificar permisos de acceso
    puede_ver_completo = current_user.role in ["coordinador", "administrador"] or (
        current_user.role == "docente" and exam.creado_por == current_user.user_id
    )

    if not puede_ver_completo and current_user.role != "estudiante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este examen",
        )

    # Obtener preguntas si se solicita
    if incluir_preguntas:
        preguntas = pregunta_examen.get_preguntas_por_examen(db=db, examen_id=examen_id)

        # Si es estudiante, filtrar información sensible
        if current_user.role == "estudiante":
            # TODO: Crear versión filtrada para estudiantes
            pass

        # Crear respuesta completa
        exam_dict = exam.__dict__.copy()
        exam_dict["preguntas"] = preguntas
        return exam_dict

    return exam


@router.put("/{examen_id}", response_model=ExamenResponse)
def actualizar_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    exam_in: ExamenUpdate,
    current_user: Usuario = Depends(get_current_user),
):
    """Actualizar un examen existente.
    Solo el creador o un coordinador pueden actualizar.
    """
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Examen no encontrado"
        )

    # Verificar permisos
    puede_editar = current_user.role in ["coordinador", "administrador"] or (
        current_user.role == "docente" and exam.creado_por == current_user.user_id
    )

    if not puede_editar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar este examen",
        )

    # No permitir edición si hay intentos finalizados (opcional)
    if exam.total_intentos > 0 and exam.estado != EstadoExamen.BORRADOR:
        # Solo permitir ciertos cambios
        campos_permitidos = ["descripcion", "instrucciones", "fecha_fin"]
        exam_dict = exam_in.dict(exclude_unset=True)
        for campo in list(exam_dict.keys()):
            if campo not in campos_permitidos:
                del exam_dict[campo]
        exam_in = ExamenUpdate(**exam_dict)

    return examen.update(db=db, db_obj=exam, obj_in=exam_in)


@router.delete("/{examen_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    current_user: Usuario = Depends(get_current_user),
) -> None:
    """Eliminar un examen.
    Solo el creador o un administrador pueden eliminar.
    Solo se puede eliminar si no hay intentos finalizados.
    """
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Examen no encontrado"
        )

    # Verificar permisos
    puede_eliminar = current_user.role == "administrador" or (
        current_user.role == "docente" and exam.creado_por == current_user.user_id
    )

    if not puede_eliminar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este examen",
        )

    # Verificar si hay intentos finalizados
    if exam.total_intentos > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un examen con intentos realizados",
        )

    examen.remove(db=db, id=examen_id)


@router.post("/{examen_id}/publicar", response_model=ExamenResponse)
def publicar_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    current_user: Usuario = Depends(get_current_user),
):
    """Publicar un examen (cambiar de borrador a publicado)."""
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Examen no encontrado"
        )

    # Verificar permisos
    puede_publicar = current_user.role in ["coordinador", "administrador"] or (
        current_user.role == "docente" and exam.creado_por == current_user.user_id
    )

    if not puede_publicar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para publicar este examen",
        )

    try:
        published_exam = examen.publicar_examen(db=db, examen_id=examen_id)
        if not published_exam:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede publicar el examen en su estado actual",
            )
        return published_exam
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post("/{examen_id}/activar", response_model=ExamenResponse)
def activar_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    current_user: Usuario = Depends(get_current_user),
):
    """Activar un examen (permitir que estudiantes lo tomen)."""
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Examen no encontrado"
        )

    # Verificar permisos
    puede_activar = current_user.role in ["coordinador", "administrador"] or (
        current_user.role == "docente" and exam.creado_por == current_user.user_id
    )

    if not puede_activar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para activar este examen",
        )

    activated_exam = examen.activar_examen(db=db, examen_id=examen_id)
    if not activated_exam:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede activar el examen en su estado actual",
        )

    return activated_exam


@router.post("/{examen_id}/finalizar", response_model=ExamenResponse)
def finalizar_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    current_user: Usuario = Depends(get_current_user),
):
    """Finalizar un examen (no permitir más intentos)."""
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Examen no encontrado"
        )

    # Verificar permisos
    puede_finalizar = current_user.role in ["coordinador", "administrador"] or (
        current_user.role == "docente" and exam.creado_por == current_user.user_id
    )

    if not puede_finalizar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para finalizar este examen",
        )

    finalized_exam = examen.finalizar_examen(db=db, examen_id=examen_id)
    if not finalized_exam:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede finalizar el examen en su estado actual",
        )

    return finalized_exam


@router.post("/{examen_id}/duplicar", response_model=ExamenResponse)
def duplicar_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen a duplicar"),
    nuevo_titulo: str = Body(
        ..., embed=True, description="Título para el examen duplicado"
    ),
    current_user: Usuario = Depends(get_current_user),
):
    """Duplicar un examen existente."""
    # Verificar permisos
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para duplicar exámenes",
        )

    duplicated_exam = examen.duplicar_examen(
        db=db,
        examen_id=examen_id,
        nuevo_titulo=nuevo_titulo,
        profesor_id=current_user.user_id,
    )

    if not duplicated_exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Examen a duplicar no encontrado",
        )

    return duplicated_exam


@router.get("/{examen_id}/estadisticas")
def obtener_estadisticas_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener estadísticas detalladas de un examen.
    Solo para profesores y coordinadores.
    """
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Examen no encontrado"
        )

    # Verificar permisos
    puede_ver_estadisticas = current_user.role in ["coordinador", "administrador"] or (
        current_user.role == "docente" and exam.creado_por == current_user.user_id
    )

    if not puede_ver_estadisticas:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estadísticas de este examen",
        )

    # Actualizar estadísticas antes de retornarlas
    examen.actualizar_estadisticas_examen(db=db, examen_id=examen_id)

    # TODO: Implementar generación de estadísticas detalladas
    return {
        "examen_id": examen_id,
        "titulo": exam.titulo,
        "total_preguntas": exam.total_preguntas,
        "total_intentos": exam.total_intentos,
        "promedio_calificacion": exam.promedio_calificacion,
        # Más estadísticas detalladas...
    }


@router.get("/{examen_id}/verificar-acceso")
def verificar_acceso_estudiante(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    current_user: Usuario = Depends(get_current_user),
):
    """Verificar si un estudiante puede acceder a un examen."""
    if current_user.role != "estudiante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta función es solo para estudiantes",
        )

    return examen.verificar_acceso_estudiante(
        db=db, examen_id=examen_id, estudiante_id=current_user.user_id
    )


@router.get("/profesor/estadisticas")
def obtener_estadisticas_profesor(
    *, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    """Obtener estadísticas generales de exámenes del profesor."""
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estas estadísticas",
        )

    profesor_id = current_user.user_id
    return examen.get_estadisticas_profesor(db=db, profesor_id=profesor_id)


@router.get("/proximos")
def obtener_examenes_proximos(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    dias_adelante: int = Query(
        7, ge=1, le=30, description="Días hacia adelante para buscar"
    ),
):
    """Obtener exámenes próximos."""
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver esta información",
        )

    return examen.get_examenes_proximos(
        db=db, profesor_id=current_user.user_id, dias_adelante=dias_adelante
    )
