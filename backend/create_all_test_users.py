"""
Script para crear todos los usuarios de prueba del sistema.
Crea: Administrador, Coordinador, Docente y Estudiante.
"""

from uuid import UUID

from passlib.context import CryptContext

from src.db.session import SessionLocal
from src.enums.users.usuario_enums import (
    EstadoCuentaUsuario,
    RolUsuario,
    TipoDocumentoUsuario,
)
from src.models.users.usuario import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Datos de los usuarios de prueba
USUARIOS_TEST = [
    {
        "usuario_id": "f860d893-1a60-49cc-ba9c-8aac75577b0f",
        "email": "airamairam178@gmail.com",
        "username": "maria_student",
        "nombres": "María",
        "apellidos": "García Estudiante",
        "tipo_documento": TipoDocumentoUsuario.cc,
        "numero_documento": "1000000001",
        "rol": RolUsuario.estudiante,
        "password": "Juanito243019@",
    },
    {
        "usuario_id": "a1b2c3d4-e5f6-4a5b-8c9d-1e2f3a4b5c6d",
        "email": "juanitomm2408@gmail.com",
        "username": "admin_juanito",
        "nombres": "Juan",
        "apellidos": "Martínez Administrador",
        "tipo_documento": TipoDocumentoUsuario.cc,
        "numero_documento": "1000000002",
        "rol": RolUsuario.administrador,
        "password": "AdminTest123@",
    },
    {
        "usuario_id": "b2c3d4e5-f6a7-4b5c-9d1e-2f3a4b5c6d7e",
        "email": "jmartine@arp.edu.co",
        "username": "coordinador_jm",
        "nombres": "José",
        "apellidos": "Martínez Coordinador",
        "tipo_documento": TipoDocumentoUsuario.cc,
        "numero_documento": "1000000003",
        "rol": RolUsuario.coordinador,
        "password": "Juanito243019@",
    },
    {
        "usuario_id": "c3d4e5f6-a7b8-4c5d-1e2f-3a4b5c6d7e8f",
        "email": "juanestebanmartinezmacias@gmail.com",
        "username": "docente_juan",
        "nombres": "Juan Esteban",
        "apellidos": "Martínez Macías",
        "tipo_documento": TipoDocumentoUsuario.cc,
        "numero_documento": "1000000004",
        "rol": RolUsuario.docente,
        "password": "Juanito243019@",
    },
]


def create_all_users():
    db = SessionLocal()
    created_count = 0
    skipped_count = 0

    try:
        print("\n" + "=" * 60)
        print("CREANDO USUARIOS DE PRUEBA")
        print("=" * 60 + "\n")

        for user_data in USUARIOS_TEST:
            # Verificar si ya existe
            existing = (
                db.query(Usuario)
                .filter(Usuario.correo_institucional == user_data["email"])
                .first()
            )

            if existing:
                print(f"⏭️  OMITIDO: {user_data['email']} (ya existe)")
                skipped_count += 1
                continue

            # Crear hash de contraseña
            hashed_password = pwd_context.hash(user_data["password"])

            # Crear usuario
            new_user = Usuario(
                usuario_id=UUID(user_data["usuario_id"]),
                correo_institucional=user_data["email"],
                username=user_data["username"],
                nombres=user_data["nombres"],
                apellidos=user_data["apellidos"],
                tipo_documento=user_data["tipo_documento"],
                numero_documento=user_data["numero_documento"],
                rol=user_data["rol"],
                password_hash=hashed_password,
                estado_cuenta=EstadoCuentaUsuario.activo,
                email_verified=True,
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            print(f"✅ CREADO: {user_data['email']}")
            print(f"  - Rol: {user_data['rol']}")
            print(f"  - Username: {user_data['username']}")
            print(f"  - Contraseña: {user_data['password']}")
            print(f"  - ID: {user_data['usuario_id']}\n")

            created_count += 1

        print("=" * 60)
        print("RESUMEN")
        print("=" * 60)
        print(f"✅ Usuarios creados: {created_count}")
        print(f"⏭️  Usuarios omitidos: {skipped_count}")
        print(f"📊 Total en base de datos: {created_count + skipped_count}")

        print("\n" + "=" * 60)
        print("RESUMEN DE CREDENCIALES")
        print("=" * 60 + "\n")

        print("ADMINISTRADOR:")
        print("  Email: juanitomm2408@gmail.com")
        print("  Contraseña: AdminTest123@\n")

        print("COORDINADOR:")
        print("  Email: jmartine@arp.edu.co")
        print("  Contraseña: Juanito243019@\n")

        print("DOCENTE:")
        print("  Email: juanestebanmartinezmacias@gmail.com")
        print("  Contraseña: Juanito243019@\n")

        print("ESTUDIANTE:")
        print("  Email: airamairam178@gmail.com")
        print("  Contraseña: Juanito243019@\n")

    except Exception as e:
        print(f"\n❌ Error creando usuarios: {e}")
        db.rollback()
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_all_users()
