from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.db.session import get_db
from src.schemas.academic.estudiante_grupo import EstudianteGrupo, EstudianteGrupoCreate, EstudianteGrupoUpdate
from src.crud.academic.crud_estudiante_grupo import estudiante_grupo_crud

router = APIRouter()

@router.get("/", response_model=list[EstudianteGrupo])
def get_all(db: Session = Depends(get_db)):
    return estudiante_grupo_crud.get_multi(db)

@router.get("/{grupo_id}/{estudiante_id}", response_model=EstudianteGrupo)
def get_one(grupo_id: UUID, estudiante_id: UUID, db: Session = Depends(get_db)):
    obj = estudiante_grupo_crud.get(db, (grupo_id, estudiante_id))
    if not obj:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    return obj

@router.post("/", response_model=EstudianteGrupo)
def create(obj_in: EstudianteGrupoCreate, db: Session = Depends(get_db)):
    return estudiante_grupo_crud.create(db, obj_in)

@router.put("/{grupo_id}/{estudiante_id}", response_model=EstudianteGrupo)
def update(grupo_id: UUID, estudiante_id: UUID, obj_in: EstudianteGrupoUpdate, db: Session = Depends(get_db)):
    db_obj = estudiante_grupo_crud.get(db, (grupo_id, estudiante_id))
    if not db_obj:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    return estudiante_grupo_crud.update(db, db_obj, obj_in)

@router.delete("/{grupo_id}/{estudiante_id}", response_model=EstudianteGrupo)
def delete(grupo_id: UUID, estudiante_id: UUID, db: Session = Depends(get_db)):
    obj = estudiante_grupo_crud.remove(db, (grupo_id, estudiante_id))
    if not obj:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    return obj
