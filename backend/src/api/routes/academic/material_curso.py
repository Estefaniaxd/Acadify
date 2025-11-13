from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.schemas.academic.material_curso import (
    MaterialCurso,
    MaterialCursoCreate,
    MaterialCursoUpdate,
)


router = APIRouter()


@router.get("/", response_model=list[MaterialCurso])
def get_all(db: Session = Depends(get_db)):
    return material_curso_crud.get_multi(db)


@router.get("/{material_curso_id}", response_model=MaterialCurso)
def get_one(material_curso_id: UUID, db: Session = Depends(get_db)):
    obj = material_curso_crud.get(db, material_curso_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Material de curso no encontrado")
    return obj


@router.post("/", response_model=MaterialCurso)
def create(obj_in: MaterialCursoCreate, db: Session = Depends(get_db)):
    return material_curso_crud.create(db, obj_in)


@router.put("/{material_curso_id}", response_model=MaterialCurso)
def update(
    material_curso_id: UUID, obj_in: MaterialCursoUpdate, db: Session = Depends(get_db)
):
    db_obj = material_curso_crud.get(db, material_curso_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Material de curso no encontrado")
    return material_curso_crud.update(db, db_obj, obj_in)


@router.delete("/{material_curso_id}", response_model=MaterialCurso)
def delete(material_curso_id: UUID, db: Session = Depends(get_db)):
    obj = material_curso_crud.remove(db, material_curso_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Material de curso no encontrado")
    return obj
