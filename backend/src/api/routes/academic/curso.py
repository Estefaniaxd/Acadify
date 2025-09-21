from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.api.deps import get_db
from src.schemas.academic.curso import Curso, CursoCreate, CursoUpdate
import src.crud.academic.crud_curso as crud_curso

router = APIRouter()

@router.get("/", response_model=list[Curso])
def get_cursos(db: Session = Depends(get_db)):
    return curso.get_multi(db)

@router.get("/{curso_id}", response_model=Curso)
def get_curso(curso_id: UUID, db: Session = Depends(get_db)):
    curso_obj = curso.get(db, curso_id)
    if not curso_obj:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso_obj

@router.post("/", response_model=Curso)
def create_curso(obj_in: CursoCreate, db: Session = Depends(get_db)):
    return curso.create(db, obj_in)

@router.put("/{curso_id}", response_model=Curso)
def update_curso(curso_id: UUID, obj_in: CursoUpdate, db: Session = Depends(get_db)):
    db_obj = curso.get(db, curso_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso.update(db, db_obj, obj_in)

@router.delete("/{curso_id}", response_model=Curso)
def delete_curso(curso_id: UUID, db: Session = Depends(get_db)):
    curso_obj = curso.remove(db, curso_id)
    if not curso_obj:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso_obj
