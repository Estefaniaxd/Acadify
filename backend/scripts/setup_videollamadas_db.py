#!/usr/bin/env python3
"""
Script simple para ejecutar SQL de videollamadas.
Intenta conectar con usuario 'postgres' por defecto.
"""

import sys
import os
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("❌ Error: psycopg2 no está instalado")
    print("   Instala con: pip install psycopg2-binary")
    sys.exit(1)

def main():
    """Ejecutar el script SQL de videollamadas."""
    
    print("=" * 80)
    print("🚀 Creación de Tablas de Videollamadas con Jitsi Meet")
    print("=" * 80)
    print()
    
    # Configuración de BD (ajustar según necesidad)
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'acadify_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }
    
    print("📊 Configuración de conexión:")
    print(f"   Host: {db_config['host']}")
    print(f"   Puerto: {db_config['port']}")
    print(f"   Base de datos: {db_config['database']}")
    print(f"   Usuario: {db_config['user']}")
    print()
    print("💡 Tip: Puedes cambiar estos valores con variables de entorno:")
    print("   DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
    print()
    
    # Leer el script SQL
    sql_file = Path(__file__).parent / "create_videollamadas_tables.sql"
    if not sql_file.exists():
        print(f"❌ Error: No se encuentra el archivo {sql_file}")
        return 1
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    print(f"📄 Script SQL cargado ({len(sql_script)} caracteres)")
    print()
    
    conn = None
    cursor = None
    
    try:
        # Conectar a la base de datos
        print("⏳ Conectando a la base de datos...")
        conn = psycopg2.connect(**db_config)
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("✅ Conexión establecida")
        print()
        print("⏳ Ejecutando script SQL...")
        print("-" * 80)
        
        # Ejecutar el script
        cursor.execute(sql_script)
        
        # Verificar tablas creadas
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
              AND routine_name IN ('finalizar_videollamada', 'get_estadisticas_videollamada', 'actualizar_duracion_participante');
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
        
        # Listar ENUMs creados
        cursor.execute("""
            SELECT typname 
            FROM pg_type 
            WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
              AND typname IN ('tipo_llamada', 'estado_videollamada', 'calidad_conexion', 
                             'formato_grabacion', 'calidad_grabacion', 'estado_procesamiento');
        """)
        
        enums = cursor.fetchall()
        if enums:
            print("🏷️  ENUMs creados:")
            for enum in enums:
                print(f"   ✓ {enum[0]}")
            print()
        
        print("=" * 80)
        print("🎉 Base de datos lista para videollamadas con Jitsi Meet!")
        print("=" * 80)
        print()
        print("📝 Próximos pasos:")
        print("   1. Verificar CRUD: python scripts/test_crud_videollamadas.py")
        print("   2. Revisar API endpoints: src/api/routes/communication/videollamadas.py")
        print("   3. Integrar frontend con Jitsi Meet IFrame API")
        print("   4. Configurar JWT: src/utils/jitsi_jwt.py")
        print()
        
        return 0
        
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        print()
        print("💡 Posibles soluciones:")
        print("   1. Verifica que PostgreSQL esté ejecutándose: sudo systemctl status postgresql")
        print("   2. Verifica usuario/contraseña en variables de entorno")
        print("   3. Crea la base de datos si no existe: createdb acadify_db")
        print()
        if conn:
            conn.rollback()
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if conn:
            conn.rollback()
        return 1
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    sys.exit(main())
