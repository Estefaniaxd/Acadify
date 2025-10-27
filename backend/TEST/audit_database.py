#!/usr/bin/env python3
"""
Script para verificar estructura real de la base de datos
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuración de base de datos desde el .env real
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'acadify_db',
    'user': 'postgres',
    'password': '243019'
}

def check_database_structure():
    """Verificar estructura completa de la BD"""
    try:
        # Intentar conexión
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 VERIFICANDO ESTRUCTURA DE BASE DE DATOS")
        print("=" * 60)
        
        # 1. Verificar tabla Comentario
        print("\n📝 TABLA COMENTARIO:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'Comentario'
            ORDER BY ordinal_position
        """)
        
        comentario_columns = cursor.fetchall()
        if comentario_columns:
            for col in comentario_columns:
                print(f"   - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        else:
            print("   ❌ Tabla Comentario no existe")
        
        # 2. Verificar tabla Reacciones
        print("\n🎭 TABLA REACCIONES:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'Reacciones'
            ORDER BY ordinal_position
        """)
        
        reacciones_columns = cursor.fetchall()
        if reacciones_columns:
            for col in reacciones_columns:
                print(f"   - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        else:
            print("   ❌ Tabla Reacciones no existe")
        
        # 3. Verificar comentarios con archivos
        print("\n📎 COMENTARIOS CON ARCHIVOS:")
        cursor.execute("""
            SELECT comentario_id, contenido, archivos_adjuntos, fecha_creacion
            FROM "Comentario" 
            WHERE archivos_adjuntos IS NOT NULL 
            AND archivos_adjuntos::text != 'null'
            AND archivos_adjuntos::text != '[]'
            ORDER BY fecha_creacion DESC
            LIMIT 3
        """)
        
        comments_with_files = cursor.fetchall()
        if comments_with_files:
            for comment in comments_with_files:
                print(f"   - ID: {comment['comentario_id']}")
                print(f"     Contenido: {comment['contenido'][:50]}...")
                print(f"     Archivos: {comment['archivos_adjuntos']}")
                print(f"     Fecha: {comment['fecha_creacion']}")
                print()
        else:
            print("   ⚠️ No hay comentarios con archivos")
        
        # 4. Verificar reacciones existentes
        print("\n🎯 REACCIONES EXISTENTES:")
        try:
            cursor.execute("""
                SELECT emoji, COUNT(*) as cantidad
                FROM "Reacciones" 
                GROUP BY emoji
                ORDER BY cantidad DESC
                LIMIT 5
            """)
            
            reacciones = cursor.fetchall()
            if reacciones:
                for reaccion in reacciones:
                    print(f"   - {reaccion['emoji']}: {reaccion['cantidad']} veces")
            else:
                print("   ⚠️ No hay reacciones registradas")
        except Exception as e:
            print(f"   ❌ Error consultando reacciones: {e}")
        
        # 5. Verificar usuarios y comentarios recientes
        print("\n👤 ACTIVIDAD RECIENTE:")
        cursor.execute("""
            SELECT c.comentario_id, c.contenido, u.nombres, u.apellidos, c.fecha_creacion
            FROM "Comentario" c
            JOIN "Usuario" u ON c.autor_id = u.usuario_id
            ORDER BY c.fecha_creacion DESC
            LIMIT 3
        """)
        
        recent_activity = cursor.fetchall()
        if recent_activity:
            for activity in recent_activity:
                print(f"   - {activity['nombres']} {activity['apellidos']}: {activity['contenido'][:30]}...")
                print(f"     ID: {activity['comentario_id']} | {activity['fecha_creacion']}")
        else:
            print("   ⚠️ No hay actividad reciente")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Verificación de BD completada")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error de conexión a PostgreSQL: {e}")
        print("\n🔧 POSIBLES SOLUCIONES:")
        print("1. Verificar que PostgreSQL esté ejecutándose")
        print("2. Ajustar credenciales en DB_CONFIG")
        print("3. Verificar nombre de la base de datos")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def check_filesystem_uploads():
    """Verificar archivos en el sistema"""
    print("\n📁 VERIFICANDO SISTEMA DE ARCHIVOS:")
    print("-" * 40)
    
    uploads_dir = "/home/esteban/Acadify/backend/static/uploads/cursos"
    
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        print(f"✅ Directorio existe: {uploads_dir}")
        print(f"📊 Archivos encontrados: {len(files)}")
        
        for i, f in enumerate(files[:5], 1):
            file_path = os.path.join(uploads_dir, f)
            size = os.path.getsize(file_path)
            print(f"   {i}. {f} ({size:,} bytes)")
        
        if len(files) > 5:
            print(f"   ... y {len(files) - 5} archivos más")
            
        return len(files) > 0
    else:
        print(f"❌ Directorio no existe: {uploads_dir}")
        return False

if __name__ == "__main__":
    print("🚀 AUDITORÍA COMPLETA DEL SISTEMA")
    print("=" * 60)
    
    db_ok = check_database_structure()
    fs_ok = check_filesystem_uploads()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL:")
    print(f"   Base de datos: {'✅ OK' if db_ok else '❌ ERROR'}")
    print(f"   Sistema archivos: {'✅ OK' if fs_ok else '❌ ERROR'}")
    
    if not db_ok:
        print("\n⚠️ ACCIÓN REQUERIDA:")
        print("1. Verificar conexión a PostgreSQL")
        print("2. Ejecutar migraciones si es necesario")
        print("3. Verificar tablas Comentario y Reacciones")