"""
Rutas de API para comentarios - REFACTORIZADO
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging
from src.api import deps
from src.models.users.usuario import Usuario
from src.services.academic.comentario_service import comentario_service
from src.services.academic.reaccion_service import reaccion_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cursos/comentarios")

@router.get("/{curso_id}/comentarios")
async def obtener_comentarios_curso(curso_id: str, limit: int = Query(20, le=100), offset: int = Query(0, ge=0), tipo: Optional[str] = None, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return comentario_service.obtener_comentarios_curso(db=db, curso_id=curso_id, usuario=current_user, limit=limit, offset=offset, tipo=tipo)

@router.post("/{curso_id}/comentarios")
async def crear_comentario(curso_id: str, contenido: str, tipo: str = "comentario", archivos: Optional[str] = None, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return comentario_service.crear_comentario(db=db, curso_id=curso_id, contenido=contenido, usuario=current_user, tipo=tipo, archivos_json=archivos)

@router.put("/comentarios/{comentario_id}")
async def editar_comentario(comentario_id: str, contenido: str, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return comentario_service.editar_comentario(db=db, comentario_id=comentario_id, contenido=contenido, usuario=current_user)

@router.delete("/comentarios/{comentario_id}")
async def eliminar_comentario(comentario_id: str, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return comentario_service.eliminar_comentario(db=db, comentario_id=comentario_id, usuario=current_user)

@router.post("/comentarios/{comentario_id}/respuestas")
async def crear_respuesta(comentario_id: str, contenido: str, archivos: Optional[str] = None, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return comentario_service.crear_respuesta(db=db, comentario_padre_id=comentario_id, contenido=contenido, usuario=current_user, archivos_json=archivos)

@router.get("/comentarios/{comentario_id}/respuestas")
async def obtener_respuestas(comentario_id: str, limit: int = Query(20, le=100), offset: int = Query(0, ge=0), current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return comentario_service.obtener_respuestas(db=db, comentario_padre_id=comentario_id, usuario=current_user, limit=limit, offset=offset)

@router.put("/respuestas/{respuesta_id}")
async def editar_respuesta(respuesta_id: str, contenido: str, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return comentario_service.editar_comentario(db=db, comentario_id=respuesta_id, contenido=contenido, usuario=current_user)

@router.delete("/respuestas/{respuesta_id}")
async def eliminar_respuesta(respuesta_id: str, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return comentario_service.eliminar_comentario(db=db, comentario_id=respuesta_id, usuario=current_user)

@router.post("/comentarios/{comentario_id}/reacciones")
async def agregar_reaccion(comentario_id: str, tipo_reaccion: str, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return reaccion_service.agregar_reaccion(db=db, comentario_id=comentario_id, tipo_reaccion=tipo_reaccion, usuario=current_user)

@router.delete("/comentarios/{comentario_id}/reacciones")
async def eliminar_reaccion(comentario_id: str, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return reaccion_service.eliminar_reaccion(db=db, comentario_id=comentario_id, usuario=current_user)

@router.get("/comentarios/{comentario_id}/reacciones")
async def obtener_reacciones(comentario_id: str, current_user: Usuario = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    return reaccion_service.obtener_reacciones(db=db, comentario_id=comentario_id, usuario=current_user)
