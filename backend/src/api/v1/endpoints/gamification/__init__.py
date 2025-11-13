"""
Routers de gamificación.

Exporta los routers de:
- Tienda virtual
- Etiquetas de perfil  
- Rachas
"""

from src.api.v1.endpoints.gamification.tienda import router as tienda_router
from src.api.v1.endpoints.gamification.etiquetas import router as etiquetas_router
from src.api.v1.endpoints.gamification.rachas import router as rachas_router

__all__ = [
    "tienda_router",
    "etiquetas_router",
    "rachas_router",
]
