from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.api.deps import get_db
from src.schemas.academic.material_educativo import MaterialEducativo, MaterialEducativoCreate, MaterialEducativoUpdate
import src.crud.academic.crud_material_educativo as crud_material_educativo_crud

router = APIRouter()

@router.get("/", response_model=list[MaterialEducativo])
def get_all(db: Session = Depends(get_db)):
    return material_educativo_crud.get_multi(db)

@router.get("/{material_id}", response_model=MaterialEducativo)
def get_one(material_id: UUID, db: Session = Depends(get_db)):
    obj = material_educativo_crud.get(db, material_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Material educativo no encontrado")
    return obj

@router.post("/", response_model=MaterialEducativo)
def create(obj_in: MaterialEducativoCreate, db: Session = Depends(get_db)):
    return material_educativo_crud.create(db, obj_in)

@router.put("/{material_id}", response_model=MaterialEducativo)
def update(material_id: UUID, obj_in: MaterialEducativoUpdate, db: Session = Depends(get_db)):
    db_obj = material_educativo_crud.get(db, material_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Material educativo no encontrado")
    return material_educativo_crud.update(db, db_obj, obj_in)

@router.delete("/{material_id}", response_model=MaterialEducativo)
def delete(material_id: UUID, db: Session = Depends(get_db)):
    obj = material_educativo_crud.remove(db, material_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Material educativo no encontrado")
    return obj
