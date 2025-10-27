#!/usr/bin/env python3
"""
Script simplificado para crear estructura de assets iniciales.
No requiere dependencias del proyecto.
"""

import os
import json
from pathlib import Path
from PIL import Image, ImageDraw


def create_sample_avatar_assets():
    """Crea assets de muestra para el sistema de avatares."""
    print("Creando assets de muestra para avatares...")
    
    # Directorio base
    base_dir = Path("static/assets")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Categorías y sus assets
    categories = {
        'base': ['light_skin', 'medium_skin', 'dark_skin'],
        'hair': ['short_brown', 'long_blonde', 'curly_black', 'bald'],
        'eyes': ['brown_eyes', 'blue_eyes', 'green_eyes', 'hazel_eyes'],
        'clothes': ['casual_shirt', 'formal_suit', 'hoodie', 't_shirt'],
        'accessories': ['glasses', 'hat', 'earrings', 'necklace'],
        'backgrounds': ['office', 'outdoor', 'studio', 'home']
    }
    
    # Crear directorio y archivos para cada categoría
    created_files = []
    
    for category, items in categories.items():
        category_dir = base_dir / category
        category_dir.mkdir(exist_ok=True)
        
        for item in items:
            file_path = category_dir / f"{item}.png"
            
            # Crear imagen simple de placeholder
            create_placeholder_image(file_path, category, item)
            created_files.append(file_path)
            print(f"✅ {file_path}")
    
    # Crear manifest.json
    manifest_data = {}
    for category, items in categories.items():
        manifest_data[category] = []
        for item in items:
            manifest_data[category].append({
                "id": f"{category}_{item}",
                "name": item.replace('_', ' ').title(),
                "filename": f"{item}.png",
                "category": category,
                "z_index": get_z_index(category)
            })
    
    manifest_path = base_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {manifest_path}")
    print(f"\nCreados {len(created_files)} archivos de assets + manifest.json")
    
    return created_files


def create_placeholder_image(file_path, category, item):
    """Crea una imagen placeholder simple."""
    try:
        # Tamaño estándar para avatares
        size = (200, 200)
        
        # Colores por categoría
        colors = {
            'base': '#F4C2A1',      # Tono piel
            'hair': '#8B4513',      # Marrón
            'eyes': '#4169E1',      # Azul
            'clothes': '#2F4F4F',   # Gris oscuro
            'accessories': '#FFD700', # Dorado
            'backgrounds': '#87CEEB'  # Azul cielo
        }
        
        color = colors.get(category, '#CCCCCC')
        
        # Crear imagen
        img = Image.new('RGBA', size, (0, 0, 0, 0))  # Transparente
        draw = ImageDraw.Draw(img)
        
        # Dibujar forma simple según categoría
        if category == 'base':
            # Círculo para cara
            draw.ellipse([40, 40, 160, 160], fill=color)
        elif category == 'hair':
            # Rectángulo arriba
            draw.rectangle([50, 30, 150, 100], fill=color)
        elif category == 'eyes':
            # Dos círculos pequeños
            draw.ellipse([70, 80, 90, 100], fill=color)
            draw.ellipse([110, 80, 130, 100], fill=color)
        elif category == 'clothes':
            # Rectángulo para cuerpo
            draw.rectangle([60, 120, 140, 190], fill=color)
        elif category == 'accessories':
            # Pequeño rectángulo
            draw.rectangle([80, 60, 120, 80], fill=color)
        else:
            # Background - rectángulo completo
            draw.rectangle([0, 0, 200, 200], fill=color)
        
        # Guardar imagen
        img.save(file_path, 'PNG')
        
    except Exception as e:
        print(f"⚠️  Error creando {file_path}: {e}")
        # Crear archivo vacío como fallback
        file_path.touch()


def get_z_index(category):
    """Retorna el z-index para layering correcto."""
    z_indexes = {
        'backgrounds': 1,
        'base': 2,
        'clothes': 3,
        'hair': 4,
        'eyes': 5,
        'accessories': 6
    }
    return z_indexes.get(category, 10)


def create_readme():
    """Crea README para assets."""
    readme_content = """# Avatar Assets

Este directorio contiene los assets para el sistema de avatares de Acadify.

## Estructura

- `base/`: Tonos de piel base
- `hair/`: Estilos de cabello
- `eyes/`: Tipos de ojos
- `clothes/`: Vestimenta
- `accessories/`: Accesorios (lentes, sombreros, etc.)
- `backgrounds/`: Fondos

## Formato

- Todas las imágenes deben ser PNG con transparencia
- Tamaño recomendado: 200x200 píxeles
- El archivo `manifest.json` contiene metadatos de todos los assets

## Agregar nuevos assets

1. Agregar imagen PNG en la carpeta correspondiente
2. Actualizar `manifest.json` con nueva entrada
3. Ejecutar `python3 scripts/sync_assets.py` para sincronizar con la BD

## Generación automática

Este directorio fue generado automáticamente con assets de placeholder.
Reemplaza las imágenes con assets reales según sea necesario.
"""
    
    readme_path = Path("static/assets/README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ {readme_path}")


def main():
    """Función principal."""
    print("CREANDO ASSETS INICIALES PARA SISTEMA DE AVATARES")
    print("="*55)
    
    try:
        # Cambiar al directorio del backend
        os.chdir("/home/esteban/Acadify/backend")
        
        # Verificar si PIL está disponible
        try:
            from PIL import Image, ImageDraw
            print("✅ PIL disponible - creando imágenes placeholder")
            use_pil = True
        except ImportError:
            print("⚠️  PIL no disponible - creando archivos vacíos")
            use_pil = False
        
        # Crear assets
        if use_pil:
            created_files = create_sample_avatar_assets()
        else:
            created_files = create_simple_assets()
        
        # Crear README
        create_readme()
        
        print(f"\n🎉 ¡Assets iniciales creados exitosamente!")
        print(f"   Total archivos: {len(created_files)}")
        print(f"   Ubicación: static/assets/")
        print(f"\n📋 Próximos pasos:")
        print(f"   1. Reemplazar placeholders con imágenes reales")
        print(f"   2. Ejecutar: python3 scripts/sync_assets.py")
        print(f"   3. Probar sistema de avatares")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def create_simple_assets():
    """Crea archivos de assets simples sin PIL."""
    print("Creando estructura de assets sin imágenes...")
    
    base_dir = Path("static/assets")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    categories = {
        'base': ['light_skin', 'medium_skin', 'dark_skin'],
        'hair': ['short_brown', 'long_blonde', 'curly_black', 'bald'],
        'eyes': ['brown_eyes', 'blue_eyes', 'green_eyes', 'hazel_eyes'],
        'clothes': ['casual_shirt', 'formal_suit', 'hoodie', 't_shirt'],
        'accessories': ['glasses', 'hat', 'earrings', 'necklace'],
        'backgrounds': ['office', 'outdoor', 'studio', 'home']
    }
    
    created_files = []
    
    for category, items in categories.items():
        category_dir = base_dir / category
        category_dir.mkdir(exist_ok=True)
        
        for item in items:
            file_path = category_dir / f"{item}.png"
            file_path.touch()  # Crear archivo vacío
            created_files.append(file_path)
            print(f"✅ {file_path}")
    
    # Crear manifest.json
    manifest_data = {}
    for category, items in categories.items():
        manifest_data[category] = []
        for item in items:
            manifest_data[category].append({
                "id": f"{category}_{item}",
                "name": item.replace('_', ' ').title(),
                "filename": f"{item}.png",
                "category": category,
                "z_index": get_z_index(category)
            })
    
    manifest_path = base_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {manifest_path}")
    
    return created_files


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)