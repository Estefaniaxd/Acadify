#!/usr/bin/env python3
"""
Script para verificar si los archivos se están guardando en la BD
"""

import sys
import os
sys.path.append('/home/esteban/Acadify/backend/src')

def check_database():
    """Verificar archivos en la BD"""
    try:
        from db.session import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Verificar comentarios con archivos
        result = db.execute(text("""
            SELECT comentario_id, contenido, archivos_adjuntos, fecha_creacion
            FROM "Comentario" 
            WHERE archivos_adjuntos IS NOT NULL 
            AND archivos_adjuntos != ''
            ORDER BY fecha_creacion DESC
            LIMIT 5
        """))
        
        comentarios = result.fetchall()
        
        print(f"🔍 Encontrados {len(comentarios)} comentarios con archivos:")
        print("-" * 60)
        
        for i, comentario in enumerate(comentarios, 1):
            print(f"\n{i}. Comentario ID: {comentario[0]}")
            print(f"   Contenido: {comentario[1][:50]}...")
            print(f"   Archivos JSON: {comentario[2]}")
            print(f"   Fecha: {comentario[3]}")
        
        if len(comentarios) == 0:
            print("❌ No hay comentarios con archivos en la BD")
        
        db.close()
        return len(comentarios) > 0
        
    except Exception as e:
        print(f"❌ Error verificando BD: {e}")
        return False

def check_filesystem():
    """Verificar archivos en el sistema de archivos"""
    uploads_dir = "/home/esteban/Acadify/backend/static/uploads/cursos"
    
    if not os.path.exists(uploads_dir):
        print(f"❌ Directorio no existe: {uploads_dir}")
        return False
    
    files = os.listdir(uploads_dir)
    print(f"\n📁 Archivos en {uploads_dir}:")
    print(f"   Total: {len(files)} archivos")
    
    for f in files[:10]:  # Mostrar máximo 10
        file_path = os.path.join(uploads_dir, f)
        size = os.path.getsize(file_path)
        print(f"   - {f} ({size} bytes)")
    
    return len(files) > 0

if __name__ == "__main__":
    print("🔍 VERIFICANDO PERSISTENCIA DE ARCHIVOS")
    print("=" * 50)
    
    db_ok = check_database()
    fs_ok = check_filesystem()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN:")
    print(f"   BD tiene archivos: {'✅' if db_ok else '❌'}")
    print(f"   Sistema archivos: {'✅' if fs_ok else '❌'}")
    
    if db_ok and fs_ok:
        print("🎉 Los archivos SÍ se están guardando")
        print("🔍 El problema debe estar en el frontend")
    elif db_ok and not fs_ok:
        print("⚠️  BD OK pero archivos físicos faltan")
    elif not db_ok and fs_ok:
        print("⚠️  Archivos físicos OK pero no en BD")
    else:
        print("❌ Ni BD ni archivos físicos funcionan")