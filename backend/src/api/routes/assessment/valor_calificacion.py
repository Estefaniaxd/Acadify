# src/api/api_v1/endpoints/valor_calificacion.py
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_db
import src.crud.assessment.escala_calificacion as crud_escala_calificacion
import src.crud.assessment.valor_calificacion as crud_valor_calificacion
from src.schemas.assessment.valor_calificacion import (
    ValorCalificacion,
    ValorCalificacionCreate,
    ValorCalificacionUpdate,
)


router = APIRouter()


@router.get("/", response_model=list[ValorCalificacion])
def read_valores_calificacion(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Obtener todos los valores de calificación."""
    return crud_valor_calificacion.get_multi(db, skip=skip, limit=limit)


@router.get("/escala/{escala_id}", response_model=list[ValorCalificacion])
def read_valores_by_escala(
    *,
    db: Session = Depends(get_db),
    escala_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Obtener valores de calificación por escala (ordenados por orden)."""
    # Verificar que la escala existe
    escala = crud_escala_calificacion.get(db, id=escala_id)
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala de calificación no encontrada.",
        )

    return crud_valor_calificacion.get_by_escala(
        db, escala_id=escala_id, skip=skip, limit=limit
    )


@router.post("/", response_model=ValorCalificacion)
def create_valor_calificacion(
    *,
    db: Session = Depends(get_db),
    valor_in: ValorCalificacionCreate,
) -> Any:
    """Crear nuevo valor de calificación."""
    # Verificar que la escala existe
    escala = crud_escala_calificacion.get(db, id=valor_in.escala_id)
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala de calificación no encontrada.",
        )

    # Verificar si ya existe un valor con el mismo valor en la escala
    valor_existente = crud_valor_calificacion.get_by_valor_and_escala(
        db, valor=valor_in.valor, escala_id=valor_in.escala_id
    )
    if valor_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un valor con este nombre en la escala de calificación.",
        )

    # Verificar si ya existe un valor con el mismo orden en la escala (si se proporciona)
    if valor_in.orden is not None:
        orden_existente = crud_valor_calificacion.get_by_orden_and_escala(
            db, orden=valor_in.orden, escala_id=valor_in.escala_id
        )
        if orden_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un valor con este orden en la escala de calificación.",
            )
    else:
        # Si no se proporciona orden, asignar el siguiente disponible
        max_orden = crud_valor_calificacion.get_max_orden_by_escala(
            db, escala_id=valor_in.escala_id
        )
        valor_in.orden = max_orden + 1

    return crud_valor_calificacion.create(db, obj_in=valor_in)


@router.put("/{valor_id}", response_model=ValorCalificacion)
def update_valor_calificacion(
    *,
    db: Session = Depends(get_db),
    valor_id: UUID,
    valor_in: ValorCalificacionUpdate,
) -> Any:
    """Actualizar valor de calificación."""
    valor = crud_valor_calificacion.get(db, id=valor_id)
    if not valor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Valor de calificación no encontrado.",
        )

    # Si se está actualizando el valor, verificar que no exista otro con el mismo valor en la escala
    if hasattr(valor_in, "valor") and valor_in.valor and valor_in.valor != valor.valor:
        valor_existente = crud_valor_calificacion.get_by_valor_and_escala(
            db, valor=valor_in.valor, escala_id=valor.escala_id
        )
        if valor_existente and valor_existente.valor_id != valor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un valor con este nombre en la escala de calificación.",
            )

    # Si se está actualizando el orden, verificar que no exista otro con el mismo orden en la escala
    if (
        hasattr(valor_in, "orden")
        and valor_in.orden is not None
        and valor_in.orden != valor.orden
    ):
        orden_existente = crud_valor_calificacion.get_by_orden_and_escala(
            db, orden=valor_in.orden, escala_id=valor.escala_id
        )
        if orden_existente and orden_existente.valor_id != valor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un valor con este orden en la escala de calificación.",
            )

    return crud_valor_calificacion.update(db, db_obj=valor, obj_in=valor_in)


@router.get("/{valor_id}", response_model=ValorCalificacion)
def read_valor_calificacion(
    *,
    db: Session = Depends(get_db),
    valor_id: UUID,
) -> Any:
    """Obtener valor de calificación por ID."""
    valor = crud_valor_calificacion.get(db, id=valor_id)
    if not valor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Valor de calificación no encontrado.",
        )
    return valor


@router.delete("/{valor_id}", response_model=ValorCalificacion)
def delete_valor_calificacion(
    *,
    db: Session = Depends(get_db),
    valor_id: UUID,
) -> Any:
    """Eliminar valor de calificación."""
    valor = crud_valor_calificacion.get(db, id=valor_id)
    if not valor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Valor de calificación no encontrado.",
        )

    return crud_valor_calificacion.remove(db, id=valor_id)
