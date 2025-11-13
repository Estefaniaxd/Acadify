"""API routes para el sistema de evaluaciones.

NOTA: Rutas legacy comentadas - en proceso de migración a Evaluacion
- examenes.py (usar /evaluaciones en su lugar)
- preguntas.py (usar /preguntas-evaluacion en su lugar)
- intentos.py (usar /intentos-evaluacion en su lugar)
"""

from fastapi import APIRouter

# from .examenes import router as examenes_router  # LEGACY - comentado
# from .preguntas import router as preguntas_router  # LEGACY - comentado
from .banco_preguntas import router as banco_preguntas_router
# from .proctoring import router as proctoring_router  # TODO: Fix imports before enabling


# from .intentos import router as intentos_router  # LEGACY - comentado

router = APIRouter()

# Incluir todos los routers de evaluaciones
# router.include_router(examenes_router, prefix="/examenes", tags=["examenes"])  # LEGACY
# router.include_router(preguntas_router, prefix="/preguntas", tags=["preguntas"])  # LEGACY
router.include_router(
    banco_preguntas_router, prefix="/banco-preguntas", tags=["banco-preguntas"]
)
# router.include_router(
#     proctoring_router, prefix="/proctoring", tags=["Proctoring"]
# )
# router.include_router(intentos_router, prefix="/intentos", tags=["intentos"])  # LEGACY

__all__ = ["router"]
