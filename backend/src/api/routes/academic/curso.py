from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.db.session import get_db
from src.schemas.academic.curso import Curso, CursoCreate, CursoUpdate
from src.crud.academic.crud_curso import curso_crud

router = APIRouter()

@router.get("/", response_model=list[Curso])
def get_cursos(db: Session = Depends(get_db)):
    return curso_crud.get_multi(db)

@router.get("/{curso_id}", response_model=Curso)
def get_curso(curso_id: UUID, db: Session = Depends(get_db)):
    curso = curso_crud.get(db, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso

@router.post("/", response_model=Curso)
def create_curso(obj_in: CursoCreate, db: Session = Depends(get_db)):
    return curso_crud.create(db, obj_in)

@router.put("/{curso_id}", response_model=Curso)
def update_curso(curso_id: UUID, obj_in: CursoUpdate, db: Session = Depends(get_db)):
    db_obj = curso_crud.get(db, curso_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso_crud.update(db, db_obj, obj_in)

@router.delete("/{curso_id}", response_model=Curso)
def delete_curso(curso_id: UUID, db: Session = Depends(get_db)):
    curso = curso_crud.remove(db, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso
