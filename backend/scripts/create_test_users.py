#!/usr/bin/env python3
"""
Script para crear usuarios de prueba para load testing
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.models.users.usuario import Usuario
from src.enums.users.usuario_enums import RolUsuario, TipoDocumentoUsuario, EstadoCuentaUsuario
from src.utils.security import SecurityManager
from datetime import datetime

# Initialize security manager
security_manager = SecurityManager()


def create_admin_user(db: Session):
    """Create admin test user"""
    # Check if user exists
    existing = db.query(Usuario).filter(Usuario.correo_institucional == "admin@senasofia.edu.co").first()
    if not existing:
        existing = db.query(Usuario).filter(Usuario.username == "admin_sena").first()
    
    if existing:
        print(f"✓ Admin user already exists: {existing.correo_institucional or existing.username} (ID: {existing.usuario_id})")
        return existing

    # Create user (admin uses username, not correo_institucional)
    admin_user = Usuario(
        nombres="Admin",
        apellidos="SENA",
        username="admin_sena",
        correo_institucional=None,  # Admin doesn't use institutional email
        password_hash=security_manager.get_password_hash("admin123"),
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento="1000000001",
        rol=RolUsuario.administrador,
        estado_cuenta=EstadoCuentaUsuario.activo
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"✓ Created admin user: {admin_user.username} (ID: {admin_user.usuario_id})")
    return admin_user


def create_docente_user(db: Session):
    """Create docente test user"""
    # Check if user exists
    existing = db.query(Usuario).filter(Usuario.correo_institucional == "docente@senasofia.edu.co").first()
    if existing:
        print(f"✓ Docente user already exists: {existing.correo_institucional} (ID: {existing.usuario_id})")
        return existing

    # Create user
    docente_user = Usuario(
        nombres="Docente",
        apellidos="SENA",
        correo_institucional="docente@senasofia.edu.co",
        username=None,  # Non-admin uses email
        password_hash=security_manager.get_password_hash("docente123"),
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento="1000000002",
        rol=RolUsuario.docente,
        estado_cuenta=EstadoCuentaUsuario.activo
    )
    
    db.add(docente_user)
    db.commit()
    db.refresh(docente_user)
    
    print(f"✓ Created docente user: {docente_user.correo_institucional} (ID: {docente_user.usuario_id})")
    return docente_user


def create_estudiante_user(db: Session):
    """Create estudiante test user"""
    # Check if user exists
    existing = db.query(Usuario).filter(Usuario.correo_institucional == "estudiante@senasofia.edu.co").first()
    if existing:
        print(f"✓ Estudiante user already exists: {existing.correo_institucional} (ID: {existing.usuario_id})")
        return existing

    # Create user
    estudiante_user = Usuario(
        nombres="Estudiante",
        apellidos="SENA",
        correo_institucional="estudiante@senasofia.edu.co",
        username=None,  # Non-admin uses email
        password_hash=security_manager.get_password_hash("estudiante123"),
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento="1000000003",
        rol=RolUsuario.estudiante,
        estado_cuenta=EstadoCuentaUsuario.activo
    )
    
    db.add(estudiante_user)
    db.commit()
    db.refresh(estudiante_user)
    
    print(f"✓ Created estudiante user: {estudiante_user.correo_institucional} (ID: {estudiante_user.usuario_id})")
    return estudiante_user


def main():
    """Main function"""
    print("=" * 70)
    print("Creating test users for load testing...")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # Create users
        admin = create_admin_user(db)
        docente = create_docente_user(db)
        estudiante = create_estudiante_user(db)
        
        print("\n" + "=" * 70)
        print("✅ Test users created successfully!")
        print("=" * 70)
        print("\n📋 Credentials:")
        print("-" * 70)
        print(f"Admin:      admin@senasofia.edu.co      / admin123")
        print(f"Docente:    docente@senasofia.edu.co    / docente123")
        print(f"Estudiante: estudiante@senasofia.edu.co / estudiante123")
        print("-" * 70)
        
        print("\n🧪 Test with curl:")
        print('curl -X POST http://localhost:8000/auth/login \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"identifier":"admin@senasofia.edu.co","password":"admin123"}\'')
        
    except Exception as e:
        print(f"\n❌ Error creating test users: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
