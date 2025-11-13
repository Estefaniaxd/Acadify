"""
Rutas de API para tareas de cursos - REFACTORIZADO

Thin controllers usando tarea_service
SOLID + Clean Code: Delegación completa a service layer
"""

from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from src.api import deps
from src.models.users.usuario import Usuario
from src.services.academic.tarea_service import tarea_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cursos/tareas")


@router.get("/{curso_id}/tareas")
async def obtener_tareas_curso(
    curso_id: str,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    logger.info(f"GET tareas curso {curso_id} - Usuario: {current_user.usuario_id}")
    return tarea_service.obtener_tareas_curso(
        db=db, curso_id=curso_id, usuario=current_user,
        limit=limit, offset=offset
    )


@router.post("/{curso_id}/tareas")
async def crear_tarea(
    curso_id: str,
    titulo: str = Body(...),
    descripcion: str = Body(...),
    fecha_limite: datetime = Body(...),
    puntos_max: int = Body(100),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    logger.info(f"POST tarea curso {curso_id} - Usuario: {current_user.usuario_id}")
    return tarea_service.crear_tarea(
        db=db, curso_id=curso_id, titulo=titulo,
        descripcion=descripcion, fecha_limite=fecha_limite,
        puntos_max=puntos_max, usuario=current_user
    )


@router.post("/tareas/{tarea_id}/entregar")
async def entregar_tarea(
    tarea_id: str,
    contenido: str = Body(...),
    archivos: Optional[str] = Body(None),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    logger.info(f"POST entregar tarea {tarea_id} - Usuario: {current_user.usuario_id}")
    return tarea_service.entregar_tarea(
        db=db, tarea_id=tarea_id, contenido=contenido,
        usuario=current_user, archivos_json=archivos
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
