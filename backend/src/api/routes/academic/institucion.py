from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.db.session import get_db
from src.schemas.academic.institucion import Institucion, InstitucionCreate, InstitucionUpdate
from src.crud.academic.crud_institucion import institucion_crud

router = APIRouter()

@router.get("/", response_model=list[Institucion])
def get_all(db: Session = Depends(get_db)):
    return institucion_crud.get_multi(db)

@router.get("/{institucion_id}", response_model=Institucion)
def get_one(institucion_id: UUID, db: Session = Depends(get_db)):
    obj = institucion_crud.get(db, institucion_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return obj

@router.post("/", response_model=Institucion)
def create(obj_in: InstitucionCreate, db: Session = Depends(get_db)):
    return institucion_crud.create(db, obj_in)

@router.put("/{institucion_id}", response_model=Institucion)
def update(institucion_id: UUID, obj_in: InstitucionUpdate, db: Session = Depends(get_db)):
    db_obj = institucion_crud.get(db, institucion_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return institucion_crud.update(db, db_obj, obj_in)

@router.delete("/{institucion_id}", response_model=Institucion)
def delete(institucion_id: UUID, db: Session = Depends(get_db)):
    obj = institucion_crud.remove(db, institucion_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return obj
