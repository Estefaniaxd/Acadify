#!/usr/bin/env python3
"""
Script para sincronizar assets de avatars con la base de datos.
Escanea la carpeta de assets y actualiza la tabla avatar_asset.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any
from sqlalchemy.orm import Session

# Añadir el directorio src al path para importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.db.session import SessionLocal
from src.models.avatar.avatar_asset import AvatarAsset
from src.crud.avatar.avatar_asset_crud import crud_avatar_asset
from src.utils.image_utils import validate_asset_file, generate_manifest, save_manifest
from src.core.config import settings


def get_db():
    """Obtiene sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def scan_assets_directory(assets_dir: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Escanea el directorio de assets y retorna información organizada.
    
    Args:
        assets_dir: Directorio de assets
        
    Returns:
        Dict con categorías y archivos
    """
    assets_info = {}
    
    if not os.path.exists(assets_dir):
        print(f"Warning: Assets directory not found: {assets_dir}")
        return assets_info
    
    print(f"Scanning assets directory: {assets_dir}")
    
    for category_path in Path(assets_dir).iterdir():
        if category_path.is_dir() and not category_path.name.startswith('.'):
            category = category_path.name
            files = []
            
            print(f"  Scanning category: {category}")
            
            for file_path in category_path.glob('*.png'):
                try:
                    # Validar archivo
                    validation = validate_asset_file(str(file_path))
                    
                    file_info = {
                        'filename': f"{category}/{file_path.name}",
                        'display_name': file_path.stem.replace('_', ' ').title(),
                        'file_size': validation['size'],
                        'width': validation['dimensions'][0],
                        'height': validation['dimensions'][1],
                        'metadata': {
                            'format': validation['format'],
                            'has_transparency': validation['has_transparency'],
                            'mode': validation['mode']
                        }
                    }
                    
                    files.append(file_info)
                    
                except Exception as e:
                    print(f"    Warning: Skipping invalid file {file_path}: {e}")
                    continue
            
            if files:
                assets_info[category] = files
                print(f"    Found {len(files)} valid assets")
    
    return assets_info


def sync_assets_to_database(db: Session, assets_info: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
    """
    Sincroniza assets con la base de datos.
    
    Args:
        db: Sesión de base de datos
        assets_info: Información de assets escaneados
        
    Returns:
        Estadísticas de sincronización
    """
    stats = {
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    print("Synchronizing assets with database...")
    
    for category, files in assets_info.items():
        print(f"  Processing category: {category}")
        
        for file_info in files:
            try:
                filename = file_info['filename']
                
                # Verificar si ya existe
                existing_asset = crud_avatar_asset.get_by_filename(db, filename=filename)
                
                if existing_asset:
                    # Actualizar solo si hay cambios
                    update_data = {}
                    
                    if existing_asset.display_name != file_info['display_name']:
                        update_data['display_name'] = file_info['display_name']
                    
                    if existing_asset.file_size != file_info['file_size']:
                        update_data['file_size'] = file_info['file_size']
                    
                    if existing_asset.width != file_info['width']:
                        update_data['width'] = file_info['width']
                    
                    if existing_asset.height != file_info['height']:
                        update_data['height'] = file_info['height']
                    
                    if existing_asset.metadata != file_info['metadata']:
                        update_data['metadata'] = file_info['metadata']
                    
                    if update_data:
                        crud_avatar_asset.update(db, db_obj=existing_asset, obj_in=update_data)
                        print(f"    Updated: {filename}")
                        stats['updated'] += 1
                    else:
                        stats['skipped'] += 1
                else:
                    # Crear nuevo asset
                    asset_data = {
                        'category': category,
                        'filename': filename,
                        'display_name': file_info['display_name'],
                        'file_size': file_info['file_size'],
                        'width': file_info['width'],
                        'height': file_info['height'],
                        'metadata': file_info['metadata'],
                        'is_active': 'Y'
                    }
                    
                    crud_avatar_asset.create(db, obj_in=asset_data)
                    print(f"    Created: {filename}")
                    stats['created'] += 1
                
            except Exception as e:
                print(f"    Error processing {file_info.get('filename', 'unknown')}: {e}")
                stats['errors'] += 1
    
    db.commit()
    return stats


def cleanup_orphaned_assets(db: Session, assets_info: Dict[str, List[Dict[str, Any]]]) -> int:
    """
    Marca como inactivos los assets que ya no existen en el directorio.
    
    Args:
        db: Sesión de base de datos
        assets_info: Información de assets actuales
        
    Returns:
        Número de assets marcados como inactivos
    """
    print("Checking for orphaned assets...")
    
    # Obtener lista de filenames actuales
    current_filenames = set()
    for files in assets_info.values():
        for file_info in files:
            current_filenames.add(file_info['filename'])
    
    # Obtener assets activos de la DB
    active_assets = crud_avatar_asset.get_multi(db, skip=0, limit=10000)
    orphaned_count = 0
    
    for asset in active_assets:
        if asset.is_active == 'Y' and asset.filename not in current_filenames:
            # Marcar como inactivo
            crud_avatar_asset.update(db, db_obj=asset, obj_in={'is_active': 'N'})
            print(f"  Marked as inactive: {asset.filename}")
            orphaned_count += 1
    
    if orphaned_count > 0:
        db.commit()
    
    return orphaned_count


async def main():
    """Función principal del script."""
    print("=== Avatar Assets Sync ===")
    print(f"Assets directory: {settings.AVATAR_ASSETS_PATH}")
    print(f"Database URL: {settings.DATABASE_URL}")
    print()
    
    # Escanear directorio de assets
    assets_info = scan_assets_directory(settings.AVATAR_ASSETS_PATH)
    
    if not assets_info:
        print("No assets found. Please check the assets directory.")
        return
    
    # Mostrar resumen
    total_files = sum(len(files) for files in assets_info.values())
    print(f"\nFound {len(assets_info)} categories with {total_files} total assets:")
    for category, files in assets_info.items():
        print(f"  {category}: {len(files)} files")
    
    # Conectar a la base de datos
    db = SessionLocal()
    try:
        # Sincronizar con la base de datos
        print("\n" + "="*50)
        sync_stats = sync_assets_to_database(db, assets_info)
        
        # Limpiar assets huérfanos
        print("\n" + "="*50)
        orphaned_count = cleanup_orphaned_assets(db, assets_info)
        
        # Generar manifest
        print("\n" + "="*50)
        print("Generating manifest.json...")
        manifest = await generate_manifest(settings.AVATAR_ASSETS_PATH)
        manifest_path = os.path.join(settings.AVATAR_ASSETS_PATH, "manifest.json")
        await save_manifest(manifest, manifest_path)
        print(f"Manifest saved to: {manifest_path}")
        
        # Mostrar estadísticas finales
        print("\n" + "="*50)
        print("SYNC COMPLETED")
        print(f"Created: {sync_stats['created']} assets")
        print(f"Updated: {sync_stats['updated']} assets")
        print(f"Skipped: {sync_stats['skipped']} assets")
        print(f"Errors: {sync_stats['errors']} assets")
        print(f"Orphaned: {orphaned_count} assets marked inactive")
        print("="*50)
        
    except Exception as e:
        print(f"Error during sync: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())