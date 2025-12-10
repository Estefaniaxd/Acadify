#!/usr/bin/env python3
"""
Diagnóstico de archivos en BD
Verifica qué archivos se guardaron realmente
"""
import os
import sys
import json

# Agregar backend al path
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

from src.db.database import SessionLocal
from sqlalchemy import text

def main():
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("🔍 DIAGNÓSTICO DE ARCHIVOS EN BD")
        print("=" * 80)
        
        # 1. Obtener últimas 3 entregas
        query = text("""
            SELECT 
                entrega_id,
                tarea_id,
                estudiante_id,
                archivo_url,
                archivos_adicionales,
                fecha_entrega,
                estado
            FROM entregas_tareas
            ORDER BY fecha_entrega DESC
            LIMIT 3
        """)
        
        results = db.execute(query).fetchall()
        
        if not results:
            print("❌ No hay entregas registradas en la BD")
            return
        
        for i, row in enumerate(results, 1):
            print(f"\n📦 ENTREGA #{i}")
            print(f"   ID: {row.entrega_id}")
            print(f"   Tarea: {row.tarea_id}")
            print(f"   Estudiante: {row.estudiante_id}")
            print(f"   Fecha: {row.fecha_entrega}")
            print(f"   Estado: {row.estado}")
            
            # Campo archivo_url (legado)
            print(f"\n   📄 Campo 'archivo_url' (legado):")
            if row.archivo_url:
                print(f"      ✓ {row.archivo_url}")
            else:
                print(f"      ✗ NULL (vacío)")
            
            # Campo archivos_adicionales (nuevo JSON)
            print(f"\n   📋 Campo 'archivos_adicionales' (JSON):")
            if row.archivos_adicionales:
                try:
                    archivos_data = json.loads(row.archivos_adicionales)
                    print(f"      ✓ JSON válido")
                    
                    if isinstance(archivos_data, dict) and 'archivos' in archivos_data:
                        archivos = archivos_data['archivos']
                        print(f"      📊 Total archivos: {len(archivos)}")
                        
                        for j, archivo in enumerate(archivos, 1):
                            print(f"\n      Archivo {j}:")
                            if isinstance(archivo, dict):
                                print(f"         URL: {archivo.get('url', 'N/A')}")
                                print(f"         Nombre Original: {archivo.get('nombre_original', 'N/A')}")
                                print(f"         Nombre Almacenado: {archivo.get('nombre_almacenado', 'N/A')}")
                            else:
                                print(f"         {archivo}")
                    else:
                        print(f"      ⚠️ Estructura JSON inválida: {archivos_data}")
                        
                except json.JSONDecodeError as e:
                    print(f"      ❌ Error al parsear JSON: {e}")
                    print(f"      Contenido: {row.archivos_adicionales[:200]}")
            else:
                print(f"      ✗ NULL (vacío)")
            
            print(f"\n   " + "-" * 70)
        
        # 2. Verificar directorio de uploads
        print(f"\n\n{'='*80}")
        print("📁 VERIFICACIÓN DE DIRECTORIO DE UPLOADS")
        print(f"{'='*80}")
        
        upload_dir = "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/uploads/entregas"
        
        if os.path.exists(upload_dir):
            files = os.listdir(upload_dir)
            print(f"✓ Directorio existe: {upload_dir}")
            print(f"  Total archivos: {len(files)}")
            
            if files:
                print(f"\n  Primeros 10 archivos:")
                for f in files[:10]:
                    file_path = os.path.join(upload_dir, f)
                    size = os.path.getsize(file_path)
                    print(f"    - {f} ({size} bytes)")
        else:
            print(f"❌ Directorio NO existe: {upload_dir}")
        
        print(f"\n{'='*80}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
