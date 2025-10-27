"""
API routes para el sistema de evaluaciones
"""

from fastapi import APIRouter

from .examenes import router as examenes_router
from .preguntas import router as preguntas_router
from .banco_preguntas import router as banco_preguntas_router
from .intentos import router as intentos_router

router = APIRouter()

# Incluir todos los routers de evaluaciones
router.include_router(examenes_router, prefix="/examenes", tags=["examenes"])
router.include_router(preguntas_router, prefix="/preguntas", tags=["preguntas"])
router.include_router(banco_preguntas_router, prefix="/banco-preguntas", tags=["banco-preguntas"])
router.include_router(intentos_router, prefix="/intentos", tags=["intentos"])

__all__ = ["router"]