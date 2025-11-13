"""
Módulo de enums para el sistema de gamificación.

Exporta todos los enums relacionados con:
- Insignias
- Recompensas
- Tienda virtual
- Etiquetas de perfil
- Rachas

Author: GitHub Copilot & Team
Date: 31 de octubre de 2025
"""

from .insignia_enums import TipoInsignia
from .recompensa_enums import TipoRecompensa
from .tienda_enums import CategoriaItem, RarezaItem, MetodoAdquisicion
from .etiqueta_enums import (
    CategoriaEtiqueta,
    RarezaEtiqueta,
    TipoRequisito,
)
from .racha_enums import (
    TipoEventoRacha,
    TipoMilestone,
    TipoActividadRacha,
)

__all__ = [
    # Insignias
    "TipoInsignia",
    # Recompensas
    "TipoRecompensa",
    # Tienda
    "CategoriaItem",
    "RarezaItem",
    "MetodoAdquisicion",
    # Etiquetas
    "CategoriaEtiqueta",
    "RarezaEtiqueta",
    "TipoRequisito",
    # Rachas
    "TipoEventoRacha",
    "TipoMilestone",
    "TipoActividadRacha",
]
