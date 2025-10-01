"""
API routes para gestión de intentos de examen
Incluye tomar exámenes, guardar respuestas y finalizar intentos
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, Request
from sqlalchemy.orm import Session
from datetime import datetime

from src.api.deps import get_current_user, get_db
from src.crud.evaluaciones import intento_examen, respuesta_estudiante, examen, pregunta_examen
from src.schemas.evaluaciones import (
    IntentoExamenResponse, RespuestaEstudianteCreate, RespuestaEstudianteResponse,
    ResultadoExamen, PreguntaParaEstudiante
)
from src.models.evaluaciones import EstadoIntento
from src.models.users.usuario import Usuario

router = APIRouter()


@router.post("/{examen_id}/iniciar", response_model=IntentoExamenResponse)
def iniciar_intento_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    contraseña: Optional[str] = Body(None, embed=True, description="Contraseña del examen si es requerida"),
    request: Request,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Iniciar un nuevo intento de examen.
    Solo estudiantes pueden iniciar intentos.
    """
    if current_user.role != "estudiante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden tomar exámenes"
        )
    
    # Verificar acceso al examen
    acceso_info = examen.verificar_acceso_estudiante(
        db=db, examen_id=examen_id, estudiante_id=current_user.user_id
    )
    
    if not acceso_info["puede_acceder"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=acceso_info["mensaje"]
        )
    
    # Verificar contraseña si es requerida
    if acceso_info.get("requiere_contraseña", False):
        exam = examen.get(db=db, id=examen_id)
        if not contraseña or contraseña != exam.contraseña_acceso:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña incorrecta"
            )
    
    # Obtener información de la request
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    
    try:
        # Crear o recuperar intento
        nuevo_intento = intento_examen.crear_intento(
            db=db,
            estudiante_id=current_user.user_id,
            examen_id=examen_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return nuevo_intento
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{intento_id}", response_model=IntentoExamenResponse)
def obtener_intento(
    *,
    db: Session = Depends(get_db),
    intento_id: str = Path(..., description="ID del intento"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener detalles de un intento específico.
    """
    intento = intento_examen.get(db=db, id=intento_id)
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado"
        )
    
    # Verificar permisos
    puede_ver = (
        current_user.role in ["coordinador", "administrador"] or
        intento.estudiante_id == current_user.user_id
    )
    
    # También permitir al profesor del examen ver el intento
    if not puede_ver and current_user.role == "docente":
        exam = examen.get(db=db, id=intento.examen_id)
        puede_ver = exam and exam.creado_por == current_user.user_id
    
    if not puede_ver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este intento"
        )
    
    return intento


@router.get("/{intento_id}/preguntas", response_model=List[PreguntaParaEstudiante])
def obtener_preguntas_intento(
    *,
    db: Session = Depends(get_db),
    intento_id: str = Path(..., description="ID del intento"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener preguntas del examen para un intento específico.
    Las preguntas se devuelven en el orden correspondiente al intento.
    """
    intento = intento_examen.get(db=db, id=intento_id)
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado"
        )
    
    # Verificar que el estudiante puede acceder a este intento
    if current_user.role == "estudiante" and intento.estudiante_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este intento"
        )
    
    # Obtener preguntas en el orden del intento
    preguntas_ordenadas = []
    if intento.orden_preguntas:
        for pregunta_id in intento.orden_preguntas:
            pregunta = pregunta_examen.get(db=db, id=pregunta_id)
            if pregunta:
                # Crear versión filtrada para estudiante
                pregunta_dict = {
                    "pregunta_id": pregunta.pregunta_id,
                    "titulo": pregunta.titulo,
                    "descripcion": pregunta.descripcion,
                    "tipo_pregunta": pregunta.tipo_pregunta,
                    "orden": len(preguntas_ordenadas) + 1,  # Orden relativo en el intento
                    "puntuacion": pregunta.puntuacion,
                    "es_obligatoria": pregunta.es_obligatoria,
                    "tiempo_limite_segundos": pregunta.tiempo_limite_segundos,
                    "opciones_respuesta": pregunta.opciones_respuesta,
                    "imagen_url": pregunta.imagen_url,
                    "audio_url": pregunta.audio_url,
                    "video_url": pregunta.video_url,
                    "archivos_adjuntos": pregunta.archivos_adjuntos
                }
                preguntas_ordenadas.append(pregunta_dict)
    
    return preguntas_ordenadas


@router.post("/{intento_id}/responder", response_model=RespuestaEstudianteResponse)
def guardar_respuesta(
    *,
    db: Session = Depends(get_db),
    intento_id: str = Path(..., description="ID del intento"),
    pregunta_id: str = Body(..., embed=True, description="ID de la pregunta"),
    respuesta_datos: Dict[str, Any] = Body(..., embed=True, description="Datos de la respuesta"),
    tiempo_empleado: Optional[int] = Body(None, embed=True, description="Tiempo empleado en segundos"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Guardar o actualizar una respuesta del estudiante.
    """
    intento = intento_examen.get(db=db, id=intento_id)
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado"
        )
    
    # Verificar que es el estudiante correcto y el intento está activo
    if (current_user.role != "estudiante" or 
        intento.estudiante_id != current_user.user_id or
        intento.estado != EstadoIntento.EN_PROGRESO):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes responder en este intento"
        )
    
    # Crear o actualizar respuesta
    respuesta = respuesta_estudiante.crear_o_actualizar_respuesta(
        db=db,
        intento_id=intento_id,
        pregunta_id=pregunta_id,
        respuesta_datos=respuesta_datos,
        tiempo_empleado=tiempo_empleado
    )
    
    if not respuesta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al guardar la respuesta"
        )
    
    return respuesta


@router.post("/{intento_id}/avanzar", response_model=IntentoExamenResponse)
def avanzar_pregunta(
    *,
    db: Session = Depends(get_db),
    intento_id: str = Path(..., description="ID del intento"),
    nueva_pregunta: Optional[int] = Body(None, embed=True, description="Número de pregunta específica"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Avanzar a la siguiente pregunta o a una pregunta específica.
    """
    intento = intento_examen.get(db=db, id=intento_id)
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado"
        )
    
    # Verificar permisos
    if (current_user.role != "estudiante" or 
        intento.estudiante_id != current_user.user_id or
        intento.estado != EstadoIntento.EN_PROGRESO):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes modificar este intento"
        )
    
    intento_actualizado = intento_examen.avanzar_pregunta(
        db=db, intento_id=intento_id, nueva_pregunta=nueva_pregunta
    )
    
    return intento_actualizado


@router.post("/{intento_id}/evento-sospechoso", response_model=Dict[str, str])
def registrar_evento_sospechoso(
    *,
    db: Session = Depends(get_db),
    intento_id: str = Path(..., description="ID del intento"),
    tipo_evento: str = Body(..., embed=True, description="Tipo de evento sospechoso"),
    detalles: Dict[str, Any] = Body(..., embed=True, description="Detalles del evento"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registrar un evento sospechoso durante el examen.
    """
    intento = intento_examen.get(db=db, id=intento_id)
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado"
        )
    
    # Verificar que es el estudiante correcto
    if (current_user.role != "estudiante" or 
        intento.estudiante_id != current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes registrar eventos en este intento"
        )
    
    intento_examen.registrar_evento_sospechoso(
        db=db, intento_id=intento_id, tipo_evento=tipo_evento, detalles=detalles
    )
    
    return {"mensaje": "Evento registrado"}


@router.post("/{intento_id}/finalizar", response_model=IntentoExamenResponse)
def finalizar_intento(
    *,
    db: Session = Depends(get_db),
    intento_id: str = Path(..., description="ID del intento"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Finalizar un intento de examen.
    """
    intento = intento_examen.get(db=db, id=intento_id)
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado"
        )
    
    # Verificar permisos
    puede_finalizar = (
        (current_user.role == "estudiante" and intento.estudiante_id == current_user.user_id) or
        current_user.role in ["coordinador", "administrador"]
    )
    
    # También permitir al profesor finalizar
    if not puede_finalizar and current_user.role == "docente":
        exam = examen.get(db=db, id=intento.examen_id)
        puede_finalizar = exam and exam.creado_por == current_user.user_id
    
    if not puede_finalizar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para finalizar este intento"
        )
    
    # Determinar motivo de finalización
    motivo = "estudiante"
    if current_user.role != "estudiante" or intento.estudiante_id != current_user.user_id:
        motivo = "profesor"
    
    intento_finalizado = intento_examen.finalizar_intento(
        db=db, intento_id=intento_id, motivo_finalizacion=motivo
    )
    
    return intento_finalizado


@router.get("/{intento_id}/resultado", response_model=ResultadoExamen)
def obtener_resultado_intento(
    *,
    db: Session = Depends(get_db),
    intento_id: str = Path(..., description="ID del intento"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener resultados detallados de un intento finalizado.
    """
    intento = intento_examen.get(db=db, id=intento_id)
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado"
        )
    
    # Verificar permisos
    puede_ver_resultado = (
        current_user.role in ["coordinador", "administrador"] or
        intento.estudiante_id == current_user.user_id
    )
    
    # También permitir al profesor ver resultados
    if not puede_ver_resultado and current_user.role == "docente":
        exam = examen.get(db=db, id=intento.examen_id)
        puede_ver_resultado = exam and exam.creado_por == current_user.user_id
    
    if not puede_ver_resultado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este resultado"
        )
    
    # Verificar que el intento esté finalizado
    if intento.estado == EstadoIntento.EN_PROGRESO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El intento aún no ha finalizado"
        )
    
    # Obtener respuestas del intento
    respuestas = respuesta_estudiante.get_respuestas_por_intento(
        db=db, intento_id=intento_id, incluir_pregunta=True
    )
    
    # Obtener configuración del examen para determinar qué mostrar
    exam = examen.get(db=db, id=intento.examen_id)
    
    # Determinar permisos de visualización
    puede_revisar = exam.permitir_revision if exam else False
    mostrar_respuestas_correctas = exam.mostrar_respuestas_correctas if exam else False
    
    # Si es estudiante, aplicar restricciones del examen
    if current_user.role == "estudiante":
        puede_revisar = puede_revisar and exam.permitir_revision
        mostrar_respuestas_correctas = mostrar_respuestas_correctas and exam.mostrar_respuestas_correctas
    
    # Obtener estadísticas del intento
    estadisticas_intento = intento_examen.get_estadisticas_intento(db=db, intento_id=intento_id)
    
    return {
        "intento": intento,
        "respuestas": respuestas,
        "estadisticas_intento": estadisticas_intento,
        "puede_revisar": puede_revisar,
        "mostrar_respuestas_correctas": mostrar_respuestas_correctas
    }


@router.get("/{intento_id}/estadisticas")
def obtener_estadisticas_intento(
    *,
    db: Session = Depends(get_db),
    intento_id: str = Path(..., description="ID del intento"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener estadísticas detalladas de un intento.
    """
    intento = intento_examen.get(db=db, id=intento_id)
    if not intento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado"
        )
    
    # Verificar permisos
    puede_ver_estadisticas = (
        current_user.role in ["coordinador", "administrador"] or
        intento.estudiante_id == current_user.user_id
    )
    
    # También permitir al profesor ver estadísticas
    if not puede_ver_estadisticas and current_user.role == "docente":
        exam = examen.get(db=db, id=intento.examen_id)
        puede_ver_estadisticas = exam and exam.creado_por == current_user.user_id
    
    if not puede_ver_estadisticas:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estas estadísticas"
        )
    
    estadisticas = intento_examen.get_estadisticas_intento(db=db, intento_id=intento_id)
    return estadisticas


@router.get("/estudiante/mis-intentos", response_model=List[IntentoExamenResponse])
def obtener_mis_intentos(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    examen_id: Optional[str] = Query(None, description="Filtrar por examen específico"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200)
):
    """
    Obtener todos los intentos de examen del estudiante actual.
    """
    if current_user.role != "estudiante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden ver sus intentos"
        )
    
    intentos = intento_examen.get_intentos_por_estudiante(
        db=db,
        estudiante_id=current_user.user_id,
        examen_id=examen_id,
        skip=skip,
        limit=limit
    )
    
    return intentos


@router.get("/examen/{examen_id}/intentos", response_model=List[IntentoExamenResponse])
def obtener_intentos_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    current_user: Usuario = Depends(get_current_user),
    estado: Optional[EstadoIntento] = Query(None, description="Filtrar por estado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200)
):
    """
    Obtener todos los intentos de un examen específico.
    Solo el profesor del examen, coordinadores y administradores pueden acceder.
    """
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Examen no encontrado"
        )
    
    # Verificar permisos
    puede_ver_intentos = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam.creado_por == current_user.user_id)
    )
    
    if not puede_ver_intentos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver los intentos de este examen"
        )
    
    intentos = intento_examen.get_intentos_por_examen(
        db=db, examen_id=examen_id, estado=estado, skip=skip, limit=limit
    )
    
    return intentos


@router.get("/examen/{examen_id}/ranking")
def obtener_ranking_examen(
    *,
    db: Session = Depends(get_db),
    examen_id: str = Path(..., description="ID del examen"),
    current_user: Usuario = Depends(get_current_user),
    limite: int = Query(10, ge=1, le=50, description="Número de posiciones del ranking")
):
    """
    Obtener ranking de mejores intentos de un examen.
    """
    exam = examen.get(db=db, id=examen_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Examen no encontrado"
        )
    
    # Verificar permisos
    puede_ver_ranking = (
        current_user.role in ["coordinador", "administrador"] or
        (current_user.role == "docente" and exam.creado_por == current_user.user_id)
    )
    
    if not puede_ver_ranking:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver el ranking de este examen"
        )
    
    ranking = intento_examen.get_ranking_intentos(
        db=db, examen_id=examen_id, limite=limite
    )
    
    return ranking


@router.get("/{estudiante_id}/recuperar/{examen_id}", response_model=Optional[IntentoExamenResponse])
def recuperar_intento_interrumpido(
    *,
    db: Session = Depends(get_db),
    estudiante_id: str = Path(..., description="ID del estudiante"),
    examen_id: str = Path(..., description="ID del examen"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Recuperar un intento interrumpido si es posible.
    """
    # Solo el propio estudiante puede recuperar su intento
    if current_user.role != "estudiante" or current_user.user_id != estudiante_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes recuperar intentos de otro estudiante"
        )
    
    intento_recuperado = intento_examen.recuperar_intento(
        db=db, estudiante_id=estudiante_id, examen_id=examen_id
    )
    
    return intento_recuperado