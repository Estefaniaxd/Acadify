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

# Add more schema imports as needed
__all__ = [
    "EscalaCalificacion",
    "EscalaCalificacionCreate", 
    "EscalaCalificacionUpdate",
    "ValorCalificacion",
    "ValorCalificacionCreate",
    "ValorCalificacionUpdate",
]