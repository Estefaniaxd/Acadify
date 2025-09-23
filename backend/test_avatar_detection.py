#!/usr/bin/env python3
"""
Script para verificar que el sistema de avatars detecta correctamente 
las imágenes organizadas en la nueva estructura de carpetas.
"""
import sys
import os

# Agregar el directorio src al PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.avatar_service import AvatarService
from src.core.config import settings
import asyncio

async def test_asset_detection():
    """
    Prueba que el AvatarService detecte correctamente todas las imágenes
    organizadas en la nueva estructura de carpetas.
    """
    print("🔍 Probando detección de assets en nueva estructura...")
    print(f"📁 Directorio de assets: {settings.AVATAR_ASSETS_PATH}")
    print()
    
    # Inicializar el servicio
    avatar_service = AvatarService()
    
    # Obtener manifest completo
    print("1️⃣ Obteniendo manifest completo...")
    try:
        manifest = await avatar_service.get_assets_manifest()
        print(f"   ✅ Total de assets: {manifest['total_assets']}")
        print(f"   📂 Categorías encontradas: {list(manifest['categories'].keys())}")
        print()
        
        # Mostrar detalles por categoría
        for category, assets in manifest['categories'].items():
            print(f"📂 {category.upper()}:")
            print(f"   📊 Total: {len(assets)} assets")
            
            # Agrupar por género
            by_gender = {}
            for asset in assets:
                gender = asset['target_gender']
                if gender not in by_gender:
                    by_gender[gender] = []
                by_gender[gender].append(asset)
            
            for gender, gender_assets in by_gender.items():
                print(f"   👤 {gender}: {len(gender_assets)} assets")
                # Mostrar primeros 3 archivos como ejemplo
                for i, asset in enumerate(gender_assets[:3]):
                    filename = asset['filename'].split('/')[-1]  # Solo el nombre del archivo
                    print(f"      - {filename}")
                if len(gender_assets) > 3:
                    print(f"      ... y {len(gender_assets) - 3} más")
            print()
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Prueba específica para masculino
    print("2️⃣ Probando manifest filtrado por género (masculino)...")
    try:
        male_manifest = await avatar_service.get_assets_manifest(gender="male")
        print(f"   ✅ Assets para masculino: {male_manifest['total_assets']}")
        print(f"   📂 Categorías: {list(male_manifest['categories'].keys())}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Prueba específica para femenino
    print("3️⃣ Probando manifest filtrado por género (femenino)...")
    try:
        female_manifest = await avatar_service.get_assets_manifest(gender="female")
        print(f"   ✅ Assets para femenino: {female_manifest['total_assets']}")
        print(f"   📂 Categorías: {list(female_manifest['categories'].keys())}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Prueba de generación de avatar
    print("4️⃣ Probando generación de avatar básico...")
    try:
        # Crear un avatar básico con solo base y cabello
        test_layers = []
        
        # Agregar base masculina
        if 'base' in manifest['categories']:
            base_assets = [a for a in manifest['categories']['base'] if a['target_gender'] in ['male', 'unisex']]
            if base_assets:
                test_layers.append({
                    'category': 'base',
                    'file': base_assets[0]['filename']
                })
                print(f"   👤 Base seleccionada: {base_assets[0]['filename']}")
        
        # Agregar cabello si hay disponible
        if 'hair' in manifest['categories']:
            hair_assets = [a for a in manifest['categories']['hair'] if a['target_gender'] in ['male', 'unisex']]
            if hair_assets:
                test_layers.append({
                    'category': 'hair',
                    'file': hair_assets[0]['filename']
                })
                print(f"   💇 Cabello seleccionado: {hair_assets[0]['filename']}")
        
        if test_layers:
            result = await avatar_service.generate_avatar(
                base_gender="male",
                layers=test_layers
            )
            print(f"   ✅ Avatar generado exitosamente!")
            print(f"   📏 Tamaño de imagen: {len(result)} bytes")
        else:
            print(f"   ⚠️ No se encontraron assets suficientes para generar avatar")
        print()
            
    except Exception as e:
        print(f"   ❌ Error generando avatar: {e}")
    
    print("🎉 ¡Prueba de detección completada!")
    return True

if __name__ == "__main__":
    asyncio.run(test_asset_detection())