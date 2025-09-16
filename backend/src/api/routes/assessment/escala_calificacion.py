# src/api/api_v1/endpoints/escala_calificacion.py
from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src import crud, schemas
from src.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.EscalaCalificacion])
def read_escalas_calificacion(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Obtener todas las escalas de calificación."""
    escalas = crud.escala_calificacion.get_multi(db, skip=skip, limit=limit)
    return escalas


@router.get(
    "/institucion/{institucion_id}", response_model=List[schemas.EscalaCalificacion]
)
def read_escalas_by_institucion(
    *,
    db: Session = Depends(deps.get_db),
    institucion_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Obtener escalas de calificación por institución."""
    escalas = crud.escala_calificacion.get_by_institucion(
        db, institucion_id=institucion_id, skip=skip, limit=limit
    )
    return escalas


@router.get(
    "/institucion/{institucion_id}/tipo/{tipo}",
    response_model=List[schemas.EscalaCalificacion],
)
def read_escalas_by_tipo_and_institucion(
    *,
    db: Session = Depends(deps.get_db),
    institucion_id: UUID,
    tipo: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Obtener escalas de calificación por tipo e institución."""
    escalas = crud.escala_calificacion.get_by_tipo_and_institucion(
        db, tipo=tipo, institucion_id=institucion_id, skip=skip, limit=limit
    )
    return escalas


@router.post("/", response_model=schemas.EscalaCalificacion)
def create_escala_calificacion(
    *,
    db: Session = Depends(deps.get_db),
    escala_in: schemas.EscalaCalificacionCreate,
) -> Any:
    """Crear nueva escala de calificación."""
    # Verificar si ya existe una escala con el mismo nombre en la institución
    escala = crud.escala_calificacion.get_by_nombre_and_institucion(
        db, nombre=escala_in.nombre, institucion_id=escala_in.institucion_id
    )
    if escala:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una escala de calificación con este nombre en la institución.",
        )

    escala = crud.escala_calificacion.create(db, obj_in=escala_in)
    return escala


@router.put("/{escala_id}", response_model=schemas.EscalaCalificacion)
def update_escala_calificacion(
    *,
    db: Session = Depends(deps.get_db),
    escala_id: UUID,
    escala_in: schemas.EscalaCalificacionUpdate,
) -> Any:
    """Actualizar escala de calificación."""
    escala = crud.escala_calificacion.get(db, id=escala_id)
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala de calificación no encontrada.",
        )

    escala = crud.escala_calificacion.update(db, db_obj=escala, obj_in=escala_in)
    return escala


@router.get("/{escala_id}", response_model=schemas.EscalaCalificacion)
def read_escala_calificacion(
    *,
    db: Session = Depends(deps.get_db),
    escala_id: UUID,
) -> Any:
    """Obtener escala de calificación por ID."""
    escala = crud.escala_calificacion.get(db, id=escala_id)
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala de calificación no encontrada.",
        )
    return escala


@router.delete("/{escala_id}", response_model=schemas.EscalaCalificacion)
def delete_escala_calificacion(
    *,
    db: Session = Depends(deps.get_db),
    escala_id: UUID,
) -> Any:
    """Eliminar escala de calificación."""
    escala = crud.escala_calificacion.get(db, id=escala_id)
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala de calificación no encontrada.",
        )

    escala = crud.escala_calificacion.remove(db, id=escala_id)
    return escala
