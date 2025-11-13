#!/usr/bin/env python3
"""
Script para ejecutar el SQL de creación de tablas de videollamadas.
Lee la configuración de .env y ejecuta el script SQL.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from psycopg2 import sql
from src.core.config import settings

def main():
    """Ejecutar el script SQL de videollamadas."""
    
    print("=" * 80)
    print("🚀 Creación de Tablas de Videollamadas con Jitsi Meet")
    print("=" * 80)
    print()
    
    # Leer el script SQL
    sql_file = Path(__file__).parent / "create_videollamadas_tables.sql"
    if not sql_file.exists():
        print(f"❌ Error: No se encuentra el archivo {sql_file}")
        return 1
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    print(f"📄 Script SQL cargado: {sql_file}")
    print(f"📊 Base de datos: {settings.POSTGRES_DB}")
    print(f"🔗 Host: {settings.POSTGRES_HOST}")
    print(f"👤 Usuario: {settings.POSTGRES_USER}")
    print()
    
    try:
        # Conectar a la base de datos
        print("⏳ Conectando a la base de datos...")
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("✅ Conexión establecida")
        print()
        print("⏳ Ejecutando script SQL...")
        print("-" * 80)
        
        # Ejecutar el script
        cursor.execute(sql_script)
        
        # Obtener resultado de verificación
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE table_name = 'videollamadas') AS videollamadas,
                COUNT(*) FILTER (WHERE table_name = 'videollamadas_participantes') AS participantes,
                COUNT(*) FILTER (WHERE table_name = 'videollamadas_grabaciones') AS grabaciones
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name IN ('videollamadas', 'videollamadas_participantes', 'videollamadas_grabaciones');
        """)
        
        result = cursor.fetchone()
        
        # Commit
        conn.commit()
        print("-" * 80)
        print("✅ Script ejecutado exitosamente!")
        print()
        print("📊 Tablas creadas:")
        print(f"   ✓ videollamadas: {'✅' if result[0] > 0 else '❌'}")
        print(f"   ✓ videollamadas_participantes: {'✅' if result[1] > 0 else '❌'}")
        print(f"   ✓ videollamadas_grabaciones: {'✅' if result[2] > 0 else '❌'}")
        print()
        
        # Listar funciones creadas
        cursor.execute("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = 'public' 
              AND routine_name IN ('finalizar_videollamada', 'get_estadisticas_videollamada');
        """)
        
        functions = cursor.fetchall()
        if functions:
            print("🔧 Funciones creadas:")
            for func in functions:
                print(f"   ✓ {func[0]}()")
            print()
        
        # Listar vistas creadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' 
              AND table_name = 'videollamadas_activas';
        """)
        
        views = cursor.fetchall()
        if views:
            print("👁️  Vistas creadas:")
            for view in views:
                print(f"   ✓ {view[0]}")
            print()
        
        cursor.close()
        conn.close()
        
        print("=" * 80)
        print("🎉 Base de datos lista para videollamadas con Jitsi Meet!")
        print("=" * 80)
        print()
        print("📝 Próximos pasos:")
        print("   1. Verificar endpoints de API en src/api/routes/communication/videollamadas.py")
        print("   2. Probar CRUD operations con scripts/test_crud_videollamadas.py")
        print("   3. Integrar frontend con Jitsi Meet IFrame API")
        print()
        
        return 0
        
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        if conn:
            conn.rollback()
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if conn:
            conn.rollback()
        return 1
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    sys.exit(main())
