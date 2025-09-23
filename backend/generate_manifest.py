#!/usr/bin/env python3
"""
Script para generar manifest.json automáticamente desde la carpeta de assets.
Uso: python generate_manifest.py [--normalize] [--assets-dir path] [--output path]
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path

# Añadir src al path para importar utils
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.image_utils import (
    generate_manifest, 
    save_manifest, 
    normalize_all_assets,
    validate_asset_file
)


async def main():
    parser = argparse.ArgumentParser(description='Generate avatar assets manifest')
    parser.add_argument('--assets-dir', default='static/assets', 
                       help='Assets directory path (default: static/assets)')
    parser.add_argument('--output', default='static/assets/manifest.json',
                       help='Output manifest path (default: static/assets/manifest.json)')
    parser.add_argument('--normalize', action='store_true',
                       help='Normalize all assets to standard resolution')
    parser.add_argument('--validate', action='store_true',
                       help='Validate all assets and report issues')
    
    args = parser.parse_args()
    
    assets_dir = os.path.abspath(args.assets_dir)
    output_path = os.path.abspath(args.output)
    
    print(f"🔍 Scanning assets directory: {assets_dir}")
    
    if not os.path.exists(assets_dir):
        print(f"❌ Assets directory not found: {assets_dir}")
        print("Creating basic structure...")
        
        # Crear estructura básica
        categories = ['base', 'hair', 'eyes', 'clothes', 'accessories', 'backgrounds']
        for category in categories:
            category_path = os.path.join(assets_dir, category)
            os.makedirs(category_path, exist_ok=True)
            print(f"   📁 Created: {category}/")
        
        print("\n💡 Please add PNG assets to the category folders and run this script again.")
        return
    
    # Validar assets si se solicita
    if args.validate:
        print("\n🔍 Validating all assets...")
        validation_report = validate_all_assets(assets_dir)
        print_validation_report(validation_report)
    
    # Normalizar assets si se solicita
    if args.normalize:
        print("\n🔧 Normalizing assets to standard resolution...")
        normalized_dir = os.path.join(assets_dir, 'normalized')
        normalize_report = await normalize_all_assets(assets_dir, normalized_dir)
        print_normalize_report(normalize_report)
    
    # Generar manifest
    print("\n📋 Generating manifest...")
    manifest = generate_manifest(assets_dir)
    
    # Guardar manifest
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    await save_manifest(manifest, output_path)
    
    # Mostrar reporte
    print(f"\n✅ Manifest generated successfully!")
    print(f"   📄 Output: {output_path}")
    print(f"   📦 Total categories: {len(manifest['categories'])}")
    print(f"   🖼️  Total assets: {manifest['total_assets']}")
    print(f"   📐 Standard resolution: {manifest['resolution'][0]}×{manifest['resolution'][1]}")
    
    if manifest['categories']:
        print("\n📁 Categories found:")
        for category, files in manifest['categories'].items():
            print(f"   • {category}: {len(files)} files")
            
            # Mostrar archivos que necesitan normalización
            non_standard = [f for f in files if not f['normalized']]
            if non_standard:
                print(f"     ⚠️  {len(non_standard)} files need normalization")
    else:
        print("\n⚠️  No valid assets found. Please add PNG files to category folders.")


def validate_all_assets(assets_dir: str) -> dict:
    """Valida todos los assets y retorna un reporte."""
    report = {
        'total': 0,
        'valid': 0,
        'invalid': 0,
        'errors': [],
        'warnings': []
    }
    
    for category_path in Path(assets_dir).iterdir():
        if category_path.is_dir() and category_path.name != 'normalized':
            for file_path in category_path.glob('*'):
                if file_path.is_file():
                    report['total'] += 1
                    
                    try:
                        if file_path.suffix.lower() != '.png':
                            report['warnings'].append(f"Non-PNG file: {file_path}")
                            continue
                            
                        validation = validate_asset_file(str(file_path))
                        if validation['valid']:
                            report['valid'] += 1
                            if not validation['matches_standard']:
                                report['warnings'].append(f"Non-standard size: {file_path} ({validation['dimensions']})")
                        else:
                            report['invalid'] += 1
                            
                    except Exception as e:
                        report['invalid'] += 1
                        report['errors'].append(f"Error validating {file_path}: {str(e)}")
    
    return report


def print_validation_report(report: dict):
    """Imprime el reporte de validación."""
    print(f"   📊 Validation results:")
    print(f"      Total files: {report['total']}")
    print(f"      Valid: {report['valid']}")
    print(f"      Invalid: {report['invalid']}")
    
    if report['warnings']:
        print(f"   ⚠️  Warnings ({len(report['warnings'])}):")
        for warning in report['warnings'][:5]:  # Mostrar solo las primeras 5
            print(f"      • {warning}")
        if len(report['warnings']) > 5:
            print(f"      ... and {len(report['warnings']) - 5} more")
    
    if report['errors']:
        print(f"   ❌ Errors ({len(report['errors'])}):")
        for error in report['errors'][:3]:  # Mostrar solo los primeros 3
            print(f"      • {error}")
        if len(report['errors']) > 3:
            print(f"      ... and {len(report['errors']) - 3} more")


def print_normalize_report(report: dict):
    """Imprime el reporte de normalización."""
    print(f"   📊 Normalization results:")
    print(f"      Processed: {report['processed']}")
    print(f"      Normalized: {report['normalized']}")
    print(f"      Skipped (already standard): {report['skipped']}")
    
    if report['errors']:
        print(f"   ❌ Errors ({len(report['errors'])}):")
        for error in report['errors'][:3]:
            print(f"      • {error}")
        if len(report['errors']) > 3:
            print(f"      ... and {len(report['errors']) - 3} more")


if __name__ == "__main__":
    asyncio.run(main())