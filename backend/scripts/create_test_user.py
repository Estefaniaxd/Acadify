"""Script para crear un usuario de prueba."""

from src.db.session import SessionLocal
from src.models.users.usuario import Usuario
from src.enums.users.usuario_enums import RolUsuario, EstadoCuentaUsuario
from passlib.context import CryptContext
from uuid import uuid4

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    db = SessionLocal()
    try:
        # Verificar si ya existe
        existing = db.query(Usuario).filter(Usuario.correo_institucional == "airamairam178@gmail.com").first()
        if existing:
            print("✅ El usuario ya existe")
            return
        
        # Crear nuevo usuario
        hashed_password = pwd_context.hash("123456")
        
        new_user = Usuario(
            usuario_id=uuid4(),
            correo_institucional="airamairam178@gmail.com",
            username="airam178",
            nombres="Airam",
            apellidos="Test User",
            tipo_documento="CC",
            numero_documento="1234567890",
            rol=RolUsuario.estudiante,
            password_hash=hashed_password,
            estado_cuenta=EstadoCuentaUsuario.activo,
            email_verified=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Usuario creado exitosamente:")
        print(f"   Email: {new_user.correo_institucional}")
        print(f"   Username: {new_user.username}")
        print(f"   Rol: {new_user.rol}")
        print(f"   Password: 123456")
        
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
