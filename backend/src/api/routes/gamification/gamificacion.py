from fastapi import APIRouter

from .insignias import router as insignias_router
from .misiones import router as misiones_router
from .puntos import router as puntos_router
from .rachas_routes import router as rachas_router
from .recompensas import router as recompensas_router

# Importar sub-routers del módulo de gamificación
from .temas import router as temas_router


# Router principal de gamificación
router = APIRouter()

# Incluir sub-routers con sus prefijos
router.include_router(temas_router, prefix="/temas", tags=["Temas"])
router.include_router(puntos_router, prefix="/puntos", tags=["Puntos"])
router.include_router(insignias_router, prefix="/insignias", tags=["Insignias"])
router.include_router(recompensas_router, prefix="/recompensas", tags=["Recompensas"])
router.include_router(misiones_router, prefix="/misiones", tags=["Misiones"])
router.include_router(rachas_router, tags=["Rachas"])  # Incluir router de rachas
