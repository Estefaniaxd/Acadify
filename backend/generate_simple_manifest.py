#!/usr/bin/env python3
"""
Servicio simplificado de avatars que lee directamente del filesystem
sin depender de la base de datos.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from PIL import Image

def scan_assets_directory(assets_path: str = "static/assets") -> Dict[str, Any]:
    """
    Escanea el directorio de assets y genera un manifest dinámico.
    """
    assets_dir = Path(assets_path)
    
    if not assets_dir.exists():
        print(f"❌ Assets directory not found: {assets_dir}")
        return {"categories": {}, "total_assets": 0, "resolution": [512, 512]}
    
    categories = {}
    total_assets = 0
    
    # Categorías esperadas
    expected_categories = [
        'base', 'hair', 'eyes', 'mouth', 'makeup', 
        'shirt', 'pants', 'shoes', 'jacket', 
        'accessories', 'backgrounds'
    ]
    
    for category in expected_categories:
        category_path = assets_dir / category
        
        if not category_path.exists():
            continue
            
        categories[category] = []
        
        # Buscar en subcarpetas de género
        for gender_path in category_path.iterdir():
            if not gender_path.is_dir():
                continue
                
            gender = gender_path.name  # male, female, unisex
            
            # Buscar archivos PNG
            for png_file in gender_path.glob("*.png"):
                try:
                    # Obtener información de la imagen
                    with Image.open(png_file) as img:
                        width, height = img.size
                    
                    file_size = png_file.stat().st_size
                    relative_path = png_file.relative_to(assets_dir)
                    
                    asset_info = {
                        "id": str(hash(str(relative_path))),  # Hash simple como ID
                        "filename": str(relative_path).replace("\\", "/"),  # Normalizar path
                        "display_name": png_file.stem.replace("_", " ").title(),
                        "target_gender": gender,
                        "width": width,
                        "height": height,
                        "file_size": file_size,
                        "is_normalized": (width == 512 and height == 512),
                        "meta_info": {},
                        "url": f"/static/assets/{relative_path}".replace("\\", "/")
                    }
                    
                    categories[category].append(asset_info)
                    total_assets += 1
                    
                except Exception as e:
                    print(f"⚠️ Error processing {png_file}: {e}")
    
    manifest = {
        "resolution": [512, 512],
        "categories": categories,
        "total_assets": total_assets
    }
    
    return manifest

def filter_manifest_by_gender(manifest: Dict[str, Any], gender: str) -> Dict[str, Any]:
    """
    Filtra el manifest por género.
    """
    filtered_categories = {}
    total_filtered = 0
    
    for category, assets in manifest["categories"].items():
        filtered_assets = []
        
        for asset in assets:
            asset_gender = asset["target_gender"]
            
            # Para la categoría base, solo mostrar específicos del género seleccionado
            if category == 'base':
                if asset_gender == gender:
                    filtered_assets.append(asset)
                    total_filtered += 1
            else:
                # Para otras categorías, mostrar específicos del género + unisex
                if asset_gender == gender or asset_gender == 'unisex':
                    filtered_assets.append(asset)
                    total_filtered += 1
        
        if filtered_assets:
            filtered_categories[category] = filtered_assets
    
    return {
        "resolution": manifest["resolution"],
        "categories": filtered_categories,
        "total_assets": total_filtered,
        "gender": gender
    }

if __name__ == "__main__":
    print("🔍 Escaneando assets...")
    manifest = scan_assets_directory()
    
    print(f"📂 Categorías encontradas: {len(manifest['categories'])}")
    print(f"📄 Total de assets: {manifest['total_assets']}")
    
    for category, assets in manifest["categories"].items():
        print(f"  {category}: {len(assets)} assets")
    
    # Guardar manifest completo
    with open("static/assets/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    # Generar manifests filtrados por género
    for gender in ["male", "female"]:
        filtered = filter_manifest_by_gender(manifest, gender)
        with open(f"static/assets/manifest_{gender}.json", "w", encoding="utf-8") as f:
            json.dump(filtered, f, indent=2, ensure_ascii=False)
        
        print(f"👤 {gender}: {filtered['total_assets']} assets disponibles")
    
    print("✅ Manifests generados correctamente!")