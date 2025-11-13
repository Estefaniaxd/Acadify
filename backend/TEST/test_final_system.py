#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de comentarios y archivos
"""

import sys
sys.path.append('backend/src')

def test_imports():
    """Verificar que todas las importaciones funcionen"""
    print("🔍 Verificando importaciones...")
    
    try:
        from main import app
        print("✅ Backend se puede importar")
    except Exception as e:
        print(f"❌ Error importando backend: {e}")
        return False
    
    try:
        from models.communication.comentario import Comentario
        print("✅ Modelo Comentario OK")
    except Exception as e:
        print(f"❌ Error importando Comentario: {e}")
        return False
    
    try:
        from db.session import SessionLocal
        print("✅ Sesión de DB OK")
    except Exception as e:
        print(f"❌ Error importando SessionLocal: {e}")
        return False
    
    return True

def test_database_structure():
    """Verificar estructura de la base de datos"""
    print("\n🗄️ Verificando estructura de BD...")
    
    try:
        from db.session import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Verificar tabla Comentario
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'Comentario',
            AND column_name = 'archivos_adjuntos'
        """))
        
        columns = result.fetchall()
        if columns:
            print(f"✅ Columna archivos_adjuntos existe: {columns[0][1]}")
        else:
            print("❌ Columna archivos_adjuntos no existe")
        
        # Verificar tabla Reacciones
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = 'Reacciones'
        """))
        
        count = result.fetchone()[0]
        if count > 0:
            print("✅ Tabla Reacciones existe")
        else:
            print("❌ Tabla Reacciones no existe")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verificando BD: {e}")
        return False

def test_file_system():
    """Verificar sistema de archivos"""
    print("\n📁 Verificando sistema de archivos...")
    
    import os
    
    # Verificar directorio static
    static_dir = "backend/static"
    if os.path.exists(static_dir):
        print(f"✅ Directorio static existe: {static_dir}")
    else:
        print(f"❌ Directorio static no existe: {static_dir}")
        return False
    
    # Verificar directorio uploads
    uploads_dir = "backend/static/uploads"
    if os.path.exists(uploads_dir):
        print(f"✅ Directorio uploads existe: {uploads_dir}")
    else:
        print(f"❌ Directorio uploads no existe: {uploads_dir}")
        return False
    
    # Verificar directorio cursos
    cursos_dir = "backend/static/uploads/cursos"
    if os.path.exists(cursos_dir):
        print(f"✅ Directorio cursos existe: {cursos_dir}")
    else:
        print(f"❌ Directorio cursos no existe: {cursos_dir}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA")
    print("=" * 50)
    
    success = True
    
    # Test 1: Importaciones
    if not test_imports():
        success = False
    
    # Test 2: Base de datos
    if not test_database_structure():
        success = False
    
    # Test 3: Sistema de archivos
    if not test_file_system():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TODAS LAS PRUEBAS PASARON")
        print("✅ El sistema está listo para usar")
        print("\nPara probar:")
        print("1. cd backend && python src/main.py")
        print("2. cd frontend && npm run dev")
        print("3. Ir a http://localhost:5173")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("⚠️ Revisa los errores arriba")
    
    return success

if __name__ == "__main__":
    main()