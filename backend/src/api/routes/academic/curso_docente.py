from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.db.session import get_db
from src.schemas.academic.curso_docente import CursoDocente, CursoDocenteCreate, CursoDocenteUpdate
from src.crud.academic.crud_curso_docente import curso_docente_crud

router = APIRouter(prefix="/cursos-docentes", tags=["CursoDocente"])

@router.get("/", response_model=list[CursoDocente])
def get_all(db: Session = Depends(get_db)):
    return curso_docente_crud.get_multi(db)

@router.get("/{curso_id}/{docente_id}", response_model=CursoDocente)
def get_one(curso_id: UUID, docente_id: UUID, db: Session = Depends(get_db)):
    obj = curso_docente_crud.get(db, (curso_id, docente_id))
    if not obj:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return obj

@router.post("/", response_model=CursoDocente)
def create(obj_in: CursoDocenteCreate, db: Session = Depends(get_db)):
    return curso_docente_crud.create(db, obj_in)

@router.put("/{curso_id}/{docente_id}", response_model=CursoDocente)
def update(curso_id: UUID, docente_id: UUID, obj_in: CursoDocenteUpdate, db: Session = Depends(get_db)):
    db_obj = curso_docente_crud.get(db, (curso_id, docente_id))
    if not db_obj:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return curso_docente_crud.update(db, db_obj, obj_in)

@router.delete("/{curso_id}/{docente_id}", response_model=CursoDocente)
def delete(curso_id: UUID, docente_id: UUID, db: Session = Depends(get_db)):
    obj = curso_docente_crud.remove(db, (curso_id, docente_id))
    if not obj:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return obj
