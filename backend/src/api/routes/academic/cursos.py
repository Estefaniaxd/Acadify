"""
Rutas de API para gestión básica de cursos - REFACTORIZADO

Thin controllers usando curso_service
SOLID + Clean Code: Rutas simples delegando lógica a services
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from src.api import deps
from src.models.users.usuario import Usuario
from src.services.academic.curso_service import curso_service

# Configuración
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cursos")


# ==================== ENDPOINTS CURSOS ====================

@router.get("/mis-cursos")
async def get_mis_cursos(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Obtiene cursos del usuario según su rol:
    - Estudiante: cursos inscritos
    - Docente: cursos que imparte
    - Coordinador: todos los cursos
    """
    logger.info(f"GET mis-cursos - Usuario: {current_user.usuario_id} ({current_user.rol})")
    return curso_service.obtener_cursos_usuario(
        db=db,
        usuario=current_user,
        limit=limit,
        offset=offset
    )


@router.get("/disponibles")
async def get_cursos_disponibles(
    institucion_id: Optional[str] = None,
    area: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Obtiene cursos disponibles para inscripción"""
    logger.info(f"GET cursos disponibles - Usuario: {current_user.usuario_id}")
    return curso_service.obtener_cursos_disponibles(
        db=db,
        usuario=current_user,
        institucion_id=institucion_id,
        area=area,
        limit=limit,
        offset=offset
    )


@router.get("/{curso_id}")
async def get_curso_detalle(
    curso_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Obtiene detalles completos de un curso"""
    logger.info(f"GET curso {curso_id} - Usuario: {current_user.usuario_id}")
    return curso_service.obtener_detalle_curso(
        db=db,
        curso_id=curso_id,
        usuario=current_user
    )
