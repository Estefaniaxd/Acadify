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

from src.schemas.communication.videollamada_schemas import (
    # Videollamadas
    VideollamadaBase,
    VideollamadaCreate,
    VideollamadaUpdate,
    VideollamadaResponse,
    VideollamadaDetallada,
    VideollamadaInDB,
    VideollamadaFilter,
    VideollamadaListResponse,
    # Participantes
    ParticipanteBase,
    ParticipanteCreate,
    ParticipanteUpdate,
    ParticipanteResponse,
    UnirseVideollamadaResponse,
    # Grabaciones
    GrabacionBase,
    GrabacionCreate,
    GrabacionUpdate,
    GrabacionResponse,
    # Estadísticas y utilidades
    EstadisticasVideollamada,
    MessageResponse,
)

__all__ = [
    # Comentarios
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
    
    # Videollamadas
    "VideollamadaCreate",
    "VideollamadaUpdate",
    "VideollamadaResponse",
    "VideollamadaDetallada",
    "VideollamadaInDB",
    "VideollamadaFilter",
    "VideollamadaListResponse",
    
    # Participantes
    "ParticipanteCreate",
    "ParticipanteUpdate",
    "ParticipanteResponse",
    
    # Grabaciones
    "GrabacionCreate",
    "GrabacionUpdate",
    "GrabacionResponse",
    
    # Estadísticas
    "EstadisticasVideollamada",
    "MessageResponse",
]
