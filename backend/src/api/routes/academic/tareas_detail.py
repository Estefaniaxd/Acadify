"""
Rutas específicas para detalles de tareas - SOLO lectura
Propósito: Servir endpoint GET /api/tareas/{tarea_id} para el frontend
No modifica el router principal de tareas.py
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.dependencies import get_current_user
from src.crud.academic.tarea import crud_tarea
from src.models.users.usuario import Usuario
from src.schemas.academic.tarea_schemas import TareaDetallada

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{tarea_id}", response_model=TareaDetallada)
def obtener_tarea_detalle(
    *,
    db: Session = Depends(get_db),
    tarea_id: str,
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener una tarea específica con detalles completos.
    
    Endpoint: GET /api/tareas/{tarea_id}
    Usado por frontend para cargar detalles de tarea en página de entrega.
    """
    try:
        tarea = crud_tarea.obtener_tarea_detallada(db=db, tarea_id=tarea_id)
        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
            )
        return tarea
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener tarea {tarea_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tarea: {str(e)}"
        )
