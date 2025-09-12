from sqlalchemy.orm import Session
from src.models.users.usuario import Usuario
from src.schemas.users.usuario import UsuarioCreate
from src.utils.security import pwd_context
import uuid

def create_usuario(db: Session, usuario_in: UsuarioCreate) -> Usuario:
    hashed_pw = pwd_context.hash(usuario_in.password)

    db_usuario = Usuario(
        usuario_id=uuid.uuid4(),
        correo_institucional=usuario_in.correo_institucional,
        username=usuario_in.username,
        rol=usuario_in.rol,
        password_hash=hashed_pw
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario
