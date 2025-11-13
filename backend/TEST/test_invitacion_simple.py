"""
Test simple del flujo de invitación - Creación directa en BD
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.session import SessionLocal
from src.services.invitation_service import InvitationService
from src.models.academic.institucion import Institucion
from datetime import datetime
import requests

def crear_institucion_prueba(db):
    """Crea una institución de prueba"""
    timestamp = datetime.now().strftime("%H%M%S")
    
    institucion = Institucion(
        nombre=f"Universidad Test {timestamp}",
        sigla=f"UT{timestamp[-4:]}",
        tipo_institucion="universidad",
        usa_programas=True,
        nivel_educativo="superior",
        sector="publico",
        pais="Colombia",
        correo_institucional=f"test{timestamp}@universidad.edu.co",
        telefono="+57 300 123 4567",
        estado="pendiente",
    )
    
    db.add(institucion)
    db.commit()
    db.refresh(institucion)
    
    print(f"✓ Institución creada: {institucion.nombre}")
    print(f"  ID: {institucion.institucion_id}")
    print(f"  Estado: {institucion.estado}")
    
    return institucion

def crear_invitacion_prueba(db, institucion_id, email):
    """Crea una invitación usando el servicio"""
    invitacion = InvitationService.crear_invitacion(
        db=db,
        email_destino=email,
        institucion_id=institucion_id,
    )
    
    print(f"✓ Invitación creada")
    print(f"  Código: {invitacion.codigo}")
    print(f"  Email: {invitacion.email_destino}")
    print(f"  Estado: {invitacion.estado}")
    
    return invitacion

def test_validar_codigo(codigo):
    """Prueba el endpoint de validación de código"""
    print(f"\n📋 Probando validación de código: {codigo}")
    
    # El endpoint de validación es GET en /invitaciones/validar/{codigo}
    response = requests.get(
        f"http://localhost:8000/invitaciones/validar/{codigo}"
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:,
        data = response.json()
        print(f"✓ Código válido!")
        print(f"  Institución: {data['institucion']['nombre']}")
        print(f"  Email destino: {data['invitacion']['email_destino']}")
        return True
    else:
        print(f"✗ Error Response: {response.text}")
        return False

def test_aceptar_invitacion(codigo):
    """Prueba el endpoint de aceptar invitación"""
    print(f"\n✅ Probando aceptación de invitación: {codigo}")
    
    # El endpoint de aceptar espera JSON en el body
    response = requests.post(
        "http://localhost:8000/invitaciones/aceptar",
        json={
            "codigo": codigo,
            "nombre": "Juan Carlos",
            "apellido": "Coordinador Test",
            "password": "TestPassword123!"
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:,
        data = response.json()
        print(f"✓ Invitación aceptada exitosamente!")
        print(f"  Usuario: {data['usuario']['nombre']} {data['usuario']['apellido']}")
        print(f"  Email: {data['usuario']['email']}")
        print(f"  Institución: {data['institucion']['nombre']}")
        print(f"  Estado institución: {data['institucion']['estado']}")
        return True
    else:
        print(f"✗ Error: {response.text}")
        return False

def main():
    print("="*60)
    print("🧪 TEST SIMPLE: FLUJO DE INVITACIÓN")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # 1. Crear institución de prueba
        print("\n1️⃣ Creando institución de prueba...")
        institucion = crear_institucion_prueba(db)
        
        # 2. Crear invitación
        print("\n2️⃣ Creando invitación...")
        timestamp = datetime.now().strftime("%H%M%S")
        email_test = f"coord.test{timestamp}@gmail.com",
        invitacion = crear_invitacion_prueba(db, institucion.institucion_id, email_test)
        
        # 3. Probar validación
        print("\n3️⃣ Probando endpoint de validación...")
        if not test_validar_codigo(invitacion.codigo):
            print("❌ Falló la validación")
            return
        
        # 4. Probar aceptación
        print("\n4️⃣ Probando endpoint de aceptación...")
        if not test_aceptar_invitacion(invitacion.codigo):
            print("❌ Falló la aceptación")
            return
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
