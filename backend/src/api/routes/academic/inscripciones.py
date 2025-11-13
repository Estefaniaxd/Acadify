"""Rutas de API para inscripciones y códigos - REFACTORIZADO.

Thin controllers usando inscripcion_service
SOLID + Clean Code: Delegación completa a services
"""

import logging

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from src.api import deps
from src.models.users.usuario import Usuario
from src.services.academic.inscripcion_service import inscripcion_service


# Configuración
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cursos/inscripciones")


# ==================== ENDPOINTS INSCRIPCIONES ====================


@router.post("/inscribir")
async def inscribir_curso(
    codigo_acceso: str = Body(..., embed=True),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> dict:
    """Inscribe estudiante a un curso usando código de acceso."""
    logger.info(
        "POST inscribir - Usuario: %s, código: %s",
        current_user.usuario_id,
        codigo_acceso,
    )
    return inscripcion_service.inscribir_por_codigo(
        db=db, codigo_acceso=codigo_acceso, usuario=current_user
    )


@router.post("/auto-vincular-estudiante")
async def auto_vincular_estudiante(
    codigo_invitacion: str = Body(..., embed=True),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> dict:
    """Vincula estudiante a institución usando código de invitación."""
    logger.info("POST auto-vincular - Usuario: %s", current_user.usuario_id)
    return inscripcion_service.vincular_por_codigo_invitacion(
        db=db, codigo_invitacion=codigo_invitacion, usuario=current_user
    )


@router.post("/confirmar-programa")
async def confirmar_programa(
    programa_id: str = Body(...),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> dict:
    """Confirma programa del estudiante."""
    logger.info(
        "POST confirmar-programa - Usuario: %s, programa: %s",
        current_user.usuario_id,
        programa_id,
    )
    return inscripcion_service.confirmar_programa_estudiante(
        db=db, programa_id=programa_id, usuario=current_user
    )


@router.post("/vincular-por-codigo")
async def vincular_por_codigo(
    codigo_vinculacion: str = Body(...),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> dict:
    """Vincula usuario por código general (alias de auto-vincular)."""
    logger.info("POST vincular-por-codigo - Usuario: %s", current_user.usuario_id)
    return inscripcion_service.vincular_por_codigo_invitacion(
        db=db, codigo_invitacion=codigo_vinculacion, usuario=current_user
    )


@router.post("/generar-codigo-invitacion")
async def generar_codigo_invitacion(
    programa_id: str | None = Body(None),
    descripcion: str | None = Body(None),
    dias_validez: int = Body(30),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> dict:
    """Genera código de invitación (solo coordinadores)."""
    logger.info("POST generar-codigo - Usuario: %s", current_user.usuario_id)
    return inscripcion_service.generar_codigo_invitacion(
        db=db, programa_id=programa_id, usuario=current_user, descripcion=descripcion, dias_validez=dias_validez
    )


@router.get("/programas-disponibles")
async def obtener_programas_disponibles(
    institucion_id: str | None = None,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> dict:
    """Obtiene programas disponibles de la institución."""
    logger.info("GET programas-disponibles - Usuario: %s", current_user.usuario_id)
    return inscripcion_service.obtener_programas_disponibles(
        db=db, usuario=current_user, institucion_id=institucion_id
    )
