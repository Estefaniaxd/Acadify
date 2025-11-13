#!/usr/bin/env python3
"""
Script para probar el sistema de login y crear un usuario de prueba si no existe.
"""

import sys
import os
import asyncio

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.crud.user.usuario import usuario_crud
from src.utils.security import security_manager
from src.enums.users.usuario_enums import RolUsuario, TipoDocumentoUsuario, EstadoCuentaUsuario
from src.models.users.usuario import Usuario

def create_test_admin():
    """Crear un usuario administrador de prueba"""
    db = SessionLocal()
    try:
        # Verificar si ya existe un admin con username 'admin'
        existing_admin = db.query(Usuario).filter(Usuario.username == 'admin').first()
        
        if existing_admin:
            print("✅ Usuario admin ya existe")
            print(f"   Username: {existing_admin.username}")
            print(f"   Nombre: {existing_admin.nombres} {existing_admin.apellidos}")
            return
        
        # Crear nuevo administrador
        admin_data = {
            "username": "admin",
            "correo_institucional": None,  # Los admin no tienen correo institucional
            "nombres": "Administrador",
            "apellidos": "Sistema",
            "tipo_documento": TipoDocumentoUsuario.cc,
            "numero_documento": "1234567890",
            "rol": RolUsuario.administrador,
            "password_hash": security_manager.get_password_hash("admin123"),
            "estado_cuenta": EstadoCuentaUsuario.activo,
            "email_verified": True,
        }
        
        new_admin = Usuario(**admin_data)
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        print("🎉 Usuario administrador creado exitosamente!")
        print(f"   Username: {new_admin.username}")
        print(f"   Password: admin123")
        print(f"   Nombre: {new_admin.nombres} {new_admin.apellidos}")
        print(f"\n💡 Puedes iniciar sesión con:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        
    except Exception as e:
        print(f"❌ Error creando administrador: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def test_password_hash():
    """Probar que el hashing de contraseñas funciona correctamente"""
    print("\n🔍 Probando sistema de hashing de contraseñas...")
    
    test_password = "admin123"
    hashed = security_manager.get_password_hash(test_password)
    
    print(f"   ✅ Hash generado: {hashed[:50]}...")
    
    # Verificar que la contraseña coincide con el hash
    is_valid = security_manager.verify_password(test_password, hashed)
    
    if is_valid:
        print(f"   ✅ Verificación de contraseña funciona correctamente")
    else:
        print(f"   ❌ Error: la verificación de contraseña falló")
    
    return is_valid

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🔐 ACADIFY - TEST DE SISTEMA DE LOGIN")
    print("="*60 + "\n")
    
    # Probar hashing de contraseñas
    if not test_password_hash():
        print("\n❌ El sistema de hashing de contraseñas tiene problemas.")
        return 1
    
    # Crear usuario admin de prueba
    print("\n📝 Creando usuario administrador de prueba...")
    create_test_admin()
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETADO")
    print("="*60)
    print("\n💡 Puedes probar el login en:")
    print("   http://localhost:8000/docs")
    print("   Endpoint: POST /auth/login")
    print("   Body: {")
    print('     "identifier": "admin",')
    print('     "password": "admin123"')
    print("   }")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
