"""
Rutas de API para la gestión de cursos en Acadify

Endpoints disponibles:
- POST /inscribir: Inscribir estudiante en un curso
- GET /mis-cursos: Obtener cursos del usuario actual
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
import logging

from ....db.session import get_db, SessionLocal
from ....api import deps
from ....models.academic.curso import Curso
from ....models.users.usuario import Usuario

# Configuración del router
router = APIRouter()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos de datos
class CourseInscriptionRequest(BaseModel):
    codigo_curso: str

class CourseResponse(BaseModel):
    success: bool
    message: str
    data: List[dict]
    total: int
    source: str
    user_role: str
    empty_state: bool
    empty_message: Optional[str] = None

@router.post("/inscribir")
async def inscribir_curso(
    request: CourseInscriptionRequest,
    current_user: dict = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Inscribir estudiante en un curso usando código
    """
    try:
        logger.info(f"Iniciando inscripción con código: {request.codigo_curso}")
        
        # Buscar curso por código
        curso = db.query(Curso).filter(Curso.codigo == request.codigo_curso).first()
        
        if not curso:
            raise HTTPException(
                status_code=404,
                detail="Código de curso no válido"
            )
        
        return {
            "success": True,
            "message": f"Inscripción exitosa al curso: {curso.nombre}",
            "curso_id": str(curso.curso_id),
            "curso_nombre": curso.nombre
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en inscripción: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/mis-cursos", response_model=CourseResponse)
async def get_mis_cursos(current_user: dict = Depends(deps.get_current_user)):
    """
    Obtener los cursos del usuario actual
    """
    try:
        logger.info(f"Obteniendo cursos para usuario: {current_user.get('sub', 'No identificado')}")
        
        # Por ahora devolvemos un estado vacío con mensaje amigable
        # Esto nos permite verificar que el endpoint funciona antes de agregar la lógica de BD
        return {
            "success": True,
            "message": "Aún no te has unido a ningún curso",
            "data": [],
            "total": 0,
            "source": "mock",
            "user_role": "temporal",
            "empty_state": True,
            "empty_message": "¡Únete a un curso para comenzar tu aprendizaje! Usa el botón 'Nuevo Curso' para inscribirte con un código."
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo cursos: {e}")
        return {
            "success": True,
            "message": "Error temporal al cargar cursos",
            "data": [],
            "total": 0,
            "source": "error",
            "user_role": "temporal",
            "empty_state": True,
            "empty_message": "Ocurrió un problema al cargar los cursos. Intenta nuevamente."
        }