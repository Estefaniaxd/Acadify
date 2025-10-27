#!/usr/bin/env python3
"""
Script minimalista para probar solo la consulta BD sin dependencias FastAPI
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def test_database_query():
    """Probar consulta directa a la BD"""
    try:
        # Import solo los módulos de BD necesarios
        from src.db.session import SessionLocal
        from sqlalchemy import text
        
        print("🔄 Probando conexión directa a la BD...")
        
        db = SessionLocal()
        try:
            # Consultar cursos reales
            result = db.execute(text('''
                SELECT 
                    c.curso_id,
                    c.nombre,
                    c.descripcion,
                    c.modalidad,
                    c.fecha_inicio,
                    c.fecha_fin
                FROM "Curso" c
                ORDER BY c.nombre
            '''))
            
            print("✅ Conexión BD exitosa!")
            print("\n📚 Cursos encontrados en la BD:")
            
            count = 0
            for row in result:
                count += 1
                print(f"  {count}. {row[1]} (ID: {row[0]})")
                print(f"     📝 Descripción: {row[2] or 'Sin descripción'}")
                print(f"     🎓 Modalidad: {row[3] or 'No especificada'}")
                print(f"     📅 Fechas: {row[4]} → {row[5]}")
                print("")
            
            print(f"🎯 Total de cursos reales en BD: {count}")
            
        finally:
            db.close()
            
        return count > 0
        
    except Exception as e:
        print(f"❌ Error de BD: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Prueba directa de consulta BD (sin FastAPI)...")
    print("=" * 55)
    
    success = test_database_query()
    
    print("=" * 55)
    if success:
        print("✅ ¡Consulta BD exitosa! Los datos son reales.")
    else:
        print("❌ Error en consulta BD.")