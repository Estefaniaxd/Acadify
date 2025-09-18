from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.classes.plataforma import (
    PlataformaCreate,
    PlataformaUpdate,
    PlataformaRead,
)
from src.crud.classes.plataforma import crud_plataforma

router = APIRouter()
PLATAFORM_NOT_FOUND = "Plataforma no encontrada"


@router.post("/", response_model=PlataformaRead)
def create_plataforma(plataforma_in: PlataformaCreate, db: Session = Depends(get_db)):
    """Crear una nueva plataforma"""
    return crud_plataforma.create(db, obj_in=plataforma_in)


@router.get("/{plataforma_id}", response_model=PlataformaRead)
def get_plataforma(plataforma_id: UUID, db: Session = Depends(get_db)):
    """Obtener una plataforma por ID"""
    plataforma = crud_plataforma.get(db, plataforma_id=plataforma_id)
    if not plataforma:
        raise HTTPException(status_code=404, detail=PLATAFORM_NOT_FOUND)
    return plataforma


@router.get("/", response_model=List[PlataformaRead])
def get_plataformas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener todas las plataformas con paginación"""
    return crud_plataforma.get_multi(db, skip=skip, limit=limit)


@router.get("/nombre/{nombre}", response_model=PlataformaRead)
def get_plataforma_by_nombre(nombre: str, db: Session = Depends(get_db)):
    """Obtener plataforma por nombre"""
    plataforma = crud_plataforma.get_by_nombre(db, nombre=nombre)
    if not plataforma:
        raise HTTPException(status_code=404, detail="Plataforma no encontrada")
    return plataforma


@router.put("/{plataforma_id}", response_model=PlataformaRead)
def update_plataforma(
    plataforma_id: UUID, plataforma_in: PlataformaUpdate, db: Session = Depends(get_db)
):
    """Actualizar una plataforma"""
    db_obj = crud_plataforma.get(db, plataforma_id=plataforma_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Plataforma no encontrada")
    return crud_plataforma.update(db, db_obj=db_obj, obj_in=plataforma_in)


@router.delete("/{plataforma_id}", response_model=PlataformaRead)
def delete_plataforma(plataforma_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una plataforma"""
    obj = crud_plataforma.remove(db, plataforma_id=plataforma_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Plataforma no encontrada")
    return obj
