from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.api.deps import get_db
from src.schemas.academic.programa import Programa, ProgramaCreate, ProgramaUpdate
import src.crud.academic.crud_programa as crud_programa_crud

router = APIRouter()

@router.get("/", response_model=list[Programa])
def get_all(db: Session = Depends(get_db)):
    return programa_crud.get_multi(db)

@router.get("/{programa_id}", response_model=Programa)
def get_one(programa_id: UUID, db: Session = Depends(get_db)):
    obj = programa_crud.get(db, programa_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    return obj

@router.post("/", response_model=Programa)
def create(obj_in: ProgramaCreate, db: Session = Depends(get_db)):
    return programa_crud.create(db, obj_in)

@router.put("/{programa_id}", response_model=Programa)
def update(programa_id: UUID, obj_in: ProgramaUpdate, db: Session = Depends(get_db)):
    db_obj = programa_crud.get(db, programa_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    return programa_crud.update(db, db_obj, obj_in)

@router.delete("/{programa_id}", response_model=Programa)
def delete(programa_id: UUID, db: Session = Depends(get_db)):
    obj = programa_crud.remove(db, programa_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    return obj
