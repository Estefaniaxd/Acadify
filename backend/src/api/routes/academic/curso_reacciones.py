"""
Rutas de API para reacciones - REFACTORIZADO
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging
from src.api import deps
from src.models.users.usuario import Usuario
from src.services.academic.reaccion_service import reaccion_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cursos/reacciones")

@router.post("/comentarios/{comentario_id}")
async def agregar_reaccion(comentario_id: str, tipo_reaccion: str, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return reaccion_service.agregar_reaccion(db=db, comentario_id=comentario_id, tipo_reaccion=tipo_reaccion, usuario=current_user)

@router.delete("/comentarios/{comentario_id}")
async def eliminar_reaccion(comentario_id: str, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return reaccion_service.eliminar_reaccion(db=db, comentario_id=comentario_id, usuario=current_user)

@router.get("/comentarios/{comentario_id}")
async def obtener_reacciones(comentario_id: str, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return reaccion_service.obtener_reacciones(db=db, comentario_id=comentario_id, usuario=current_user)
