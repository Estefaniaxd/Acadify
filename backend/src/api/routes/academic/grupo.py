from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.db.session import get_db
from src.schemas.academic.grupo import Grupo, GrupoCreate, GrupoUpdate
from src.crud.academic.crud_grupo import grupo_crud

# src/api/routes/academic/grupo.py

# ... importaciones reealizadas

router = APIRouter() 

@router.get("/", response_model=list[Grupo])
def get_all(db: Session = Depends(get_db)):
    return grupo_crud.get_multi(db)

@router.get("/{grupo_id}", response_model=Grupo)
def get_one(grupo_id: UUID, db: Session = Depends(get_db)):
    obj = grupo_crud.get(db, grupo_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return obj

# ... resto de código

@router.post("/", response_model=Grupo)
def create(obj_in: GrupoCreate, db: Session = Depends(get_db)):
    return grupo_crud.create(db, obj_in)

@router.put("/{grupo_id}", response_model=Grupo)
def update(grupo_id: UUID, obj_in: GrupoUpdate, db: Session = Depends(get_db)):
    db_obj = grupo_crud.get(db, grupo_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return grupo_crud.update(db, db_obj, obj_in)

@router.delete("/{grupo_id}", response_model=Grupo)
def delete(grupo_id: UUID, db: Session = Depends(get_db)):
    obj = grupo_crud.remove(db, grupo_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return obj
