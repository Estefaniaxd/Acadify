from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from src.api import deps
from src.models.users.usuario import Usuario
from src.models.communication.comentario import TipoComentario
from src.services.academic import comentario_service, reaccion_service

router = APIRouter(prefix="/cursos", tags=["Comentarios"])

# Pydantic schemas
class ComentarioCreate(BaseModel):
    contenido: str
    tipo: str = 'comentario'  # anuncio, pregunta, comentario
    archivos: Optional[List[str]] = []

class ComentarioResponse(BaseModel):
    id: str
    contenido: str
    tipo: str
    autor: str
    fecha: str

@router.post("/{curso_id}/comentarios")
async def crear_comentario(
    curso_id: str,
    comentario: ComentarioCreate,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    # Convertir string a enum
    tipo_enum = TipoComentario.comentario
    if comentario.tipo == 'anuncio':
        tipo_enum = TipoComentario.anuncio
    elif comentario.tipo == 'pregunta':
        tipo_enum = TipoComentario.pregunta
    
    return comentario_service.crear_comentario(
        db=db,
        curso_id=curso_id,
        contenido=comentario.contenido,
        tipo=tipo_enum,
        usuario=current_user
    )

@router.get("/{curso_id}/comentarios")
async def obtener_comentarios(
    curso_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    return comentario_service.obtener_comentarios_curso(
        db=db, curso_id=curso_id, limit=limit, offset=offset, usuario=current_user
    )

@router.post("/comentarios/{comentario_id}/reacciones")
async def crear_reaccion(
    comentario_id: str,
    tipo: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    return reaccion_service.crear_reaccion(
        db=db, comentario_id=comentario_id, tipo=tipo, usuario=current_user
    )

@router.get("/comentarios/{comentario_id}/reacciones")
async def obtener_reacciones(
    comentario_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    return reaccion_service.obtener_reacciones(
        db=db, comentario_id=comentario_id, usuario=current_user
    )
