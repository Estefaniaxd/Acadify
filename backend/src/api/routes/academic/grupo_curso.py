from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.db.session import get_db
from src.schemas.academic.grupo_curso import GrupoCurso, GrupoCursoCreate, GrupoCursoUpdate
from src.crud.academic.crud_grupo_curso import grupo_curso_crud

router = APIRouter()

@router.get("/", response_model=list[GrupoCurso])
def get_all(db: Session = Depends(get_db)):
    return grupo_curso_crud.get_multi(db)

@router.get("/{grupo_curso_id}", response_model=GrupoCurso)
def get_one(grupo_curso_id: UUID, db: Session = Depends(get_db)):
    obj = grupo_curso_crud.get(db, grupo_curso_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Relación Grupo-Curso no encontrada")
    return obj

@router.post("/", response_model=GrupoCurso)
def create(obj_in: GrupoCursoCreate, db: Session = Depends(get_db)):
    return grupo_curso_crud.create(db, obj_in)

@router.put("/{grupo_curso_id}", response_model=GrupoCurso)
def update(grupo_curso_id: UUID, obj_in: GrupoCursoUpdate, db: Session = Depends(get_db)):
    db_obj = grupo_curso_crud.get(db, grupo_curso_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Relación Grupo-Curso no encontrada")
    return grupo_curso_crud.update(db, db_obj, obj_in)

@router.delete("/{grupo_curso_id}", response_model=GrupoCurso)
def delete(grupo_curso_id: UUID, db: Session = Depends(get_db)):
    obj = grupo_curso_crud.remove(db, grupo_curso_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Relación Grupo-Curso no encontrada")
    return obj
