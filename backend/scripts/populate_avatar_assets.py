#!/usr/bin/env python3
"""
Script para poblar la tabla avatar_asset con los assets existentes
"""
import os
import sys
from pathlib import Path
from PIL import Image
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
STATIC_DIR = Path(__file__).parent / "static" / "assets"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:243019@localhost:5432/acadify_db")

# Mapeo de carpetas a categorías
CATEGORY_MAPPING = {
    "base": "base",
    "eyes": "eyes",
    "hair": "hair",
    "clothes": "clothes",
    "makeup": "makeup",
    "mounth": "mouth",  # Nota: typo en el nombre de carpeta, pero lo mapeamos correctamente
    "backgrounds": "background",
    "accessories": "accessories"
}

# Mapeo de subcarpetas de base a género
GENDER_MAPPING = {
    "base-man": "male",
    "base-woman": "female"
}

def get_image_dimensions(image_path):
    """Obtener dimensiones de una imagen"""
    try:
        with Image.open(image_path) as img:
            return img.size  # (width, height)
    except Exception as e:
        print(f"❌ Error al leer {image_path}: {e}")
        return (512, 512)  # Dimensiones por defecto

def scan_assets():
    """Escanear directorio de assets y recopilar información"""
    assets = []
    
    for folder_name, category in CATEGORY_MAPPING.items():
        folder_path = STATIC_DIR / folder_name
        
        if not folder_path.exists():
            print(f"⚠️  Carpeta no encontrada: {folder_path}")
            continue
        
        print(f"📁 Escaneando {folder_name}/ ({category})...")
        
        # Para la carpeta base, necesitamos procesar las subcarpetas
        if folder_name == "base":
            for gender_folder in folder_path.iterdir():
                if gender_folder.is_dir():
                    gender = GENDER_MAPPING.get(gender_folder.name, "unisex")
                    
                    for image_file in gender_folder.glob("*.png"):
                        width, height = get_image_dimensions(image_file)
                        file_size = image_file.stat().st_size
                        
                        # Construir el path relativo desde static/
                        relative_path = f"assets/{folder_name}/{gender_folder.name}/{image_file.name}"
                        
                        display_name = image_file.stem.replace("_", " ").replace("-", " ").title()
                        
                        assets.append({
                            "category": category,
                            "filename": relative_path,
                            "display_name": display_name,
                            "file_size": file_size,
                            "width": width,
                            "height": height,
                            "target_gender": gender,
                            "meta_info": f'{{"path": "{relative_path}", "original_name": "{image_file.name}"}}'
                        })
                        
                        print(f"  ✓ {image_file.name} ({width}x{height}, {file_size} bytes, {gender})")
        else:
            # Para otras categorías, procesar directamente
            target_gender = "unisex"
            
            # Detectar género por el nombre de la categoría o archivos
            if "woman" in folder_name or "female" in folder_name:
                target_gender = "female"
            elif "man" in folder_name or "male" in folder_name:
                target_gender = "male"
            
            for image_file in folder_path.glob("*.png"):
                width, height = get_image_dimensions(image_file)
                file_size = image_file.stat().st_size
                
                # Construir el path relativo desde static/
                relative_path = f"assets/{folder_name}/{image_file.name}"
                
                display_name = image_file.stem.replace("_", " ").replace("-", " ").title()
                
                assets.append({
                    "category": category,
                    "filename": relative_path,
                    "display_name": display_name,
                    "file_size": file_size,
                    "width": width,
                    "height": height,
                    "target_gender": target_gender,
                    "meta_info": f'{{"path": "{relative_path}", "original_name": "{image_file.name}"}}'
                })
                
                print(f"  ✓ {image_file.name} ({width}x{height}, {file_size} bytes)")
    
    return assets

def insert_assets(assets):
    """Insertar assets en la base de datos"""
    if not assets:
        print("⚠️  No hay assets para insertar")
        return
    
    try:
        # Parsear DATABASE_URL
        # Formato: postgresql://usuario:password@host:puerto/database
        url_parts = DATABASE_URL.replace("postgresql://", "").split("/")
        db_name = url_parts[1]
        user_pass_host = url_parts[0].split("@")
        user_pass = user_pass_host[0].split(":")
        host_port = user_pass_host[1].split(":")
        
        conn = psycopg2.connect(
            dbname=db_name,
            user=user_pass[0],
            password=user_pass[1],
            host=host_port[0],
            port=host_port[1]
        )
        
        cursor = conn.cursor()
        
        print(f"\n💾 Insertando {len(assets)} assets en la base de datos...")
        
        # Preparar datos para inserción
        insert_query = """
            INSERT INTO avatar_asset (
                category, filename, display_name, file_size, 
                width, height, target_gender, meta_info, is_active
            ) VALUES %s
            ON CONFLICT (filename) DO UPDATE SET
                category = EXCLUDED.category,
                display_name = EXCLUDED.display_name,
                file_size = EXCLUDED.file_size,
                width = EXCLUDED.width,
                height = EXCLUDED.height,
                target_gender = EXCLUDED.target_gender,
                meta_info = EXCLUDED.meta_info,
                is_active = EXCLUDED.is_active,
                updated_at = NOW()
        """
        
        values = [
            (
                asset["category"],
                asset["filename"],
                asset["display_name"],
                asset["file_size"],
                asset["width"],
                asset["height"],
                asset["target_gender"],
                asset["meta_info"],
                "Y"
            )
            for asset in assets
        ]
        
        execute_values(cursor, insert_query, values)
        conn.commit()
        
        print(f"✅ {len(assets)} assets insertados correctamente")
        
        # Verificar
        cursor.execute("SELECT category, COUNT(*) FROM avatar_asset GROUP BY category ORDER BY category")
        results = cursor.fetchall()
        
        print("\n📊 Assets por categoría:")
        for category, count in results:
            print(f"  • {category}: {count} assets")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al insertar en la base de datos: {e}")
        sys.exit(1)

def main():
    print("=" * 60)
    print("🎨 POPULATE AVATAR ASSETS")
    print("=" * 60)
    print()
    
    if not STATIC_DIR.exists():
        print(f"❌ Directorio de assets no encontrado: {STATIC_DIR}")
        sys.exit(1)
    
    print(f"📂 Directorio de assets: {STATIC_DIR}")
    print(f"🔗 Base de datos: {DATABASE_URL.split('@')[1]}")  # Ocultar password
    print()
    
    # Escanear assets
    assets = scan_assets()
    
    print(f"\n✨ Total assets encontrados: {len(assets)}")
    
    if assets:
        # Insertar en DB
        insert_assets(assets)
    
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
