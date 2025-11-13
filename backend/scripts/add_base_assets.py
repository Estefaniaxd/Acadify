#!/usr/bin/env python3
"""Script para agregar los assets base adicionales que están directamente en /base/"""

import os
import psycopg2
from psycopg2.extras import execute_values
from PIL import Image

# Configuración
DB_CONFIG = {
    "dbname": "acadify_db",
    "user": "postgres",
    "password": "243019",
    "host": "localhost",
    "port": "5432"
}

ASSETS_DIR = "static/assets"

def process_base_files():
    """Procesar archivos en /base/ directamente"""
    base_dir = os.path.join(ASSETS_DIR, "base")
    assets = []
    
    # Procesar archivos directamente en /base/
    for filename in os.listdir(base_dir):
        filepath = os.path.join(base_dir, filename)
        
        # Solo archivos PNG/JPG
        if not os.path.isfile(filepath):
            continue
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
            
        # Determinar género por el nombre del archivo
        filename_lower = filename.lower()
        if 'male' in filename_lower and 'female' not in filename_lower:
            target_gender = 'male'
        elif 'female' in filename_lower:
            target_gender = 'female'
        else:
            # Si no tiene indicador, marcar como unisex
            target_gender = 'unisex'
        
        # Obtener dimensiones
        try:
            with Image.open(filepath) as img:
                width, height = img.size
        except Exception as e:
            print(f"⚠️  Error leyendo {filename}: {e}")
            continue
        
        file_size = os.path.getsize(filepath)
        
        # Ruta relativa desde static/assets/
        rel_path = f"base/{filename}"
        
        # Display name
        display_name = filename.replace('_', ' ').replace('.png', '').replace('.jpg', '').title()
        
        assets.append((
            'base',
            rel_path,
            display_name,
            file_size,
            width,
            height,
            target_gender,
            'Y'
        ))
        
        print(f"  📄 {filename} -> {target_gender}")
    
    return assets

# Conectar a la base de datos
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

print("🔄 Procesando archivos base adicionales...")
assets = process_base_files()

if assets:
    # Insertar en la base de datos
    insert_query = """
    INSERT INTO avatar_asset (
        category, filename, display_name, file_size, width, height, 
        target_gender, is_active
    ) VALUES %s
    ON CONFLICT (filename) DO UPDATE SET
        display_name = EXCLUDED.display_name,
        file_size = EXCLUDED.file_size,
        width = EXCLUDED.width,
        height = EXCLUDED.height,
        target_gender = EXCLUDED.target_gender;
    """
    
    execute_values(cur, insert_query, assets)
    conn.commit()
    
    print(f"\n✅ Insertados/Actualizados {len(assets)} assets base adicionales")
else:
    print("⚠️  No se encontraron archivos base adicionales")

cur.close()
conn.close()
