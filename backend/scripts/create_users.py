"""Script para crear usuarios de prueba"""

import sys

sys.path.insert(0, "src")

import uuid

from src.db.session import SessionLocal
from src.models.users.usuario import Usuario
from src.services.auth.password_service import PasswordService


def verificar_y_crear_usuarios():
    db = SessionLocal()
    password_service = PasswordService()

    try:
        # Definir usuarios a crear
        usuarios = [
            {
                "email": "juanitomm2408@gmail.com",
                "rol": "administrador",
                "password": "AdminTest123@",  # Diferente para probar recuperación
                "nombres": "Juan",
                "apellidos": "Martínez Admin",
                "username": "juanito_admin",
            },
            {
                "email": "jmartine@arp.edu.co",
                "rol": "coordinador",
                "password": "Juanito243019@",
                "nombres": "Juan",
                "apellidos": "Martínez Coordinador",
                "username": "jmartine_coord",
            },
            {
                "email": "juanestebanmartinezmacias@gmail.com",
                "rol": "docente",  # Cambiado de "profesor" a "docente"
                "password": "Juanito243019@",
                "nombres": "Juan Esteban",
                "apellidos": "Martínez Macías",
                "username": "juanesteban_prof",
            },
            {
                "email": "airamairam178@gmail.com",
                "rol": "estudiante",
                "password": "Juanito243019@",
                "nombres": "María",
                "apellidos": "Estudiante Test",
                "username": "maria_student",
            },
        ]

        print("=" * 60)
        print("VERIFICANDO Y CREANDO USUARIOS")
        print("=" * 60)

        for user_data in usuarios:
            # Verificar si el usuario ya existe
            existing_user = (
                db.query(Usuario)
                .filter(Usuario.correo_institucional == user_data["email"])
                .first()
            )

            if existing_user:
                print(f"\n✓ Ya existe: {user_data['email']}")
                print(f"  - Rol: {existing_user.rol}")
                print(f"  - Username: {existing_user.username}")
                print(f"  - ID: {existing_user.usuario_id}")
            else:
                # Crear nuevo usuario
                nuevo_usuario = Usuario(
                    usuario_id=uuid.uuid4(),
                    correo_institucional=user_data["email"],
                    username=user_data["username"],
                    nombres=user_data["nombres"],
                    apellidos=user_data["apellidos"],
                    rol=user_data["rol"],
                    password_hash=password_service.hash_password(user_data["password"]),
                    tipo_documento="cc",  # Cambiado a minúsculas
                    numero_documento=f"100000{len(db.query(Usuario).all())}",
                    estado_cuenta="activo",
                    email_verified=True,  # Para que puedan iniciar sesión inmediatamente
                )

                db.add(nuevo_usuario)
                db.commit()
                db.refresh(nuevo_usuario)

                print(f"\n✅ CREADO: {user_data['email']}")
                print(f"  - Rol: {user_data['rol']}")
                print(f"  - Username: {user_data['username']}")
                print(f"  - Contraseña: {user_data['password']}")
                print(f"  - ID: {nuevo_usuario.usuario_id}")

        print("\n" + "=" * 60)
        print("RESUMEN DE CREDENCIALES")
        print("=" * 60)

        for user_data in usuarios:
            print(f"\n{user_data['rol'].upper()}:")
            print(f"  Email: {user_data['email']}")
            print(f"  Contraseña: {user_data['password']}")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    verificar_y_crear_usuarios()
