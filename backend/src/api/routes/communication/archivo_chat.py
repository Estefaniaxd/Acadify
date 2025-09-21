from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.schemas.communication.archivo_chat import (
    ArchivoChatCreate,
    ArchivoChatUpdate,
    ArchivoChat,
)
import src.crud.communication.archivo_chat as archivo_chat

router = APIRouter()
ARCHIVO_NOT_FOUND = "Archivo no encontrado"


@router.post("/", response_model=ArchivoChat)
def create_archivo_chat(
    *, db: Session = Depends(get_db), archivo_in: ArchivoChatCreate
):
    return archivo_chat.create(db=db, obj_in=archivo_in)


@router.get("/{archivo_id}", response_model=ArchivoChat)
def read_archivo_chat(archivo_id: str, db: Session = Depends(get_db)):
    db_obj = archivo_chat.get(db=db, id=archivo_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail=ARCHIVO_NOT_FOUND)
    return db_obj


@router.put("/{archivo_id}", response_model=ArchivoChat)
def update_archivo_chat(
    archivo_id: str, archivo_in: ArchivoChatUpdate, db: Session = Depends(get_db)
):
    db_obj = archivo_chat.get(db=db, id=archivo_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail=ARCHIVO_NOT_FOUND)
    return archivo_chat.update(db=db, db_obj=db_obj, obj_in=archivo_in)


@router.delete("/{archivo_id}", response_model=ArchivoChat)
def delete_archivo_chat(archivo_id: str, db: Session = Depends(get_db)):
    db_obj = archivo_chat.get(db=db, id=archivo_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail=ARCHIVO_NOT_FOUND)
    return archivo_chat.remove(db=db, id=archivo_id)
