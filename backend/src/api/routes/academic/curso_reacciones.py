"""Rutas de API para reacciones - REFACTORIZADO."""

import logging

from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from src.api import deps
from src.models.users.usuario import Usuario
from src.services.academic.reaccion_service import reaccion_service


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cursos/reacciones")


@router.post("/comentarios/{comentario_id}")
async def agregar_reaccion(
    comentario_id: str,
    tipo_reaccion: str = Form(...),
    emoji: str = Form(None),
    action: str = Form(None),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    logger.info(f"📨 POST /cursos/reacciones/comentarios/{comentario_id} - tipo={tipo_reaccion} emoji={emoji} action={action} user={current_user.usuario_id}")
    return reaccion_service.agregar_reaccion(
        db=db,
        comentario_id=comentario_id,
        tipo_reaccion=tipo_reaccion,
        usuario=current_user,
        emoji=emoji,
        action=action,
    )


@router.delete("/comentarios/{comentario_id}")
async def eliminar_reaccion(
    comentario_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    logger.info(f"🗑️ DELETE /cursos/reacciones/comentarios/{comentario_id} - user={current_user.usuario_id}")
    return reaccion_service.eliminar_reaccion(
        db=db, comentario_id=comentario_id, usuario=current_user
    )


@router.delete("/comentarios/reaccion/{reaccion_id}")
async def eliminar_reaccion_por_id(
    reaccion_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Elimina una reacción específica por su ID (solo la fila indicada)."""
    logger.info(f"🗑️ DELETE /cursos/reacciones/comentarios/reaccion/{reaccion_id} - user={current_user.usuario_id}")
    return reaccion_service.eliminar_reaccion_por_id(db=db, reaccion_id=reaccion_id, usuario=current_user)


@router.get("/comentarios/{comentario_id}")
async def obtener_reacciones(
    comentario_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Obtiene las reacciones de un comentario."""
    return reaccion_service.obtener_reacciones(
        db=db, comentario_id=comentario_id, usuario=current_user
    )


@router.get("/comentarios/{comentario_id}")
async def obtener_reacciones(
    comentario_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    return reaccion_service.obtener_reacciones(
        db=db, comentario_id=comentario_id, usuario=current_user
    )
