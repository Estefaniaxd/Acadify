# Schemas exports
from .assessment.escala_calificacion import (
    EscalaCalificacion,
    EscalaCalificacionCreate,
    EscalaCalificacionUpdate,
)
from .assessment.valor_calificacion import (
    ValorCalificacion,
    ValorCalificacionCreate,
    ValorCalificacionUpdate,
)

# Communication schemas
from .communication.comentario import (
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

# Add more schema imports as needed
__all__ = [
    "EscalaCalificacion",
    "EscalaCalificacionCreate", 
    "EscalaCalificacionUpdate",
    "ValorCalificacion",
    "ValorCalificacionCreate",
    "ValorCalificacionUpdate",
    # Communication
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