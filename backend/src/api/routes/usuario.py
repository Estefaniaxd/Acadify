from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.schemas.usuario import UsuarioCreate, UsuarioRead
from src.services.usuario_service import create_usuario
from src.db.session import get_db

router = APIRouter()

@router.post("/usuarios", response_model=UsuarioRead)
def crear_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db)):
    return create_usuario(db, usuario_in)
