#!/usr/bin/env python3
"""
Script para poblar la base de datos con los assets de avatars existentes.
"""

import os
import sys
from pathlib import Path
from PIL import Image

# Agregar el directorio padre al PYTHONPATH
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.models.avatar.avatar_asset import AvatarAsset


def validate_asset_file_sync(file_path: str) -> dict:
    """Versión síncrona de validate_asset_file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Asset file not found: {file_path}")
    
    file_size = os.path.getsize(file_path)
    MAX_FILE_SIZE = 1024 * 1024 * 5  # 5MB para ser más permisivo
    
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {file_size} bytes")
    
    try:
        with Image.open(file_path) as img:
            # Validar formato
            if img.format not in {'PNG', 'JPEG'}:
                raise ValueError(f"Unsupported format: {img.format}")
            
            has_transparency = 'transparency' in img.info or img.mode in ('RGBA', 'LA')
            
            return {
                'valid': True,
                'size': file_size,
                'format': img.format,
                'dimensions': img.size,
                'has_transparency': has_transparency,
                'mode': img.mode,
                'matches_standard': img.size == (512, 512)
            }
            
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}")


def clean_filename(filename: str) -> str:
    """Limpia el nombre del archivo para hacerlo más legible."""
    # Remover extensión
    name = os.path.splitext(filename)[0]
    
    # Reemplazar espacios y caracteres especiales
    name = name.replace(' ', '_')
    name = name.replace('(', '')
    name = name.replace(')', '')
    name = name.replace('WhatsApp_Image_2025-09-22_at_11.19.', '')
    name = name.replace('11_PM', '')
    name = name.replace('_', ' ')
    
    # Capitalizar cada palabra
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name or "Asset"


def get_gender_from_path(filepath: str) -> str:
    """Determina el género basado en la ruta del archivo."""
    path_parts = filepath.split('/')
    
    for part in path_parts:
        if part == 'male':
            return 'male'
        elif part == 'female' or part == 'famale':  # Typo en la carpeta
            return 'female'
        elif part == 'unisex':
            return 'unisex'
    
    return 'unisex'  # Default


def get_category_from_path(filepath: str) -> str:
    """Determina la categoría basada en la ruta del archivo."""
    path_parts = filepath.split('/')
    
    for part in ['base', 'hair', 'clothes', 'eyes', 'accessories', 'backgrounds']:
        if part in path_parts:
            return part
    
    return 'accessories'  # Default


def populate_avatar_assets():
    """Pobla la base de datos con los assets encontrados."""
    db = SessionLocal()
    
    try:
        assets_dir = "static/assets"
        added_count = 0
        
        # Limpiar assets existentes (opcional)
        # db.query(AvatarAsset).delete()
        
        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                # Solo procesar imágenes
                if not (file.lower().endswith('.png') or 
                       file.lower().endswith('.jpeg') or 
                       file.lower().endswith('.jpg')):
                    continue
                
                # Saltar archivos de sistema
                if file.startswith('.') or file == 'manifest.json':
                    continue
                
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, assets_dir)
                
                try:
                    # Validar el archivo
                    validation_info = validate_asset_file_sync(full_path)
                    
                    # Determinar categoría y género
                    category = get_category_from_path(relative_path)
                    target_gender = get_gender_from_path(relative_path)
                    
                    # Generar display name
                    display_name = clean_filename(file)
                    
                    # Verificar si ya existe
                    existing = db.query(AvatarAsset).filter(
                        AvatarAsset.filename == relative_path
                    ).first()
                    
                    if existing:
                        print(f"⚠️  Ya existe: {relative_path}")
                        continue
                    
                    # Crear nuevo asset
                    asset = AvatarAsset(
                        category=category,
                        filename=relative_path,
                        display_name=display_name,
                        target_gender=target_gender,
                        file_size=validation_info['size'],
                        width=validation_info['dimensions'][0],
                        height=validation_info['dimensions'][1],
                        meta_info={
                            'format': validation_info['format'],
                            'has_transparency': validation_info['has_transparency']
                        }
                    )
                    
                    db.add(asset)
                    added_count += 1
                    
                    print(f"✅ Agregado: {category}/{target_gender} - {display_name} ({relative_path})")
                    
                except Exception as e:
                    print(f"❌ Error procesando {full_path}: {e}")
                    continue
        
        # Guardar cambios
        db.commit()
        print(f"\n🎉 ¡Proceso completado! {added_count} assets agregados a la base de datos.")
        
        # Mostrar resumen
        print("\n📊 Resumen por categoría:")
        categories = db.query(AvatarAsset.category, AvatarAsset.target_gender).distinct().all()
        for category, gender in categories:
            count = db.query(AvatarAsset).filter(
                AvatarAsset.category == category,
                AvatarAsset.target_gender == gender
            ).count()
            print(f"  {category}/{gender}: {count} assets")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Poblando base de datos con assets de avatars...")
    populate_avatar_assets()