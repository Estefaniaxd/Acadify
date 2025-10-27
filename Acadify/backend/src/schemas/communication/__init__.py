# src/schemas/communication/__init__.py

from .comentario import (
    ComentarioCreate,
    ComentarioUpdate,
    ComentarioResponse,
    ComentarioDetallado,
    ComentariosList,
    ComentariosResumen,
    ComentariosFiltros,
    ComentarioEstadisticas,
    ComentariosBulkDelete,
    ComentariosBulkUpdate,
)

__all__ = [
    "ComentarioCreate",
    "ComentarioUpdate",
    "ComentarioResponse", 
    "ComentarioDetallado",
    "ComentariosList",
    "ComentariosResumen",
    "ComentariosFiltros",
    "ComentarioEstadisticas",
    "ComentariosBulkDelete",
    "ComentariosBulkUpdate",
]
