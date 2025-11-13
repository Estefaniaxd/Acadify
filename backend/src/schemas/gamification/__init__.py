"""
Schemas de validación para el sistema de gamificación.

Este módulo contiene todos los modelos Pydantic para:
- Puntos y niveles
- Etiquetas (badges)
- Tienda e inventario
- Rachas (streaks)

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
Version: 1.0.0
"""

# =============================================================================
# COMMON SCHEMAS
# =============================================================================
from .common import (
    PaginationParams,
    BaseResponse,
    ErrorResponse,
    SuccessMessageResponse
)

# =============================================================================
# PUNTOS SCHEMAS
# =============================================================================
from .puntos_schemas import (
    NivelInfo,
    InsigniaBasica,
    HistorialPuntoItem,
    PuntosCompletoResponse,
    RankingUsuarioItem,
    RankingResponse,
    PosicionRankingResponse,
    OtorgarPuntosRequest,
    OtorgarPuntosResponse
)

# =============================================================================
# ETIQUETAS SCHEMAS
# =============================================================================
from .etiquetas_schemas import (
    CategoriaEtiqueta,
    RarezaEtiqueta,
    EtiquetaBase,
    EtiquetaCatalogo,
    CatalogoEtiquetasResponse,
    CompraEtiquetaResponse,
    UsuarioEtiquetaDetalle,
    MisEtiquetasResponse,
    EquiparEtiquetasRequest,
    EtiquetaEquipadaInfo,
    EquiparEtiquetasResponse,
    EvolucionDisponibleResponse,
    EvolucionResponse,
    EstadisticasEtiquetasResponse
)

# =============================================================================
# TIENDA SCHEMAS
# =============================================================================
from .tienda_schemas import (
    CategoriaItem,
    RarezaItem,
    TipoItem,
    TiendaItemBase,
    TiendaItemCatalogo,
    CatalogoTiendaResponse,
    CompraRequest,
    CompraResponse,
    InventarioItem,
    InventarioResponse,
    EquiparItemResponse,
    UsarItemResponse,
    TransaccionHistorial,
    HistorialTransaccionesResponse,
    EstadisticasTiendaResponse
)

# =============================================================================
# RACHAS SCHEMAS
# =============================================================================
from .rachas_schemas import (
    TipoRacha,
    EstadoRacha,
    RachaActual,
    ObtenerRachaResponse,
    VerificarRachaRequest,
    VerificarRachaResponse,
    CongelarRachaRequest,
    CongelarRachaResponse,
    RecuperarRachaResponse,
    MilestoneRacha,
    MilestonesResponse,
    HistorialRachaItem,
    HistorialRachaResponse,
    EstadisticasRachaResponse,
    RankingRachaItem,
    RankingRachasResponse
)

# =============================================================================
# EXPORTS
# =============================================================================
__all__ = [
    # Common
    "PaginationParams",
    "BaseResponse",
    "ErrorResponse",
    "SuccessMessageResponse",
    # Puntos
    "NivelInfo",
    "InsigniaBasica",
    "HistorialPuntoItem",
    "PuntosCompletoResponse",
    "RankingUsuarioItem",
    "RankingResponse",
    "PosicionRankingResponse",
    "OtorgarPuntosRequest",
    "OtorgarPuntosResponse",
    # Etiquetas
    "CategoriaEtiqueta",
    "RarezaEtiqueta",
    "EtiquetaBase",
    "EtiquetaCatalogo",
    "CatalogoEtiquetasResponse",
    "CompraEtiquetaResponse",
    "UsuarioEtiquetaDetalle",
    "MisEtiquetasResponse",
    "EquiparEtiquetasRequest",
    "EtiquetaEquipadaInfo",
    "EquiparEtiquetasResponse",
    "EvolucionDisponibleResponse",
    "EvolucionResponse",
    "EstadisticasEtiquetasResponse",
    # Tienda
    "CategoriaItem",
    "RarezaItem",
    "TipoItem",
    "TiendaItemBase",
    "TiendaItemCatalogo",
    "CatalogoTiendaResponse",
    "CompraRequest",
    "CompraResponse",
    "InventarioItem",
    "InventarioResponse",
    "EquiparItemResponse",
    "UsarItemResponse",
    "TransaccionHistorial",
    "HistorialTransaccionesResponse",
    "EstadisticasTiendaResponse",
    # Rachas
    "TipoRacha",
    "EstadoRacha",
    "RachaActual",
    "ObtenerRachaResponse",
    "VerificarRachaRequest",
    "VerificarRachaResponse",
    "CongelarRachaRequest",
    "CongelarRachaResponse",
    "RecuperarRachaResponse",
    "MilestoneRacha",
    "MilestonesResponse",
    "HistorialRachaItem",
    "HistorialRachaResponse",
    "EstadisticasRachaResponse",
    "RankingRachaItem",
    "RankingRachasResponse",
]

# Common schemas
from .common import (
    PaginationParams,
    BaseResponse,
    ErrorResponse,
    SuccessMessageResponse
)

# Puntos schemas
from .puntos_schemas import (
    NivelInfo,
    InsigniaBasica,
    HistorialPuntoItem,
    PuntosCompletoResponse,
    RankingUsuarioItem,
    RankingResponse,
    PosicionRankingResponse,
    OtorgarPuntosRequest,
    OtorgarPuntosResponse
)

# Se importarán conforme se vayan creando
# from .etiquetas_schemas import *
# from .tienda_schemas import *
# from .rachas_schemas import *

__all__ = [
    # Common
    "PaginationParams",
    "BaseResponse",
    "ErrorResponse",
    "SuccessMessageResponse",
    # Puntos
    "NivelInfo",
    "InsigniaBasica",
    "HistorialPuntoItem",
    "PuntosCompletoResponse",
    "RankingUsuarioItem",
    "RankingResponse",
    "PosicionRankingResponse",
    "OtorgarPuntosRequest",
    "OtorgarPuntosResponse",
]
