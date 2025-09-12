from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.db.session import get_db
from src.schemas.academic.material_clase import MaterialClase, MaterialClaseCreate, MaterialClaseUpdate
from src.crud.academic.crud_material_clase import material_clase_crud

router = APIRouter(prefix="/materiales-clases", tags=["MaterialClase"])

@router.get("/", response_model=list[MaterialClase])
def get_all(db: Session = Depends(get_db)):
    return material_clase_crud.get_multi(db)

@router.get("/{material_clase_id}", response_model=MaterialClase)
def get_one(material_clase_id: UUID, db: Session = Depends(get_db)):
    obj = material_clase_crud.get(db, material_clase_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Material de clase no encontrado")
    return obj

@router.post("/", response_model=MaterialClase)
def create(obj_in: MaterialClaseCreate, db: Session = Depends(get_db)):
    return material_clase_crud.create(db, obj_in)

@router.put("/{material_clase_id}", response_model=MaterialClase)
def update(material_clase_id: UUID, obj_in: MaterialClaseUpdate, db: Session = Depends(get_db)):
    db_obj = material_clase_crud.get(db, material_clase_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Material de clase no encontrado")
    return material_clase_crud.update(db, db_obj, obj_in)

@router.delete("/{material_clase_id}", response_model=MaterialClase)
def delete(material_clase_id: UUID, db: Session = Depends(get_db)):
    obj = material_clase_crud.remove(db, material_clase_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Material de clase no encontrado")
    return obj
